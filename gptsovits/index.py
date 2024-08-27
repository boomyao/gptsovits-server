from hyperpyyaml import load_hyperpyyaml
from gptsovits.frontend import GPTSovitsFrontend
from gptsovits.model import GPTSovitsModel
import numpy as np
from huggingface_hub import snapshot_download

def download_model(id: str) -> str:
    return 'pretrained_models/voices/{}'.format(id)

class GPTSovits:
    def __init__(self, id: str):
        self.id = id

        self.shared_model = GPTSovits.load_shared_models()

        model_dir = download_model(self.id)

        self.model_dir = model_dir  

    def load(self):
        model_dir = self.model_dir
        with open('{}/gptsovits.yaml'.format(model_dir), 'r') as f:
            configs = load_hyperpyyaml(f)

        self.model = GPTSovitsModel(configs['gpt'], configs['sovits'])
        self.model.load('{}/gpt.ckpt'.format(model_dir), '{}/sovits.pth'.format(model_dir))

        self.frontend = GPTSovitsFrontend()

    def inference(self, text: str, ref_id: str, speed = 1):
        ref_audio, ref_prompt = self.load_reference(ref_id)
        
        tts_speeches = []
        generator = self.frontend.zero_shot(text, ref_audio, ref_prompt, speed)
        for model_input in generator:
            model_output = self.model.inference(**model_input)
            tts_speeches.append(model_output)
            tts_speeches.append(self.frontend.speech_service.get_zero_wav())

        return (np.concatenate(tts_speeches, 0) * 32768).astype(np.int16)
        

    def load_reference(self, ref_id: str):
        presets_dir = '{}/presets'.format(self.model_dir)
        with open('{}/{}.txt'.format(presets_dir, ref_id), 'r') as f:
            ref_prompt = f.read()
        with open('{}/{}.wav'.format(presets_dir, ref_id), 'rb') as f:
            ref_audio = f.read()
        return ref_audio, ref_prompt


    @staticmethod
    def load_shared_models():
        snapshot_download(repo_id="boomyao/gptsovits", local_dir="pretrained_models")
