# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hookspath=['./build_hooks'],
    hiddenimports=[
        'engineio.async_drivers.threading',
        'gptsovits.AR.models.t2s_lightning_module',
        'gptsovits.AR.models.t2s_model',
        'gptsovits.sovits.models',
    ],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tensorflow', 'tensorboard', 'botocore', 'boto3', 'IPython'],
    noarchive=False,
    optimize=1,
    module_collection_mode={
        "g2p_en": "py",
        "gptsovits.AR.models.t2s_lightning_module": "py",
        "gptsovits.AR.models.t2s_model": "py",
        "gptsovits.sovits.models": "py",
        "modelscope": "py",
        "torch": "py",
        "numpy": "py",
        "transformers": "py",
        "flask": "py",
        "flask_socketio": "py",
        "nltk": "py",
        "py3langid": "py",
        "pypinyin": "py",
        "jieba_fast": "py",
        "librosa": "py",
        "soundfile": "py",
    }
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='gptsovits',
)
