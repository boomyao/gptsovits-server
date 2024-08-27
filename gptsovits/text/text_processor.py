from typing import Tuple
import torch
from .chinese.normalizer import ChineseTextNormalizer
from .chinese.phoneme_converter import ChinesePhonemeConverter
from .normalizer import EmptyTextNormalizer
from .symbols import get_symbols_dict

class LanguageProcessor:
    def __init__(self, language: str):
        if language == "chinese":
            self.phoneme_converter = ChinesePhonemeConverter()
            self.text_normalizer = ChineseTextNormalizer()
        elif language == "english":
            self.phoneme_converter = EnglishPhonemeConverter()
            self.text_normalizer = EnglishTextNormalizer()
        elif language == "japanese":
            self.phoneme_converter = JapanesePhonemeConverter()
            self.text_normalizer = EmptyTextNormalizer()
        elif language == "korean":
            self.phoneme_converter = KoreanPhonemeConverter()
            self.text_normalizer = EmptyTextNormalizer()
        elif language == "cantonese":
            self.phoneme_converter = CantonesePhonemeConverter()
            self.text_normalizer = ChineseTextNormalizer()
        else:
            raise ValueError(f"Unsupported language: {language}")


    def process(self, text: str) -> Tuple[str, list[str], torch.Tensor]:
        normalized_text = self.text_normalizer.normalize_text(text)
        phonemes, phoneme_lengths = self.phoneme_converter.convert_to_phonemes(normalized_text)
        bert_features = self.phoneme_converter.get_bert_features(normalized_text, phonemes, phoneme_lengths)
        symbols_dict = get_symbols_dict()
        phonemes = [symbols_dict[phoneme] for phoneme in phonemes]
        return normalized_text, phonemes, bert_features

class LanguageProcessorFactory:
    _processor_cache = {}

    @staticmethod
    def get_processor(language: str) -> LanguageProcessor:
        if language not in LanguageProcessorFactory._processor_cache:
            LanguageProcessorFactory._processor_cache[language] = LanguageProcessor(language)
        return LanguageProcessorFactory._processor_cache[language]
