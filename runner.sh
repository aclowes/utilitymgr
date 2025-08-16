#!/bin/bash

set -e

# cleanup any leftover chrome instances
pkill chrome || echo "none running"

if ! which google-chrome > /dev/null; then
  curl -O https://storage.googleapis.com/chrome-for-testing-public/138.0.7204.157/linux64/chrome-linux64.zip
  unzip chrome-linux64.zip
  apt-get update
  while read -r pkg; do
    apt-get satisfy -y --no-install-recommends "${pkg}"
  done < chrome-linux64/deb.deps
  rm chrome-linux64.zip
fi

echo "exec $PWD/chrome-linux64/chrome --no-sandbox --headless --window-size=1920,1080 --disable-dev-shm-usage \"\$@\"" > /usr/local/bin/google-chrome
chmod +x /usr/local/bin/google-chrome

# clone if it doesn't exist
ls utilitymgr || git clone https://github.com/aclowes/utilitymgr.git
cd utilitymgr

git pull
pip install -q --upgrade pip setuptools
pip install -q -r requirements.txt

# https://googlechromelabs.github.io/chrome-for-testing/
if ! ls chromedriver > /dev/null; then
  curl -O https://storage.googleapis.com/chrome-for-testing-public/138.0.7204.157/linux64/chromedriver-linux64.zip
  unzip chromedriver-linux64.zip
  mv chromedriver-linux64/chromedriver .
  rm -r chromedriver-linux64.zip chromedriver-linux64
fi

mkdir -p data
python runner.py
