#!/usr/bin/env bash
set -x

choco install python
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
echo $PATH
export PATH=/C/Python37:$PATH
which python
python get-pip.py
curl https://download.lfd.uci.edu/pythonlibs/u2hcgva4/cx_Freeze-5.1.1-cp37-cp37m-win_amd64.whl -o cx_Freeze.whl
python -m pip install cx_Freeze.whl
