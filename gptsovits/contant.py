import os

def relative_base_path(path: str = ''):
    user_data_dir = os.getenv('USER_DATA_PATH', '')
    return os.path.join(user_data_dir, 'pretrained_models', path)