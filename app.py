

from gptsovits_manager import GPTSovitsManager
import soundfile as sf

def main():
  mgr = GPTSovitsManager()

  id = '80ffe8c8-a205-49b5-a745-470e1e47c02f'
  gptsovits = mgr.get(id)

  audio = gptsovits.inference('你好呀', '2feac86a-c5ab-4751-939a-9b94f19e1872')

  sf.write('output.wav', audio, 32000)

if __name__ == '__main__':
  main()