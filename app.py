

from gptsovits_manager import GPTSovitsManager
import soundfile as sf

def main():
  mgr = GPTSovitsManager()

  id = '001'
  gptsovits = mgr.get(id)

  audio = gptsovits.inference('你好呀', 'source.mp3_0000021120_0000223040')

  sf.write('output.wav', audio, 32000)

if __name__ == '__main__':
  main()