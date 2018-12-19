# -*- mode: python -*-


block_cipher = None


added_files = []

import os
def traverseDirByOSWalk(path):
    path = os.path.expanduser(path)
    for (dirname, subdir, subfile) in os.walk(path):
        for f in subfile:
            file_path = os.path.join(dirname, f)
            added_files.append((file_path, '/'.join(file_path.split('/')[:-1])))

rootdir = "FlaskWeb/app/static"
traverseDirByOSWalk(rootdir)
templatedir = "FlaskWeb/app/templates"
traverseDirByOSWalk(templatedir)

a = Analysis(['FlaskWeb/StartServer.py'],
             pathex=['/data/running/dev3x'],
             binaries=None,
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='StartServer',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='StartServer')