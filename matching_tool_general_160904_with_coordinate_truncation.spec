# -*- mode: python -*-

block_cipher = None


a = Analysis(['/home/sf/Downloads/matching_tool_general_160904_with_coordinate_truncation.py'],
             pathex=['/home/sf/chgis'],
             binaries=None,
             datas=None,
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
          name='matching_tool_general_160904_with_coordinate_truncation',
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
               name='matching_tool_general_160904_with_coordinate_truncation')
