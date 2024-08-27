import os, logging, shutil
import boto3
from botocore.client import Config

class FileService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.bucket_name = os.getenv('R2_BUCKET_NAME')
        self.s3 = boto3.client('s3',
            endpoint_url=f'https://{os.getenv("R2_ACCOUNT_ID")}.r2.cloudflarestorage.com',
            aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )
        self.cache_dir = os.getenv('CACHE_DIR', '/tmp/r2_cache')
        os.makedirs(self.cache_dir, exist_ok=True)

    def upload_file(self, file_path, object_name=None):
        if object_name is None:
            object_name = file_path.split('/')[-1]
        
        try:
            self.s3.upload_file(file_path, self.bucket_name, object_name)
            return True
        except Exception as e:
            self.logger.error(f"上传文件时出错: {e}", exc_info=True)
            return False

    def download_file(self, object_name, file_path):
        cache_path = os.path.join(self.cache_dir, object_name)
        if os.path.exists(cache_path):
            self.logger.info(f"从缓存返回文件: {object_name}")
            os.rename(cache_path, file_path)
            return True

        try:
            self.s3.download_file(self.bucket_name, object_name, file_path)
            # 下载成功后，将文件复制到缓存
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            shutil.copy(file_path, cache_path)
            return True
        except Exception as e:
            self.logger.error(f"下载文件时出错: {e}", exc_info=True)
            return False

    def delete_file(self, object_name):
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=object_name)
            # 同时删除缓存中的文件
            cache_path = os.path.join(self.cache_dir, object_name)
            if os.path.exists(cache_path):
                os.remove(cache_path)
            return True
        except Exception as e:
            self.logger.error(f"删除文件时出错: {e}")
            return False

    def list_files(self, prefix=''):
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            files = [obj['Key'] for obj in response.get('Contents', [])]
            return files
        except Exception as e:
            self.logger.error(f"列出文件时出错: {e}")
            return []

    def get_file_url(self, object_name, expires_in=3600):
        try:
            url = self.s3.generate_presigned_url('get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_name},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            self.logger.error(f"生成文件 URL 时出错: {e}")
            return None

    @classmethod
    def get_instance(cls):
        """
        获取FileService的单例实例
        :return: FileService实例
        """
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance

    def __new__(cls):
        """
        确保只创建一个FileService实例
        """
        if not hasattr(cls, '_instance'):
            cls._instance = super(FileService, cls).__new__(cls)
        return cls._instance

