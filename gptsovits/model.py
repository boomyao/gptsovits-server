import torch
import numpy as np

class GPTSovitsModel:
  def __init__(self,
    gpt: torch.nn.Module,
    sovits: torch.nn.Module):
    self.gpt = gpt
    self.sovits = sovits

    self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    self.is_half = True if self.device == 'cuda' else False

    self.top_k = 15
    self.top_p = 1
    self.temperature = 1
    self.hz = 50
    self.max_sec = 54

  def load(self, gpt_path, sovits_path):
    self.gpt.load_state_dict(torch.load(gpt_path, map_location=self.device)['weight'])
    self.sovits.load_state_dict(torch.load(sovits_path, map_location=self.device)['weight'])
    if self.is_half:
      self.gpt.half()
      self.sovits.half()
    self.gpt.to(self.device)
    self.sovits.to(self.device)
    self.gpt.eval()
    self.sovits.eval()

  def inference(self, text, bert_features, phoneme, all_phoneme_ids, all_phoneme_len,ref_features,ref_mel_specs, speed):
    semantic_embedding = self._extract_embeddings(ref_features) if ref_features is not None else None
    pred_semantic = self._extract_pred_semantic(all_phoneme_ids, all_phoneme_len, semantic_embedding, bert_features)
    audio = self.sovits.decode(pred_semantic, phoneme, ref_mel_specs, speed).detach().cpu().numpy()[0, 0]
    max_audio=np.abs(audio).max()#简单防止16bit爆音
    if max_audio>1:audio/=max_audio
    return audio

  def _extract_pred_semantic(self, all_phoneme_ids, all_phoneme_len, semantic_embedding, bert_features):
    top_k = self.top_k
    top_p = self.top_p
    temperature = self.temperature
    hz = self.hz
    max_sec = self.max_sec

    with torch.no_grad():
      pred_semantic, idx = self.gpt.model.infer_panel(
          all_phoneme_ids,
          all_phoneme_len,
          semantic_embedding,
          bert_features,
          top_k=top_k,
          top_p=top_p,
          temperature=temperature,
          early_stop_num=hz * max_sec,
      )
      pred_semantic = pred_semantic[:, -idx:].unsqueeze(0)
    return pred_semantic

  def _extract_embeddings(self, ref_features):
    codes = self.sovits.extract_latent(ref_features)
    prompt_semantic = codes[0, 0]
    prompt = prompt_semantic.unsqueeze(0).to(self.device)
    return prompt