from abc import ABC, abstractmethod
from typing import Tuple

from torch import Tensor
import torch

class PhonemeConverter(ABC):
    dtype = torch.float32
    device = 'cuda'

    @staticmethod
    def set_device(device: str):
        PhonemeConverter.device = device

    @staticmethod
    def set_dtype(dtype: torch.dtype):
        PhonemeConverter.dtype = dtype

    def __init__(self):
        self.device = PhonemeConverter.device
        self.dtype = PhonemeConverter.dtype

    @abstractmethod
    def convert_to_phonemes(self, text: str) -> Tuple[list[str], list[int]]:
        pass

    def get_bert_features(self, text: str, phonemes: list[str], phoneme_lengths: list[int]) -> Tensor:
        return torch.zeros(
            (1024, len(phonemes)),
            dtype=self.dtype
        ).to(self.device)