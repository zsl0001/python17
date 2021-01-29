# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew
from kivy.tools.packaging.pyinstaller_hooks import get_deps_minimal, get_deps_all, hookspath, runtime_hooks

block_cipher = None


a = Analysis(['touchtracer\\main.py'],
             pathex=['F:\\pyproject\\kv-demo\\第6章\\1\\4'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=hookspath(),
             runtime_hooks=runtime_hooks(),
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False,
             **get_deps_all())
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='touchtracer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe, Tree('touchtracer'),
               a.binaries,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=True,
               name='touchtracer')
