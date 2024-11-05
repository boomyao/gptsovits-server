import torch
from gptsovits.index import GPTSovits
import os
import requests
from tqdm import tqdm
import concurrent.futures
from tools.path import pretrained_models_base_path
from services.mongo import get_collection
from services.oss import cache_file
import shutil
from bson.objectid import ObjectId
VOICE_BASE_DIR = pretrained_models_base_path('voices')

class GPTSovitsManager:
    def __init__(self, memory_threshold=0.9):
        self.cached_gptsovits = {}
        self.memory_threshold = memory_threshold
  
    def get(self, id: str, auto_download=True):
        if id in self.cached_gptsovits:
            return self.cached_gptsovits[id]
        else:
            if auto_download:
                self.download_model(id)
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
        prefix = 'https://modelscope.cn/models/boomyao/easyvoice/resolve/master'
        base_dir = pretrained_models_base_path()
        files = [
            'gptsovits/chinese-hubert-base/config.json',
            'gptsovits/chinese-hubert-base/preprocessor_config.json',
            'gptsovits/chinese-hubert-base/pytorch_model.bin',
            'gptsovits/chinese-roberta-wwm-ext-large/config.json',
            'gptsovits/chinese-roberta-wwm-ext-large/pytorch_model.bin',
            'gptsovits/chinese-roberta-wwm-ext-large/tokenizer.json',
            'nltk/corpora/cmudict/cmudict',
            'nltk/taggers/averaged_perceptron_tagger/averaged_perceptron_tagger.pickle',
            'nltk/taggers/averaged_perceptron_tagger_eng/averaged_perceptron_tagger_eng.classes.json',
            'nltk/taggers/averaged_perceptron_tagger_eng/averaged_perceptron_tagger_eng.tagdict.json',
            'nltk/taggers/averaged_perceptron_tagger_eng/averaged_perceptron_tagger_eng.weights.json',
        ]

        def download_file(file, max_retries=3):
            output_file = os.path.join(base_dir, file)
            if not os.path.exists(output_file):
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                for attempt in range(max_retries):
                    try:
                        response = requests.get(f'{prefix}/{file}', stream=True)
                        response.raise_for_status()
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
                    except (requests.RequestException, IOError) as e:
                        print(f"下载 {file} 时发生错误 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                        if attempt == max_retries - 1:
                            print(f"下载 {file} 失败，已达到最大重试次数")
                            return file, False
                        else:
                            print("正在重试...")
            else:
                return file, False

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
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

    def download_model(self, id: str):
        output_dir = f'{VOICE_BASE_DIR}/{id}'
        if os.path.exists(output_dir):
            return
        voice_collection = get_collection('vocrawl', 'voice')
        voice = voice_collection.find_one({'_id': ObjectId(id)})
        if not voice:
            raise Exception(f'voice {id} not found')
        cache_file(voice['sovits_object_name'], output_dir, ignore_object_dir=True)
        cache_file(voice['gpt_object_name'], output_dir, ignore_object_dir=True)
        shutil.copy('gptsovits.yaml', f'{output_dir}/gptsovits.yaml')

        voice_segment_collection = get_collection('vocrawl', 'voice_segment')
        voice_segments = voice_segment_collection.find({'voice_id': ObjectId(id)})
        for voice_segment in voice_segments:
            ref_audio_path = cache_file(voice_segment['ref_object_name'], f'{output_dir}/presets', ignore_object_dir=True)
            prompt_file = ref_audio_path.replace('.wav', '.txt')
            with open(prompt_file, 'w') as f:
                f.write(voice_segment['ref_text'])
    
    def _check_and_free_memory(self):
        if torch.cuda.is_available():
            current_memory = torch.cuda.memory_allocated() / torch.cuda.get_device_properties(0).total_memory
            if current_memory > self.memory_threshold:
                self._free_memory()
    
    def _free_memory(self):
        if self.cached_gptsovits:
            oldest_id = next(iter(self.cached_gptsovits))
            del self.cached_gptsovits[oldest_id]

if __name__ == '__main__':
    manager = GPTSovitsManager()
    manager.load_shared_models()
