import re
import ffmpeg
import numpy as np

chinese_char_pattern = re.compile(r'[\u4e00-\u9fff]+')

# whether contain chinese character
def contains_chinese(text):
    return bool(chinese_char_pattern.search(text))

def load_audio(file, sr):
    try:
        out, _ = (
            ffmpeg.input(file, threads=0)
            .output("-", format="f32le", acodec="pcm_f32le", ac=1, ar=sr)
            .run(cmd=["ffmpeg", "-nostdin"], capture_stdout=True, capture_stderr=True)
        )
    except Exception as e:
        raise ValueError(f"Failed to load audio file: {e}")

    return np.frombuffer(out, np.float32).flatten()