#!/usr/bin/env bash
set -x

choco install python
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
echo $PATH
export PATH=/C/Python37:$PATH
which python
python get-pip.py
python -m pip install --upgrade git+https://github.com/anthony-tuininga/cx_Freeze.git@master

set +x
