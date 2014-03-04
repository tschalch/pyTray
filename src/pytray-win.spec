# -*- mode: python -*-
a = Analysis(['pytray.py'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          #[('v', None, 'OPTION'),('W ignore', None, 'OPTION')],
          exclude_binaries=True,
          name='pytray.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True,
          windowed=True,
          icon='files/images/icon.ico'
          )
files = Tree('files', prefix='files', excludes=['.git'])
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               files,
               strip=None,
               upx=True,
               name='pytray')
