#!/bin/bash

set -e

# clone if it doesn't exist
ls utilitymgr || git clone https://github.com/aclowes/utilitymgr.git

cd utilitymgr
git pull

pip install -q --upgrade pip setuptools
pip install -q -r requirements.txt

mkdir -p data
python runner.py
