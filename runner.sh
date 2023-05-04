#!/bin/bash

set -e

# cleanup any leftover chrome instances
pkill chrome || echo "none running"
rm -rf /opt/google/chrome/chrome_debug.log

if ! which google-chrome > /dev/null; then
  wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
  sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
  apt-get update && apt install -y google-chrome-stable
fi

echo 'exec /usr/bin/google-chrome --no-sandbox --headless --disable-dev-shm-usage --disable-gpu --enable-crash-reporter --enable-logging --v=2 "$@"' > /usr/local/bin/google-chrome
chmod +x /usr/local/bin/google-chrome

# clone if it doesn't exist
ls utilitymgr || git clone https://github.com/aclowes/utilitymgr.git
cd utilitymgr

git pull
pip install -q --upgrade pip setuptools
pip install -q -r requirements.txt

if ! ls chromedriver > /dev/null; then
  curl -O https://chromedriver.storage.googleapis.com/113.0.5672.63/chromedriver_linux64.zip
  unzip chromedriver_linux64.zip
  rm chromedriver_linux64.zip
fi

mkdir -p data
python runner.py
