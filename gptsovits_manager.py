import torch
from gptsovits.index import GPTSovits

class GPTSovitsManager:
    def __init__(self, memory_threshold=0.9):
        self.cached_gptsovits = {}
        self.memory_threshold = memory_threshold
  
    def get(self, id: str):
        if id in self.cached_gptsovits:
            return self.cached_gptsovits[id]
        else:
            self._check_and_free_memory()
            gptsovits = GPTSovits(id)
            gptsovits.load()
            self.cached_gptsovits[id] = gptsovits
            return gptsovits
    
    def _check_and_free_memory(self):
        if torch.cuda.is_available():
            current_memory = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated()
            if current_memory > self.memory_threshold:
                self._free_memory()
    
    def _free_memory(self):
        if self.cached_gptsovits:
            oldest_id = next(iter(self.cached_gptsovits))
            del self.cached_gptsovits[oldest_id]
            torch.cuda.empty_cache()