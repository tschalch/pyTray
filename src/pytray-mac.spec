# -*- mode: python -*-
a = Analysis(['pytray.py'],
             pathex=['/Users/schalch/_Programming/pyTray/src'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='pytray',
          debug=False,
          strip=None,
          upx=True,
          console=False , icon='files/images/icon-windowed.icns')
files = Tree('files', prefix='files', excludes=['.git'])
coll = COLLECT(exe,
               a.binaries,
	       files,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='pytray')
app = BUNDLE(coll,
             name='pytray.app',
             icon='files/images/icon-windowed.icns')
