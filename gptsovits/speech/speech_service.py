import torch, io, librosa
from .feature_extractor import cnhubert
import numpy as np
from gptsovits.module.mel_processing import spectrogram_torch
from .constants import FILTER_LENGTH, HOP_LENGTH, WIN_LENGTH, SAMPLE_RATE
from gptsovits.contant import pretrained_models_base_path

class SpeechService:
  def __init__(self, device='cuda', dtype=torch.float32):
    self.device = device
    self.dtype = dtype

    self.is_half = dtype == torch.float16

    cnhubert_base_path = pretrained_models_base_path('gptsovits/chinese-hubert-base')

    cnhubert.cnhubert_base_path = cnhubert_base_path

    ssl_model = cnhubert.get_model()
    self.ssl_model = ssl_model.half().to(device) if self.is_half else ssl_model.to(device)

  def process_audio(self, audio: bytes, ref_prompt = None):
    ref_features = self._get_ref_features(audio) if ref_prompt else None
    mel_specs = self._get_mel_specs(audio)
    return ref_features, mel_specs
  
  def _get_ref_features(self, ref_audio: bytes):
    device = self.device
    audio_file = io.BytesIO(ref_audio)
    
    wav16k, sr = librosa.load(audio_file, sr=16000)
    
    wav16k = torch.from_numpy(wav16k)
    zero_wav = self.get_zero_wav(sr)
    zero_wav_torch = torch.from_numpy(zero_wav)
    
    if self.is_half:
        wav16k = wav16k.half().to(device)
        zero_wav_torch = zero_wav_torch.half().to(device)
    else:
        wav16k = wav16k.to(device)
        zero_wav_torch = zero_wav_torch.to(device)
    
    wav16k = torch.cat([wav16k, zero_wav_torch])
    
    ssl_content = self.ssl_model.model(wav16k.unsqueeze(0))["last_hidden_state"].transpose(1, 2)
    
    return ssl_content
  
  def _get_mel_specs(self, audio: bytes):
    audio, _ = librosa.load(io.BytesIO(audio), sr=SAMPLE_RATE)
    audio = torch.FloatTensor(audio)
    maxx=audio.abs().max()
    if(maxx>1):audio/=min(2,maxx)
    audio_norm = audio
    audio_norm = audio_norm.unsqueeze(0)
    spec = spectrogram_torch(
        audio_norm,
        FILTER_LENGTH,
        SAMPLE_RATE,
        HOP_LENGTH,
        WIN_LENGTH,
        center=False,
    )
    return [spec.to(self.dtype).to(self.device)]

  def get_zero_wav(self, sr=32000):
    is_half = self.is_half
    zero_wav = np.zeros(
        int(sr * 0.3),
        dtype=np.float16 if is_half == True else np.float32,
    )
    return zero_wav
