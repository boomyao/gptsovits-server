import os

class GPTSovitsManager:
    def __init__(self):
        self.cached_gptsovits = {}
  
    def get(self, id: str):
        if id in self.cached_gptsovits:
            return self.cached_gptsovits[id]
        else:
            # TODO memory check
            gptsovits = GPTSovits(id)
            gptsovits.load()
            self.cached_gptsovits[id] = gptsovits
            return gptsovits