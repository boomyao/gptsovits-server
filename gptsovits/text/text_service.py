from typing import List

import torch
from .text_processor import LanguageProcessorFactory
from .phoneme_converter import PhonemeConverter

class TextService:
  def __init__(self, device='cuda', dtype=torch.float32):
    self.device = device
    self.dtype = dtype

    PhonemeConverter.set_device(device)
    PhonemeConverter.set_dtype(dtype)

  def process_text(self, text: str, language = None):
    language = self._detect_language(text) if not language else language
    processor = LanguageProcessorFactory.get_processor(language)
    return processor.process(text)
  
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
  
  def _detect_language(self, text: str) -> str:
    # 使用第三方库进行语言检测
    return "chinese"