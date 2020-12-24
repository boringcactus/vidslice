import os
import sys

from cx_Freeze import setup, Executable

from vidslice import VERSION

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages=[], excludes=[])

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
if sys.platform == "win32":
    dlls_folder = os.path.join(PYTHON_INSTALL_DIR, 'DLLs')
    targets = ['libcrypto', 'libssl']
    include_files = []
    for dll in os.listdir(dlls_folder):
        for target in targets:
            if target.startswith(target):
                include_files.append(os.path.join(dlls_folder, dll))
    buildOptions['include_files'] = include_files

base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable('vidslice.py', base=base)
]

setup(name='vidslice',
      version=VERSION,
      description='',
      options=dict(build_exe=buildOptions),
      executables=executables)
