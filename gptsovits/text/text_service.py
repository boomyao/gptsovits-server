from typing import List
import logging
import re
import torch
from .text_processor import LanguageProcessorFactory
from .phoneme_converter import PhonemeConverter
import LangSegment

logger = logging.getLogger(__name__)

class TextService:
  def __init__(self, device='cuda', dtype=torch.float32):
    self.device = device
    self.dtype = dtype

    PhonemeConverter.set_device(device)
    PhonemeConverter.set_dtype(dtype)

    LangSegment.setfilters(["zh","ja","en","ko"])

  def process_text(self, text: str, language = None):
    # preprocess number in chinese text
    if re.search(r'[\u4e00-\u9fff]', text):
      from .chinese.zh_normalization.text_normlization import TextNormalizer
      text = TextNormalizer().normalize_sentence(text)

    segments = []
    for item in LangSegment.getTexts(text):
      segments.append(item)

    logger.debug(segments)

    results = []
    for segment in segments:
       processor = LanguageProcessorFactory.get_processor(segment['lang'])
       results.append(processor.process(segment['text']))

    normalized_text = ''.join([result[0] for result in results])
    phonemes = sum([result[1] for result in results], [])
    bert_features = torch.cat([result[2] for result in results], dim=1)
       
    return normalized_text, phonemes, bert_features
  
  def process_text_batch(self, texts: List[str], language = None):
    return [self.process_text(text, language) for text in texts]
  
  def split_paragraph(self, text, threshold=5, group_size=4):
    splits = {"，", "。", "？", "！", ",", ".", "?", "!", "~", ":", "：", "—", "…"}
    punctuation = set(['!', '?', '…', ',', '.', '-', " "])
    
    # Normalize input text
    text = text.replace("……", "。").replace("——", "，").strip("\n")
    if not text or text in [" ", "\n"]:
        raise ValueError("Input text is empty or invalid")
    
    if text[-1] not in splits:
        text += "。"
    
    # Split text based on delimiters
    segments = []
    start = 0
    for i, char in enumerate(text):
        if char in splits:
            segments.append(text[start:i+1])
            start = i + 1
    
    # Group segments by specified group size
    grouped_segments = ["".join(segments[i:i+group_size]) for i in range(0, len(segments), group_size)]
    
    # Combine small segments within each group
    combined_segments = []
    for group in grouped_segments:
        if len(group) < threshold:
            if combined_segments:
                combined_segments[-1] += group
            else:
                combined_segments.append(group)
        else:
            combined_segments.append(group)
    
    # Remove segments that only contain punctuation
    result = [seg for seg in combined_segments if not set(seg).issubset(punctuation)]
    
    return result