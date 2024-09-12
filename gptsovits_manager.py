import torch
from gptsovits.index import GPTSovits
import os
import requests
from tqdm import tqdm
import concurrent.futures

VOICE_BASE_DIR = 'pretrained_models/voices'

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
    
    def get_download_state(self, ids):
        result = {}
        for id in ids:
            path = f'{VOICE_BASE_DIR}/{id}'
            if os.path.exists(path):
                result[id] = 1
            else:
                result[id] = 0
        return result
    
    def load_shared_models(self):
        prefix = 'https://modelscope.cn/models/boomyao/easyvoice/resolve/master/gptsovits'
        base_dir = 'pretrained_models/gptsovits'
        files = [
            'chinese-hubert-base/config.json',
            'chinese-hubert-base/preprocessor_config.json',
            'chinese-hubert-base/pytorch_model.bin',
            'chinese-roberta-wwm-ext-large/config.json',
            'chinese-roberta-wwm-ext-large/pytorch_model.bin',
            'chinese-roberta-wwm-ext-large/tokenizer.json'
        ]

        def download_file(file):
            output_file = os.path.join(base_dir, file)
            if not os.path.exists(output_file):
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                response = requests.get(f'{prefix}/{file}', stream=True)
                if response.status_code == 200:
                    total_size = int(response.headers.get('content-length', 0))
                    with open(output_file, 'wb') as f, tqdm(
                        desc=file,
                        total=total_size,
                        unit='iB',
                        unit_scale=True,
                        unit_divisor=1024,
                    ) as progress_bar:
                        for data in response.iter_content(chunk_size=1024):
                            size = f.write(data)
                            progress_bar.update(size)
                return file, True
            return file, False

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            future_to_file = {executor.submit(download_file, file): file for file in files}
            for future in concurrent.futures.as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    _, success = future.result()
                    if success:
                        print(f"成功下载: {file}")
                    else:
                        print(f"文件已存在,跳过: {file}")
                except Exception as exc:
                    print(f"{file} 下载失败: {exc}")
    
    def _check_and_free_memory(self):
        if torch.cuda.is_available():
            current_memory = torch.cuda.memory_allocated() / torch.cuda.get_device_properties(0).total_memory
            if current_memory > self.memory_threshold:
                self._free_memory()
    
    def _free_memory(self):
        if self.cached_gptsovits:
            oldest_id = next(iter(self.cached_gptsovits))
            del self.cached_gptsovits[oldest_id]