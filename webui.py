import gradio as gr
from gptsovits_manager import GPTSovitsManager
from gptsovits.contant import relative_base_path
import uuid
import soundfile as sf
import logging
import os

logging.basicConfig(level=logging.DEBUG if os.getenv("DEBUG") else logging.INFO)

mgr = GPTSovitsManager()

TMP_PATH = 'tmp'
TMP_ROOT_DIR = relative_base_path(TMP_PATH)

def generate_audio(text, model_id, preset_id):
  model = mgr.get(model_id)
  if not model:
    raise gr.Error(f"模型 {model_id} 不存在")
  audio = model.inference(text, ref_id=preset_id)
  
  obj_path = f"{TMP_ROOT_DIR}/{uuid.uuid4()}.wav"
  sf.write(obj_path, audio, 32000, format='wav')
  return obj_path

iface = gr.Interface(
    fn=generate_audio,
    inputs=[
      gr.Textbox(label="输入文本"),
      gr.Textbox(label="模型"),
      gr.Textbox(label="预设")
    ],
    outputs=gr.Audio(label="音频输出")
).launch(debug=True, server_name="0.0.0.0")