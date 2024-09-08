import typeguard
typeguard.typechecked = lambda x: x

from gptsovits_manager import GPTSovitsManager
import argparse
import soundfile as sf
import uuid

TMP_DIR = '/tmp'

mgr = GPTSovitsManager()

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--model_id', type=str, required=True)
  parser.add_argument('--text', type=str, required=True)
  parser.add_argument('--ref_audio_id', type=str, required=True)
  args = parser.parse_args()

  model_id = args.model_id
  text = args.text
  ref_audio_id = args.ref_audio_id

  gptsovits = mgr.get(model_id)
  audio = gptsovits.inference(text, ref_audio_id)

  file_name = f'{TMP_DIR}/{str(uuid.uuid4())}.wav'
  sf.write(file_name, audio, 32000, format='wav')

  print(file_name)