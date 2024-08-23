from typing import List
from gptsovits.text.text_service import TextService
from gptsovits.speech.speech_service import SpeechService
import torch

class GPTSovitsFrontend:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.text_service = TextService(device=self.device, dtype=self.dtype)
        self.speech_service = SpeechService(device=self.device, dtype=self.dtype)

    def zero_shot(self, text: str, ref_audio, ref_prompt = None, speed = 1):
        texts = self.text_service.split_paragraph(text)
        text_inputs = self.text_service.process_text_batch(texts)
        ref_prompt_input = self.text_service.process_text(ref_prompt) if ref_prompt else None
        ref_features, ref_mel_specs = self.speech_service.process_audio(ref_audio)
        
        for text_input in text_inputs:
            bert_features = text_input[2] if not ref_prompt_input else torch.cat([ref_prompt_input[2], text_input[2]], 1)
            bert_features = bert_features.to(self.device).unsqueeze(0)
            all_phoneme_ids = text_input[1] if not ref_prompt_input else ref_prompt_input[1] + text_input[1]
            all_phoneme_ids = torch.LongTensor(all_phoneme_ids).to(self.device).unsqueeze(0)
            all_phoneme_len = torch.tensor([all_phoneme_ids.shape[-1]]).to(self.device)
            yield {
                "text": text_input[0],
                "bert_features": bert_features,
                "phoneme": torch.LongTensor(text_input[1]).to(self.device).unsqueeze(0),
                "all_phoneme_ids": all_phoneme_ids,
                "all_phoneme_len": all_phoneme_len,
                "ref_features": ref_features,
                "ref_mel_specs": ref_mel_specs,
                "speed": speed,
            }

    def _extract_text_tokens(self, text: str) -> List[str]:
        return text.split()

def preprocess_text(text, language):
    """Preprocess the text based on the language."""
    if language == "en":
        LangSegment.setfilters(["en"])
        return " ".join(tmp["text"] for tmp in LangSegment.getTexts(text))
    return text

def normalize_text(text):
    """Normalize text by converting lowercase letters to uppercase and applying Chinese-specific normalization."""
    if re.search(r'[A-Za-z]', text):
        text = re.sub(r'[a-z]', lambda x: x.group(0).upper(), text)
        return chinese.mix_text_normalize(text)
    return text

def process_single_language(text, language, version):
    """Process text for a single language."""
    phones, word2ph, norm_text = clean_text_inf(text, language, version)
    if language == "zh":
        bert = get_bert_feature(norm_text, word2ph).to(device)
    else:
        bert = torch.zeros(
            (1024, len(phones)),
            dtype=torch.float16 if is_half else torch.float32
        ).to(device)
    return phones, bert, norm_text

def process_multiple_languages(text, language, version):
    """Process text that contains multiple languages."""
    LangSegment.setfilters(["zh", "ja", "en", "ko"])
    textlist, langlist = [], []

    for tmp in LangSegment.getTexts(text):
        if language == "auto":
            langlist.append(tmp["lang"])
        elif language == "auto_yue" and tmp["lang"] == "zh":
            langlist.append("yue")
        else:
            langlist.append(language if tmp["lang"] != "en" else "en")
        textlist.append(tmp["text"])

    phones_list, bert_list, norm_text_list = [], [], []
    for i, lang in enumerate(langlist):
        phones, word2ph, norm_text = clean_text_inf(textlist[i], lang, version)
        bert = get_bert_inf(phones, word2ph, norm_text, lang)
        phones_list.append(phones)
        norm_text_list.append(norm_text)
        bert_list.append(bert)

    return sum(phones_list, []), torch.cat(bert_list, dim=1), ''.join(norm_text_list)

def get_phones_and_bert(text, language, version, final=False):
    """Main function to get phones and BERT features."""
    language = language.replace("all_", "")
    formattext = preprocess_text(text, language)

    if language in {"en", "zh", "ja", "ko", "yue"}:
        formattext = normalize_text(formattext, language)
        if language in {"zh", "yue"} and not re.search(r'[A-Za-z]', formattext):
            return process_single_language(formattext, language, version)
    elif language in {"auto", "auto_yue"}:
        phones, bert, norm_text = process_multiple_languages(formattext, language, version)
    else:
        phones, bert, norm_text = process_single_language(formattext, language, version)

    if not final and len(phones) < 6:
        return get_phones_and_bert("." + text, language, version, final=True)

    return phones, bert.to(dtype), norm_text