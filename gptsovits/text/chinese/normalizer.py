import re
from gptsovits.text.normalizer import TextNormalizer
from gptsovits.text.constants import PUNCTUATION, PUNCTUATION_REP_MAP
from .zh_normalization.text_normlization import TextNormalizer as ZHTextNormalizer

class ChineseTextNormalizer(TextNormalizer):
    def normalize_text(self, text: str) -> str:
      tx = ZHTextNormalizer()
      sentences = tx.normalize(text)
      dest_text = ""
      for sentence in sentences:
          dest_text += self._replace_punctuation(sentence)

      # 避免重复标点引起的参考泄露
      dest_text = self._replace_consecutive_punctuation(dest_text)
      return dest_text
    
    def _replace_punctuation(self, text):
      text = text.replace("嗯", "恩").replace("呣", "母")
      pattern = re.compile("|".join(re.escape(p) for p in PUNCTUATION_REP_MAP.keys()))

      replaced_text = pattern.sub(lambda x: PUNCTUATION_REP_MAP[x.group()], text)

      replaced_text = re.sub(
          r"[^\u4e00-\u9fa5" + "".join(PUNCTUATION) + r"]+", "", replaced_text
      )

      return replaced_text
    
    def _replace_consecutive_punctuation(self, text):
      punctuations = ''.join(re.escape(p) for p in PUNCTUATION)
      pattern = f'([{punctuations}])([{punctuations}])+'
      result = re.sub(pattern, r'\1', text)
      return result