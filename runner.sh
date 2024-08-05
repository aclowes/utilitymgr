#!/bin/bash

set -e

# cleanup any leftover chrome instances
pkill chrome || echo "none running"
rm -rf /opt/google/chrome/chrome_debug.log

if ! which google-chrome > /dev/null; then
  # find them here: https://mirror.cs.uchicago.edu/google-chrome/pool/main/g/google-chrome-stable/
  CHROME_VERSION='114.0.5735.198-1'
  curl -O https://mirror.cs.uchicago.edu/google-chrome/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb
  apt-get update
  apt install -y ./google-chrome-stable_${CHROME_VERSION}_amd64.deb
  rm google-chrome-stable_${CHROME_VERSION}_amd64.deb
fi

echo 'exec /usr/bin/google-chrome --no-sandbox --headless --disable-dev-shm-usage --disable-gpu --enable-crash-reporter --enable-logging --v=2 "$@"' > /usr/local/bin/google-chrome
chmod +x /usr/local/bin/google-chrome

# clone if it doesn't exist
ls utilitymgr || git clone https://github.com/aclowes/utilitymgr.git
cd utilitymgr

git pull
pip install -q --upgrade pip setuptools
pip install -q -r requirements.txt

# https://googlechromelabs.github.io/chrome-for-testing/
if ! ls chromedriver > /dev/null; then
  curl -O https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip
  unzip chromedriver_linux64.zip
  rm chromedriver_linux64.zip
fi

mkdir -p data
python runner.py
