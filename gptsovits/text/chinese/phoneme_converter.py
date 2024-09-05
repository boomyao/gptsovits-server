import re, os, json
import torch
from gptsovits.text.phoneme_converter import PhonemeConverter
from gptsovits.text.constants import PUNCTUATION
from transformers import AutoModelForMaskedLM, AutoTokenizer
import jieba_fast.posseg as psg
from pypinyin import Style, lazy_pinyin
from pypinyin.contrib.tone_convert import to_initials, to_finals_tone3
from .tone_sandhi import ToneSandhi

current_file_path = os.path.dirname(__file__)
pinyin_to_symbol_map = {
    line.split("\t")[0]: line.strip().split("\t")[1]
    for line in open(os.path.join(current_file_path, "opencpop-strict.txt")).readlines()
}

class ChinesePhonemeConverter(PhonemeConverter):
    def __init__(self):
        super().__init__()
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.device = PhonemeConverter.device
        self.dtype = PhonemeConverter.dtype
        bert_model_path = 'pretrained_models/chinese-roberta-wwm-ext-large'
        self.tokenizer = AutoTokenizer.from_pretrained(bert_model_path)
        self.bert_model = AutoModelForMaskedLM.from_pretrained(bert_model_path)
        self.tone_modifier = ToneSandhi()

        if self.dtype == torch.float16:
            self.bert_model = self.bert_model.half().to(self.device)
        else:
            self.bert_model = self.bert_model.to(self.device)

        self._loadErhuaDict()
    
    def convert_to_phonemes(self, text: str):
        initials, finals = self._convert_to_initials_finals(text)
        phones_list = self._process_phonemes(initials, finals, text)
        phoneme_lengths = self._process_phoneme_lengths(initials, finals)
        return phones_list, phoneme_lengths
    
    def get_bert_features(self, text: str, phonemes: list[str], phoneme_lengths: list[int]):
        with torch.no_grad():
            inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
            res = self.bert_model(**inputs, output_hidden_states=True)
            hidden_states = torch.cat(res["hidden_states"][-3:-2], -1)[0].cpu()[1:-1]
        
        assert len(phoneme_lengths) == len(text)
        phone_level_feature = [
            hidden_states[i].repeat(length, 1) for i, length in enumerate(phoneme_lengths)
        ]
        return torch.cat(phone_level_feature, dim=0).T.to(self.device)
    
    def _loadErhuaDict(self):
        config_file_path = os.path.join(self.base_path, "erhua.json")
        with open(config_file_path, 'r', encoding='utf-8') as f:
            erhua_config = json.load(f)

        self.must_erhua = set(erhua_config["must_erhua"])
        self.not_erhua = set(erhua_config["not_erhua"])
    
    def _convert_to_initials_finals(self, text: str):
        sentences = [i.strip() for i in re.split(r"(?<=[{0}])\s*".format("".join(PUNCTUATION)), text) if i.strip()]
        use_g2pw = self._initialize_g2pw()

        initials_list, finals_list = [], []
        for seg in sentences:
            seg_cut = self._clean_and_segment_text(seg)
            initials, finals = self._convert_to_pinyin(seg_cut, use_g2pw)
            initials_list.extend(initials)
            finals_list.extend(finals)

        return initials_list, finals_list
    
    def _initialize_g2pw(self):
        try:
            from text.g2pw import G2PWPinyin, correct_pronunciation
            self.g2pw = G2PWPinyin()
            self.correct_pronunciation = correct_pronunciation
            return True
        except ImportError:
            print("g2pw 加载失败，降级到 pypinyin")
            return False
    
    def _clean_and_segment_text(self, seg: str):
        seg = re.sub("[a-zA-Z]+", "", seg)
        seg_cut = psg.lcut(seg)
        return self.tone_modifier.pre_merge_for_modify(seg_cut)
    
    def _convert_to_pinyin(self, seg_cut, use_g2pw):
        if use_g2pw:
            return self._convert_using_g2pw(seg_cut)
        else:
            return self._convert_using_pypinyin(seg_cut)
    
    def _convert_using_g2pw(self, seg_cut):
        initials, finals = [], []
        pinyins = self.g2pw.lazy_pinyin(seg_cut, neutral_tone_with_five=True, style=Style.TONE3)
        pre_word_length = 0

        for word, pos in seg_cut:
            if pos == 'eng':
                pre_word_length += len(word)
                continue

            word_pinyins = self.correct_pronunciation(word, pinyins[pre_word_length:pre_word_length + len(word)])
            sub_initials, sub_finals = self._extract_initials_finals(word_pinyins)
            pre_word_length += len(word)

            sub_finals = self.tone_modifier.modified_tone(word, pos, sub_finals)
            sub_initials, sub_finals = self._merge_erhua(sub_initials, sub_finals, word, pos)

            initials.extend(sub_initials)
            finals.extend(sub_finals)

        return initials, finals
    
    def _convert_using_pypinyin(self, seg_cut):
        initials, finals = [], []

        for word, pos in seg_cut:
            if pos == "eng":
                continue
            sub_initials, sub_finals = self._extract_initials_finals_word(word)
            sub_finals = self.tone_modifier.modified_tone(word, pos, sub_finals)
            sub_initials, sub_finals = self._merge_erhua(sub_initials, sub_finals, word, pos)

            initials.extend(sub_initials)
            finals.extend(sub_finals)

        return initials, finals
    
    def _extract_initials_finals_word(self, word):
        initials = []
        finals = []

        orig_initials = lazy_pinyin(word, neutral_tone_with_five=True, style=Style.INITIALS)
        orig_finals = lazy_pinyin(
            word, neutral_tone_with_five=True, style=Style.FINALS_TONE3
        )

        for c, v in zip(orig_initials, orig_finals):
            initials.append(c)
            finals.append(v)
        return initials, finals
    
    def _extract_initials_finals(self, word_pinyins):
        sub_initials, sub_finals = [], []
        for pinyin in word_pinyins:
            if pinyin[0].isalpha():
                sub_initials.append(to_initials(pinyin))
                sub_finals.append(to_finals_tone3(pinyin, neutral_tone_with_five=True))
            else:
                sub_initials.append(pinyin)
                sub_finals.append(pinyin)
        return sub_initials, sub_finals
    
    def _merge_erhua(self, initials: list[str], finals: list[str], word: str, pos: str):
        for i, phn in enumerate(finals):
            if i == len(finals) - 1 and word[i] == "儿" and phn == 'er1':
                finals[i] = 'er2'

        if word not in self.must_erhua and (word in self.not_erhua or pos in {"a", "j", "nr"}):
            return initials, finals

        if len(finals) != len(word):
            return initials, finals

        new_initials, new_finals = [], []
        for i, phn in enumerate(finals):
            if i == len(finals) - 1 and word[i] == "儿" and phn in {"er2", "er5"} and word[-2:] not in self.not_erhua:
                phn = "er" + new_finals[-1][-1]

            new_initials.append(initials[i])
            new_finals.append(phn)

        return new_initials, new_finals
    
    def _process_phonemes(self, initials, finals, seg):
        phones_list = []
        for c, v in zip(initials, finals):
            phone = self._map_pinyin_to_phone(c, v, seg)
            phones_list.extend(phone)
        return phones_list
    
    def _map_pinyin_to_phone(self, c, v, seg):
        if c == v:
            assert c in PUNCTUATION
            return [c]
        else:
            v_without_tone = v[:-1]
            tone = v[-1]
            assert tone in "12345"
            pinyin = self._normalize_pinyin(c, v_without_tone)

            assert pinyin in pinyin_to_symbol_map.keys(), (pinyin, seg, c + v)
            new_c, new_v = pinyin_to_symbol_map[pinyin].split(" ")
            new_v += tone
            return [new_c, new_v]
    
    def _normalize_pinyin(self, c, v_without_tone):
        if c:
            v_rep_map = {"uei": "ui", "iou": "iu", "uen": "un"}
            return c + v_rep_map.get(v_without_tone, v_without_tone)
        else:
            pinyin = c + v_without_tone
            pinyin_rep_map = { "ing": "ying", "i": "yi", "in": "yin", "u": "wu" }
            if pinyin in pinyin_rep_map.keys():
                pinyin = pinyin_rep_map[pinyin]
            else:
                single_rep_map = { "v": "yu", "e": "e", "i": "y", "u": "w" }
                if pinyin[0] in single_rep_map.keys():
                    pinyin = single_rep_map[pinyin[0]] + pinyin[1:]
            return pinyin
    
    def _process_phoneme_lengths(self, initials, finals):
        return [1 if c == v else 2 for c, v in zip(initials, finals)]