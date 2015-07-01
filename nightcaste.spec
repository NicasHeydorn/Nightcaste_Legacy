# -*- mode: python -*-
a = Analysis(['nightcaste.py', 'nightcaste.exe'],
             pathex=['/home/nicas/dev/nightcaste'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='nightcaste',
          debug=False,
          strip=None,
          upx=True,
          console=True )
