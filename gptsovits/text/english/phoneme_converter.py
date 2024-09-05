import os, re
from wordsegment import load as wordsegment_load, segment as word_segment
from nltk.tokenize import TweetTokenizer
from nltk import pos_tag
import nltk
from g2p_en import G2p
from gptsovits.text.constants import PUNCTUATION
from gptsovits.text.symbols import get_symbols
from gptsovits.text.phoneme_converter import PhonemeConverter
from gptsovits.utils.pickle_utils import load_pickle, save_pickle

nltk.data.path.append(os.environ.get("NLTK_DATA", "/home/nltk_data"))

class EnglishPhonemeConverter(PhonemeConverter):
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.g2p_model = G2p()
        wordsegment_load()
        self.cmu = self._load_cmu_dict()
        self.namedict = self._load_namedict()
        self._remove_invalid_entries()
        self._add_homograph_corrections()

        nltk.download('averaged_perceptron_tagger_eng')

    def convert_to_phonemes(self, text: str):
        words = TweetTokenizer().tokenize(text)
        tokens = pos_tag(words)
        prons = [pron for o_word, pos in tokens for pron in self._get_pronunciation(o_word, pos)]

        phonemes = self._process_phonemes(prons, get_symbols())
        return phonemes, []

    def _load_cmu_dict(self):
        cmu_dict = {}
        cmu_dict_path = os.path.join(self.base_path, 'cmudict.rep')
        cmu_fast_path = os.path.join(self.base_path, 'cmudict-fast.rep')
        cmu_hot_path = os.path.join(self.base_path, 'engdict-hot.rep')
        cache_path = os.path.join(self.base_path, 'engdict_cache.pickle')

        # Load or generate the CMU dictionary cache
        cmu_dict = load_pickle(cache_path)
        if cmu_dict is None:
            cmu_dict = self._read_cmu_dict(cmu_dict_path)
            cmu_dict.update(self._read_cmu_dict(cmu_fast_path, start_line=0))
            save_pickle(cmu_dict, cache_path)

        # Load the hot dictionary
        hot_dict = self._read_cmu_dict(cmu_hot_path, start_line=0)
        cmu_dict.update(hot_dict)

        return cmu_dict

    def _read_cmu_dict(self, file_path, start_line=57):
        cmu_dict = {}
        with open(file_path) as f:
            lines = f.readlines()[start_line:]
            for line in lines:
                word, phonemes = line.strip().split(" ", 1)
                cmu_dict[word.lower()] = [phonemes.split()]
        return cmu_dict

    def _load_namedict(self):
        name_dict_path = os.path.join(self.base_path, 'namedict_cache.pickle')
        return load_pickle(name_dict_path, default={})

    def _remove_invalid_entries(self):
        for word in ["AE", "AI", "AR", "IOS", "HUD", "OS"]:
            self.cmu.pop(word.lower(), None)

    def _add_homograph_corrections(self):
        self.g2p_model.homograph2features.update({
            "read": (['R', 'IY1', 'D'], ['R', 'EH1', 'D'], 'VBP'),
            "complex": (['K', 'AH0', 'M', 'P', 'L', 'EH1', 'K', 'S'], ['K', 'AA1', 'M', 'P', 'L', 'EH0', 'K', 'S'], 'JJ')
        })

    def _get_pronunciation(self, o_word, pos):
        word = o_word.lower()

        if not re.search("[a-z]", word):
            return [word]
        if len(word) == 1:
            return ['EY1'] if o_word == "A" else self.cmu.get(word, [["UNK"]])[0]
        if word in self.g2p_model.homograph2features:
            return self._resolve_homograph(word, pos)
        if word in self.cmu:
            return self.cmu[word][0]
        if o_word.istitle() and word in self.namedict:
            return self.namedict[word][0]
        if len(word) <= 3:
            return [phone for w in word for phone in self.cmu.get(w, [["UNK"]])[0]]
        if re.match(r"^([a-z]+)('s)$", word):
            return self._handle_possessive(word[:-2], word[-2:])

        return [phone for comp in word_segment(word) for phone in self._get_pronunciation(comp, pos)]

    def _resolve_homograph(self, word, pos):
        pron1, pron2, pos1 = self.g2p_model.homograph2features[word]
        return pron1 if pos.startswith(pos1) else pron2

    def _handle_possessive(self, root_word):
        phones = self._get_pronunciation(root_word, None)
        if phones[-1] in ['P', 'T', 'K', 'F', 'TH', 'HH']:
            return phones + ['S']
        elif phones[-1] in ['S', 'Z', 'SH', 'ZH', 'CH', 'JH']:
            return phones + ['AH0', 'Z']
        else:
            return phones + ['Z']
        
    def _process_phonemes(self, prons, symbols):
      rep_map = {"'": "-"}
      return [
          rep_map.get(ph, ph) if ph in symbols else ("UNK" if ph == "<unk>" else ph)
          for ph in prons if ph not in [" ", "<pad>", "UW", "</s>", "<s>"]
      ]
