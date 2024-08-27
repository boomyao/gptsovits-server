from flask import Flask, request, jsonify
from gptsovits_manager import GPTSovitsManager
from services.file_service import FileService
import soundfile as sf
import io
import base64

app = Flask(__name__)

# 初始化GPTSovitsManager
mgr = GPTSovitsManager()
file_service = FileService.get_instance()

@app.route('/tts', methods=['POST'])
def text_to_speech():
    data = request.json
    if not data or 'text' not in data or 'model_id' not in data or 'ref_audio_id' not in data:
        return jsonify({'error': '缺少必要的参数'}), 400

    text = data['text']
    model_id = data['model_id']
    ref_audio_id = data['ref_audio_id']

    try:
        # 获取模型实例
        gptsovits = mgr.get(model_id)

        # 执行推理
        audio = gptsovits.inference(text, ref_audio_id)

        # 将音频数据转换为字节流
        audio_bytes = io.BytesIO()
        sf.write(audio_bytes, audio, 32000, format='wav')

        object_name = file_service.upload_tmp_file(audio_bytes, ext='wav')

        return jsonify({'object_name': object_name})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)