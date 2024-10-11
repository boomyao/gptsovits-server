from tools.path import abs_path
import ffmpeg
import os
from typing import List
import zipfile

IS_WINDOWS = os.name == 'nt'

if IS_WINDOWS:
    os.environ['FFMPEG_BINARY'] = os.path.join(os.getcwd(), 'ffmpeg.exe')

def speed_wav_file(input_file: str, speed: float = 1) -> str:
    input_file = abs_path(input_file)
    temp_file = f'{input_file}-{speed}.wav'

    if speed == 1:
        return input_file
    
    ffmpeg.input(input_file).filter('atempo', speed).output(temp_file).run(overwrite_output=True)
    return temp_file


def merge_wav_files(input_files: List[str], output_file: str) -> str:
    concat_file = os.path.join(os.getcwd(), 'concat.txt')
    with open(concat_file, 'w', encoding='utf-8') as f:
        for input_file in input_files:
            f.write(f"file '{input_file}'\n")

    ffmpeg.input(concat_file, format='concat', safe=0).output(output_file).run(overwrite_output=True)

    os.remove(concat_file)
    return output_file

def pack_wav_files(input_files: List[str], output_file: str) -> str:
    with zipfile.ZipFile(output_file, 'w') as zip:
        for input_file in input_files:
            zip.write(input_file, os.path.basename(input_file))
    return output_file
