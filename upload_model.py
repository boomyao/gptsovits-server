from dotenv import load_dotenv
import argparse

load_dotenv()

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--model_dir', type=str, required=True)
  args = parser.parse_args()

  model_dir = args.model_dir

  from services.model_file_service import ModelFileService

  modelFileService = ModelFileService.get_instance()

  id = modelFileService.upload_model(model_dir)
  modelFileService.upload_presets(id, '{}/presets'.format(model_dir))
  print(f'模型上传成功，ID为：{id}')