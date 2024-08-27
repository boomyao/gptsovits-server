import os, uuid
import logging
from .file_service import FileService

class ModelFileService:
    _instance = None

    def __init__(self, file_service=None):
        if not hasattr(self, 'file_service'):
            self.file_service = file_service or FileService.get_instance()
        self.model_dir = 'voices'
        self.logger = logging.getLogger(__name__)

    @classmethod
    def get_instance(cls):
        """
        获取ModelFileService的单例实例
        :return: ModelFileService实例
        """
        if cls._instance is None:
            cls._instance = cls(FileService.get_instance())
        return cls._instance

    def __new__(cls, *args, **kwargs):
        """
        确保只创建一个ModelFileService实例
        """
        if cls._instance is None:
            cls._instance = super(ModelFileService, cls).__new__(cls)
        return cls._instance

    def upload_model(self, model_dir):
        """
        上传模型文件到存储服务
        :param model_dir: 模型文件目录路径
        :return: 上传成功返回模型ID，失败返回None
        """
        model_id = str(uuid.uuid4())
        required_files = ['gpt.ckpt', 'sovits.pth', 'gptsovits.yaml']
        model_dir = os.path.abspath(model_dir)
        
        for file_name in required_files:
            local_path = os.path.join(model_dir, file_name)
            if not os.path.exists(local_path):
                self.logger.error(f"错误：{file_name} 不存在于指定目录中")
                return None

            object_name = f"{self.model_dir}/{model_id}_{file_name}"
            if not self.file_service.upload_file(local_path, object_name):
                self.logger.error(f"错误：上传 {file_name} 失败")
                return None

        self.logger.info(f"模型 {model_id} 上传成功")
        return model_id

    def download_model(self, model_id):
        """
        从存储服务下载模型文件
        :param model_id: 模型ID
        :return: 是否下载成功
        """
        local_dir = f"pretrained_models/voices/{model_id}"
        os.makedirs(local_dir, exist_ok=True)

        required_files = ['gpt.ckpt', 'sovits.pth', 'gptsovits.yaml']
        success = True

        for file_name in required_files:
            object_name = f"{self.model_dir}/{model_id}_{file_name}"
            local_path = os.path.join(local_dir, file_name)
            if not self.file_service.download_file(object_name, local_path):
                self.logger.error(f"错误：下载 {file_name} 失败")
                success = False
                break

        if success:
            self.logger.info(f"模型 {model_id} 下载成功")
        return success

    def delete_model(self, model_id):
        """
        删除存储服务中的模型文件
        :param model_id: 模型ID
        :return: 是否删除成功
        """
        required_files = ['gpt.ckpt', 'sovits.pth', 'gptsovits.yaml']
        success = True

        for file_name in required_files:
            object_name = f"{self.model_dir}/{model_id}_{file_name}"
            if not self.file_service.delete_file(object_name):
                print(f"错误：删除 {file_name} 失败")
                success = False

        return success

    def list_models(self):
        """
        列出所有可用的模型
        :return: 模型ID列表
        """
        files = self.file_service.list_files(f"{self.model_dir}/")
        model_ids = set()
        for file in files:
            parts = file.split('_')
            if len(parts) > 1:
                model_ids.add(parts[0].split('/')[-1])
        return list(model_ids)

    def get_model_files_url(self, model_id, expires_in=3600):
        """
        获取模型文件的临时访问URL
        :param model_id: 模型ID
        :param expires_in: URL有效期（秒）
        :return: 模型文件URL字典
        """
        required_files = ['gpt.ckpt', 'sovits.pth', 'gptsovits.yaml']
        urls = {}

        for file_name in required_files:
            object_name = f"{self.model_dir}/{model_id}_{file_name}"
            url = self.file_service.get_file_url(object_name, expires_in)
            if url:
                urls[file_name] = url
            else:
                self.logger.warning(f"警告：无法获取 {file_name} 的URL")

        return urls

    def upload_presets(self, model_id, presets_dir):
        """
        上传模型的预设数据（音频和文本文件）
        :param model_id: 模型ID
        :param presets_dir: 预设数据目录路径
        :return: 是否上传成功
        """
        presets_dir = os.path.abspath(presets_dir)
        success = True
        file_pairs = {}

        # 首先，将文件按基本名称分组
        for file_name in os.listdir(presets_dir):
            if file_name.endswith(('.wav', '.txt')):
                base_name = os.path.splitext(file_name)[0]
                if base_name not in file_pairs:
                    file_pairs[base_name] = {'wav': None, 'txt': None}
                file_pairs[base_name][file_name.split('.')[-1]] = file_name

        # 然后，上传每对文件
        for base_name, files in file_pairs.items():
            if files['wav'] and files['txt']:
                preset_uuid = str(uuid.uuid4())
                for ext in ['wav', 'txt']:
                    local_path = os.path.join(presets_dir, files[ext])
                    object_name = f"presets/{model_id}/{preset_uuid}.{ext}"
                    if not self.file_service.upload_file(local_path, object_name):
                        self.logger.error(f"错误：上传预设文件 {files[ext]} 失败")
                        success = False
            else:
                self.logger.warning(f"警告：预设 {base_name} 缺少配对的 .wav 或 .txt 文件")

        return success

    def download_presets(self, model_id):
        local_dir = f"pretrained_models/voices/{model_id}/presets"
        """
        下载模型的预设数据（音频和文本文件）
        :param model_id: 模型ID
        :param local_dir: 本地保存目录
        :return: 是否下载成功
        """
        os.makedirs(local_dir, exist_ok=True)
        success = True

        object_files = self.file_service.list_files(f"presets/{model_id}/")
        # 遍历所有预设文件
        for object_name in object_files:
            # 获取文件名
            file_name = os.path.basename(object_name)
            # 构建本地文件路径
            local_file_path = os.path.join(local_dir, file_name)
            
            # 下载文件
            if self.file_service.download_file(object_name, local_file_path):
                self.logger.info(f"成功下载预设文件: {file_name}")
            else:
                self.logger.error(f"下载预设文件失败: {file_name}")
                success = False

        if success:
            self.logger.info(f"所有预设文件已成功下载到 {local_dir}")
        else:
            self.logger.warning("部分预设文件下载失败")

        return success
