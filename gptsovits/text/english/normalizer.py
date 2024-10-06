import re
from gptsovits.text.normalizer import TextNormalizer
from gptsovits.text.constants import PUNCTUATION
from g2p_en.expand import normalize_numbers
import unicodedata
from builtins import str as unicode

def replace_consecutive_punctuation(text):
    punctuations = ''.join(re.escape(p) for p in PUNCTUATION)
    return re.sub(f'([{punctuations}])([{punctuations}])+', r'\1', text)

class EnglishTextNormalizer(TextNormalizer):
    def normalize_text(self, text: str) -> str:

        rep_map = {
            "[;:：，；]": ",",
            '["’]': "'",
            "。": ".",
            "！": "!",
            "？": "?",
        }
        for p, r in rep_map.items():
            text = re.sub(p, r, text)
        
        text = normalize_numbers(unicode(text))
        text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
        text = re.sub("[^ A-Za-z'.,?!\-]", "", text)
        text = re.sub(r"(?i)i\.e\.", "that is", text)
        text = re.sub(r"(?i)e\.g\.", "for example", text)
        return replace_consecutive_punctuation(text)
        