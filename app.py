import os
import typeguard
typeguard.typechecked = lambda f: f

from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit
from services.model_file_service import ModelFileService
from gptsovits_manager import GPTSovitsManager
import soundfile as sf
import logging
import uuid
# import dotenv
# dotenv.load_dotenv()

IS_DEBUG = os.getenv('IS_DEBUG', 'false').lower() == 'true'

logging.basicConfig(level=logging.DEBUG if IS_DEBUG else logging.INFO)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('s3transfer').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 初始化GPTSovitsManager
mgr = GPTSovitsManager()

TMP_DIR = f'tmp'

@app.route('/static/tmp/<name>', methods=['GET'])
def serve_tmp_static(name):
    print(f'serve_tmp_static: {name}')
    return send_from_directory(TMP_DIR, name)

@socketio.on('tts')
def text_to_speech(data):
    if not data or 'text' not in data or 'model_id' not in data or 'ref_audio_id' not in data:
        return {'error': '缺少必要的参数'}

    text = data['text']
    model_id = data['model_id']
    ref_audio_id = data['ref_audio_id']

    try:
        gptsovits = mgr.get(model_id)
        audio = gptsovits.inference(text, ref_audio_id)

        object_name = f'{TMP_DIR}/{str(uuid.uuid4())}.wav'
        sf.write(object_name, audio, 32000, format='wav')

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

serve_state = None
@socketio.on('connect')
def on_connect():
    global serve_state
    if serve_state is None:
        serve_state = 'Downloading'
        emit('state', {'state': serve_state}, broadcast=True)
        mgr.load_shared_models()
        serve_state = 'Done'
        emit('state', {'state': serve_state}, broadcast=True)
    else:
        emit('state', {'state': serve_state}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=55001, allow_unsafe_werkzeug=True)
