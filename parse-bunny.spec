# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path
from PyInstaller.utils.hooks import copy_metadata

block_cipher = None

# Base project path
base_path = Path(".").resolve()

a = Analysis(
    ['main.py'],
    pathex=[str(base_path)],
    binaries=[],
    datas=[
        ('key.bin', '.'),
        ('commands/config.json', 'commands'),
        ('secure_setup.py', '.'),
        ('commands', 'commands'),
        ('syntax', 'syntax'),
        ('environments', 'environments'),
        ('dependencies', 'dependencies'),
        ('internal', 'internal'),
        ('C:/parse-bunny/dashboard/creds/service_account.json', 'creds'),  # relative now
    ],
    hiddenimports=[
        # core stdlib
        'json', 'datetime', 'os', 'sys', 're', 'pathlib', 'pkgutil',

        # internal project
        'commands', 'commands.command', 'commands.base', 'commands.parsing',
        'secure_setup',
        'syntax', 'syntax.lexer', 'syntax.parser', 'syntax.interface', 'syntax.types',
        'environments', 'environments.piping',
        'dependencies', 'dependencies.callback', 'dependencies.error', 'dependencies.master',
        'internal', 'internal.web_crawler', 'internal.usage',
        
        # Cryptography
        'cryptography',
        'cryptography.fernet',
        'cryptography.hazmat.backends',
        'cryptography.hazmat.backends.openssl',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.primitives.asymmetric',
        'cryptography.hazmat.primitives.ciphers',
        'cryptography.hazmat.primitives.hashes',
        'cryptography.hazmat.primitives.kdf',
        'cryptography.hazmat.primitives.kdf.pbkdf2',
        'cryptography.x509',

        # HTTP
        'requests'
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
    console=True
)
