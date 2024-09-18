import os

def relative_base_path(path: str = ''):
    user_data_dir = os.getenv('USER_DATA_PATH', '')
    return os.path.join(user_data_dir, path)

def pretrained_models_base_path(path: str = ''):
    return relative_base_path(os.path.join('pretrained_models', path))
