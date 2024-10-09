from typing import Tuple
import torch
import logging

from gptsovits.text.korean.phoneme_converter import KoreanPhonemeConverter
from .chinese.normalizer import ChineseTextNormalizer
from .chinese.phoneme_converter import ChinesePhonemeConverter
from .english.phoneme_converter import EnglishPhonemeConverter
from .english.normalizer import EnglishTextNormalizer
from .normalizer import EmptyTextNormalizer
from .symbols import get_symbols_dict

logger = logging.getLogger(__name__)

class LanguageProcessor:
    def __init__(self, language: str):
        if language == "zh":
            self.phoneme_converter = ChinesePhonemeConverter()
            self.text_normalizer = ChineseTextNormalizer()
        elif language == "en":
            self.phoneme_converter = EnglishPhonemeConverter()
            self.text_normalizer = EnglishTextNormalizer()
        elif language == "ja":
            self.phoneme_converter = JapanesePhonemeConverter()
            self.text_normalizer = EmptyTextNormalizer()
        elif language == "ko":
            self.phoneme_converter = KoreanPhonemeConverter()
            self.text_normalizer = EmptyTextNormalizer()
        elif language == "yue":
            self.phoneme_converter = CantonesePhonemeConverter()
            self.text_normalizer = ChineseTextNormalizer()
        else:
            raise ValueError(f"Unsupported language: {language}")

    def process(self, text: str) -> Tuple[str, list[str], torch.Tensor]:
        normalized_text = self.text_normalizer.normalize_text(text)
        logger.debug('normalized_text: %s', normalized_text)
        phonemes, phoneme_lengths = self.phoneme_converter.convert_to_phonemes(normalized_text)
        bert_features = self.phoneme_converter.get_bert_features(normalized_text, phonemes, phoneme_lengths)
        symbols_dict = get_symbols_dict()
        phonemes = [symbols_dict[phoneme] for phoneme in phonemes]
        return normalized_text, phonemes, bert_features
    
    def phonemes_to_seq(self, phonemes: list[str]) -> list[int]:
        rep_map = {"'": "-"}
        symbols_dict = get_symbols_dict()
        seq = []
        for phoneme in phonemes:
            if phoneme in symbols_dict:
                seq.append(symbols_dict[phoneme])
            elif phoneme in rep_map:
                seq.append(symbols_dict[rep_map[phoneme]])
            else:
                print(f"Warning: '{phoneme}' not found in symbols_dict")
        return seq

class LanguageProcessorFactory:
    _processor_cache = {}

    @staticmethod
    def get_processor(language: str) -> LanguageProcessor:
        if language not in LanguageProcessorFactory._processor_cache:
            LanguageProcessorFactory._processor_cache[language] = LanguageProcessor(language)
        return LanguageProcessorFactory._processor_cache[language]
