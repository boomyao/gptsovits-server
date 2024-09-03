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
        ref_features, ref_mel_specs = self.speech_service.process_audio(ref_audio, ref_prompt)
        
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
