from gptsovits.index import GPTSovits
from gptsovits.text.symbols import get_symbols
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
  from services.model_file_service import ModelFileService

  modelFileService = ModelFileService.get_instance()

  # modelFileService.upload_model('./pretrained_models/voices/001')
  # modelFileService.download_model('80ffe8c8-a205-49b5-a745-470e1e47c02f')
  # modelFileService.upload_presets('80ffe8c8-a205-49b5-a745-470e1e47c02f', './pretrained_models/voices/001/presets')
  modelFileService.download_presets('80ffe8c8-a205-49b5-a745-470e1e47c02f')