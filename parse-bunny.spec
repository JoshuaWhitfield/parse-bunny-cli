# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('setup.enc', '.'),         # Encrypted config
        ('key.bin', '.'),           # Encryption key
        ('commands/config.json', 'commands'),
        ('secure_setup.py', '.'),   # Your encryption/decryption logic
        ('commands', 'commands'),
        ('syntax', 'syntax'),
        ('environments', 'environments'),
        ('dependencies', 'dependencies'),
        ('internal', 'internal'),
    ],
    hiddenimports=[
        'json', 'datetime', 'os', 'sys', 're', 'pathlib', 'pkgutil',
        'commands', 'commands.command', 'commands.base', 'commands.parsing',
        'secure_setup',  # Make sure secure_setup is included
        'syntax', 'syntax.lexer', 'syntax.parser', 'syntax.interface', 'syntax.types',
        'environments', 'environments.piping',
        'dependencies', 'dependencies.callback', 'dependencies.error', 'dependencies.master',
        'internal', 'internal.web_crawler', 'internal.usage'
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='parse-bunny',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)