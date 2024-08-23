from gptsovits_manager import GPTSOVITSManager

def main():
  gptsovitsMgr = GPTSOVITSManager()

  gptsovits = gptsovitsMgr.get('xxxx')

  audio = gptsovits(text, ref_id)

  return audio