# Utility Manager

Get started:

    brew install tcl-tk
    brew install pyenv 
    env PATH="$(brew --prefix tcl-tk)/bin:$PATH" \
      LDFLAGS="-L$(brew --prefix tcl-tk)/lib" \
      CPPFLAGS="-I$(brew --prefix tcl-tk)/include" \
      PKG_CONFIG_PATH="$(brew --prefix tcl-tk)/lib/pkgconfig" \
      CFLAGS="-I$(brew --prefix tcl-tk)/include" \
      PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I$(brew --prefix tcl-tk)/include' --with-tcltk-libs='-L$(brew --prefix tcl-tk)/lib -ltcl8.6 -ltk8.6'" \
      pyenv install 3.8.6
  
    pyenv install 3.8.6    
    pyenv virtualenv 3.8.6 utilitymgr
    pyenv local utilitymgr

    curl -O https://chromedriver.storage.googleapis.com/89.0.4389.23/chromedriver_mac64.zip
    unzip chromedriver_mac64.zip
    rm chromedriver_mac64.zip
    
    pip3 install -r requirements.txt
