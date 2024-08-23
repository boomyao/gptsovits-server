from abc import ABC, abstractmethod

class TextNormalizer(ABC):
    @abstractmethod
    def normalize_text(self, text: str) -> str:
        pass

class EmptyTextNormalizer(TextNormalizer):
    def normalize_text(self, text: str) -> str:
        return text