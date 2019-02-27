from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages=[], excludes=[])

import sys

from vidslice import VERSION

base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable('vidslice.py', base=base)
]

setup(name='vidslice',
      version=VERSION,
      description='',
      options=dict(build_exe=buildOptions),
      executables=executables)
