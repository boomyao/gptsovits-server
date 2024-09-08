# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['cli.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hookspath=['./build_hooks'],
    hiddenimports=[
        'gptsovits.AR.models.t2s_lightning_module',
        'gptsovits.AR.models.t2s_model',
        'gptsovits.sovits.models'
    ],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
    module_collection_mode={
        "g2p_en": "py",
        "gptsovits.AR.models.t2s_lightning_module": "py",
        "gptsovits.AR.models.t2s_model": "py",
        "gptsovits.sovits.models": "py",
    }
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='cli',
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
    name='cli',
)
