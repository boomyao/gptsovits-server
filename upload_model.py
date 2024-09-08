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

  print('开始上传模型')
  id = modelFileService.upload_model(model_dir)
  if id is None:
    print('模型上传失败')
    exit(1)

  print('开始上传预设')
  modelFileService.upload_presets(id, '{}/presets'.format(model_dir))
  print(f'模型上传成功，ID为：{id}')