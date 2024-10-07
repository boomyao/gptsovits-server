import re
from g2p_en import G2p
from gptsovits.text.symbols import get_symbols
from gptsovits.text.phoneme_converter import PhonemeConverter
from jamo import h2j, j2hcj

_hangul_divided = [(re.compile('%s' % x[0]), x[1]) for x in [
    ('ㅘ', 'ㅗㅏ'),
    ('ㅙ', 'ㅗㅐ'),
    ('ㅚ', 'ㅗㅣ'),
    ('ㅝ', 'ㅜㅓ'),
    ('ㅞ', 'ㅜㅔ'),
    ('ㅟ', 'ㅜㅣ'),
    ('ㅢ', 'ㅡㅣ'),
    ('ㅑ', 'ㅣㅏ'),
    ('ㅒ', 'ㅣㅐ'),
    ('ㅕ', 'ㅣㅓ'),
    ('ㅖ', 'ㅣㅔ'),
    ('ㅛ', 'ㅣㅗ'),
    ('ㅠ', 'ㅣㅜ')
]]

_latin_to_hangul = [(re.compile('%s' % x[0], re.IGNORECASE), x[1]) for x in [
    ('a', '에이'),
    ('b', '비'),
    ('c', '시'),
    ('d', '디'),
    ('e', '이'),
    ('f', '에프'),
    ('g', '지'),
    ('h', '에이치'),
    ('i', '아이'),
    ('j', '제이'),
    ('k', '케이'),
    ('l', '엘'),
    ('m', '엠'),
    ('n', '엔'),
    ('o', '오'),
    ('p', '피'),
    ('q', '큐'),
    ('r', '아르'),
    ('s', '에스'),
    ('t', '티'),
    ('u', '유'),
    ('v', '브이'),
    ('w', '더블유'),
    ('x', '엑스'),
    ('y', '와이'),
    ('z', '제트')
]]

class KoreanPhonemeConverter(PhonemeConverter):
    def __init__(self):
        self.g2p_model = G2p()

    def convert_to_phonemes(self, text: str):
        text = self.latin_to_hangul(text)
        text = self.g2p_model(text)
        text = self.divide_hangul(text)
        text = self.fix_g2pk2_error(text)
        text = re.sub(r'([\u3131-\u3163])$', r'\1.', text)
        phonemes = [self.post_replace_ph(i) for i in text]
        return phonemes, []

    def latin_to_hangul(self, text: str):
        for regex, replacement in _latin_to_hangul:
            text = re.sub(regex, replacement, text)
        return text

    def divide_hangul(self, text: str):
        text = j2hcj(h2j(text))
        for regex, replacement in _hangul_divided:
            text = re.sub(regex, replacement, text)
        return text

    def fix_g2pk2_error(self, text: str):
        new_text = ""
        i = 0
        while i < len(text) - 4:
            if (text[i:i+3] == 'ㅇㅡㄹ' or text[i:i+3] == 'ㄹㅡㄹ') and text[i+3] == ' ' and text[i+4] == 'ㄹ':
                new_text += text[i:i+3] + ' ' + 'ㄴ'
                i += 5
            else:
                new_text += text[i]
                i += 1

        new_text += text[i:]
        return new_text

    def post_replace_ph(self, text: str):
        symbols = get_symbols()
        rep_map = {
            "：": ",",
            "；": ",",
            "，": ",",
            "。": ".",
            "！": "!",
            "？": "?",
            "\n": ".",
            "·": ",",
            "、": ",",
            "...": "…",
            " ": "空",
        }
        if ph in rep_map.keys():
            ph = rep_map[ph]
        if ph in symbols:
            return ph
        if ph not in symbols:
            ph = "停"
        return ph