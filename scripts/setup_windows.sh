#!/usr/bin/env bash
set -x

choco install python --version 3.7.9 -y
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
echo $PATH
export PATH=/C/Python37:$PATH
which python
python get-pip.py

set +x
