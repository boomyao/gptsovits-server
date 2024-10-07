import os, uuid
import logging
# from .file_service import FileService
import requests
import concurrent.futures
from gptsovits.contant import pretrained_models_base_path

REQUIRED_FILES = ['gpt.pth', 'sovits.pth', 'gptsovits.yaml']

class ModelFileService:
    _instance = None

    def __init__(self, file_service=None):
        # if not hasattr(self, 'file_service'):
            # self.file_service = file_service or FileService.get_instance()
        self.model_dir = 'voices'
        self.logger = logging.getLogger(__name__)

    @classmethod
    def get_instance(cls):
        """
        获取ModelFileService的单例实例
        :return: ModelFileService实例
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __new__(cls, *args, **kwargs):
        """
        确保只创建一个ModelFileService实例
        """
        if cls._instance is None:
            cls._instance = super(ModelFileService, cls).__new__(cls)
        return cls._instance

    def download_model_with_config(self, config):
        fileUrls = config['fileUrls']

        def download_file(file_path, url):
            local_path = os.path.join(pretrained_models_base_path(), file_path)
            if not os.path.exists(local_path):
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                response = requests.get(url)
                if response.status_code == 200:
                    with open(local_path, 'wb') as f:
                        f.write(response.content)
                    return f"成功下载: {file_path}"
                else:
                    return f"下载失败: {file_path}, 状态码: {response.status_code}"
            return f"文件已存在，跳过: {file_path}"

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(download_file, file_path, url): file_path for file_path, url in fileUrls.items()}
            for future in concurrent.futures.as_completed(future_to_url):
                file_path = future_to_url[future]
                try:
                    result = future.result()
                    self.logger.info(result)
                except Exception as exc:
                    self.logger.error(f"{file_path} 下载出错: {exc}")

        return True

    def download_model(self, model_id):
        from .file_service import FileService
        file_service = FileService.get_instance()
        files = file_service.list_files(f'voices/{model_id}')
        os.makedirs(pretrained_models_base_path(f'voices/{model_id}'), exist_ok=True)
        os.makedirs(pretrained_models_base_path(f'voices/{model_id}/presets'), exist_ok=True)
        for file in files:
            file_service.download_file(file, pretrained_models_base_path(file))
