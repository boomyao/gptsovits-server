import pickle, os


def load_pickle(file_path, default=None):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return pickle.load(f)
    return default

def save_pickle(data, file_path):
    with open(file_path, "wb") as f:
        pickle.dump(data, f)