#!/bin/bash

set -e

if ! which chrome > /dev/null; then
  wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
  sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
  apt-get update && apt install -y google-chrome-stable
fi

echo '/usr/bin/google-chrome --no-sandbox --headless --disable-dev-shm-usage --disable-gpu --enable-crash-reporter --enable-logging --v=2 "$@"' > /usr/local/bin/google-chrome
chmod +x /usr/local/bin/google-chrome

# clone if it doesn't exist
ls utilitymgr || git clone https://github.com/aclowes/utilitymgr.git
cd utilitymgr

git pull
pip install -q --upgrade pip setuptools
pip install -q -r requirements.txt

mkdir -p data
python runner.py
