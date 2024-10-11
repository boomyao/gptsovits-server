import os, io
from flask import Flask, send_from_directory, request, Response
from flask_socketio import SocketIO
from tools.model_file_service import ModelFileService
from flask_cors import CORS
import soundfile as sf
import logging
import uuid
import shutil
from tools.path import relative_base_path, pretrained_models_base_path, abs_path
from tools.media import speed_wav_file, merge_wav_files, pack_wav_files
from gptsovits_manager import GPTSovitsManager

IS_DEBUG = os.getenv('IS_DEBUG', 'false').lower() == 'true'

logging.basicConfig(level=logging.DEBUG if IS_DEBUG else logging.INFO)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('s3transfer').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 初始化GPTSovitsManager
mgr = GPTSovitsManager()

TMP_PATH = 'tmp'
TMP_ROOT_DIR = relative_base_path(TMP_PATH)
if os.path.exists(pretrained_models_base_path(TMP_PATH)):
    shutil.move(pretrained_models_base_path(TMP_PATH), TMP_ROOT_DIR)
else:
    os.makedirs(TMP_ROOT_DIR, exist_ok=True)

@app.route('/static/tmp/<name>', methods=['GET'])
def serve_tmp_static(name):
    return send_from_directory(os.path.abspath(TMP_ROOT_DIR), name)

@app.route('/tts', methods=['POST'])
def tts():
    try:
        data = request.get_json()
        text = data.get('text')
        model_id = data.get('model_id')
        ref_id = data.get('ref_id')
        extra_ref_ids = data.get('extra_ref_ids') or []
        gptsovits = mgr.get(model_id)
        audio = gptsovits.inference(text, ref_id=ref_id, extra_ref_ids=extra_ref_ids)   

        wav_io = io.BytesIO()
        sf.write(wav_io, audio, 32000, format='wav')

        return Response(wav_io.getvalue(), content_type='audio/wav')
    except Exception as e:
        logger.error(e, exc_info=True)
        return Response(status=500, response=str(e))

@socketio.on('tts')
def text_to_speech(data):
    if not data or 'text' not in data or 'model_id' not in data or 'ref_audio_id' not in data:
        return {'error': '缺少必要的参数'}

    text = data['text']
    model_id = data['model_id']
    ref_audio_id = data.get('ref_audio_id')
    try:
        gptsovits = mgr.get(model_id)
        audio = gptsovits.inference(text, ref_id=ref_audio_id)

        object_name = f'{TMP_PATH}/{str(uuid.uuid4())}.wav'
        sf.write(relative_base_path(object_name), audio, 32000, format='wav')

        return {'object_name': object_name}

    except Exception as e:
        logger.error(e, exc_info=True)
        return {'error': str(e)}

@socketio.on('download_voice')
def download_voice(data):
    try:
        model_file_service = ModelFileService.get_instance()
        model_file_service.download_model_with_config(data)
        return {'success': True}
    except Exception as e:
        logger.error(e, exc_info=True)
        return {'error': str(e)}

@socketio.on('get_download_voice_state')
def get_voice_dl_state(data):
    ids = data['ids']
    state = mgr.get_download_state(ids)
    return state

@socketio.on('load_base_models')
def load_base_models(data):
    mgr.load_shared_models()
    return {'success': True}

@socketio.on('download_dub_result')
def download_dub_result(data):
    input_paths = [abs_path(path) for path in data['audioPaths']]
    output_path = abs_path(data['outputPath'])
    speed = data.get('speed', 1)
    compress = data.get('compress', False)
    if speed != 1:
        input_paths = [speed_wav_file(input_path, speed) for input_path in input_paths]

    try:
        if compress:
            result = pack_wav_files(input_paths, output_path)
        else:
            result = merge_wav_files(input_paths, output_path)
        return {'result': result}
    except Exception as e:
        logger.error(e, exc_info=True)
        return {'error': str(e)}

def main():
    socketio.run(app, host='0.0.0.0', port=55001, allow_unsafe_werkzeug=True, debug=IS_DEBUG)

if __name__ == '__main__':
    main()
