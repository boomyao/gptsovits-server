from typing import Tuple
import torch
from .chinese.normalizer import ChineseTextNormalizer
from .chinese.phoneme_converter import ChinesePhonemeConverter
from .normalizer import EmptyTextNormalizer

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
        return normalized_text, phonemes, bert_features

class LanguageProcessorFactory:
    _processor_cache = {}

    @staticmethod
    def get_processor(language: str) -> LanguageProcessor:
        if language not in LanguageProcessorFactory._processor_cache:
            LanguageProcessorFactory._processor_cache[language] = LanguageProcessor(language)
        return LanguageProcessorFactory._processor_cache[language]


# class PhonemeConverter:
#     def __init__(self, language):
#         self.language = language
#         self.language_module_map = {
#             "zh": "ChinesePhoneme",
#             "ja": "JapanesePhoneme",
#             "en": "EnglishPhoneme",
#             "ko": "KoreanPhoneme",
#             "yue": "CantonesePhoneme"
#         }
#         self.symbols = symbols_v2.symbols
#         self.language_module = self._load_language_module()

#     def _load_language_module(self):
#         if self.language not in self.language_module_map:
#             self.language = "en"
#         return __import__("text." + self.language_module_map[self.language], fromlist=[self.language_module_map[self.language]])

#     def normalize_text(self, text):
#         if hasattr(self.language_module, "text_normalize"):
#             return self.language_module.text_normalize(text)
#         return text

#     def text_to_phonemes(self, text):
#         phonemes = self.language_module.g2p(text)
#         if self.language in ["zh", "yue"]:
#             word_to_phoneme = self.language_module.g2p(text)[1]
#             assert len(phonemes[0]) == sum(word_to_phoneme)
#             assert len(text) == len(word_to_phoneme)
#         else:
#             word_to_phoneme = None
#             if self.language == "en" and len(phonemes) < 4:
#                 phonemes = [','] + phonemes
#         return phonemes, word_to_phoneme


# class SpecialSymbolHandler:
#     def __init__(self, special_mappings, symbols):
#         self.special_mappings = special_mappings
#         self.symbols = symbols

#     def handle_special_symbols(self, text, phoneme_converter):
#         for symbol, language, replacement in self.special_mappings:
#             if symbol in text and phoneme_converter.language == language:
#                 return self._replace_and_convert(text, phoneme_converter, symbol, replacement)
#         return None

#     def _replace_and_convert(self, text, phoneme_converter, symbol, replacement):
#         text = text.replace(symbol, ",")
#         normalized_text = phoneme_converter.normalize_text(text)
#         phonemes, word_to_phoneme = phoneme_converter.text_to_phonemes(normalized_text)
#         processed_phonemes = [
#             replacement if phoneme == "," else phoneme for phoneme in phonemes[0]
#         ]
#         return processed_phonemes, word_to_phoneme, normalized_text


# def convert_text_to_phonemes(text, language, special_mappings):
#     phoneme_converter = PhonemeConverter(language)
#     special_handler = SpecialSymbolHandler(special_mappings, phoneme_converter.symbols)
    
#     special_result = special_handler.handle_special_symbols(text, phoneme_converter)
#     if special_result:
#         return special_result
    
#     normalized_text = phoneme_converter.normalize_text(text)
#     phonemes, word_to_phoneme = phoneme_converter.text_to_phonemes(normalized_text)
    
#     phonemes = ['UNK' if phoneme not in phoneme_converter.symbols else phoneme for phoneme in phonemes[0]]
    
#     return phonemes, word_to_phoneme, normalized_text
