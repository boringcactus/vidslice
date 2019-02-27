import os
import sys

from cx_Freeze import setup, Executable

from vidslice import VERSION

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages=[], excludes=[])

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
if sys.platform == "win32":
    buildOptions['include_files'] = [
        os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'libcrypto-1_1-x64.dll'),
        os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'libssl-1_1-x64.dll'),
    ]

base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable('vidslice.py', base=base)
]

setup(name='vidslice',
      version=VERSION,
      description='',
      options=dict(build_exe=buildOptions),
      executables=executables)
