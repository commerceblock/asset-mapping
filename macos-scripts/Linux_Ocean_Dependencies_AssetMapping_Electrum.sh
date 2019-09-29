#!/bin/bash

#Ocean
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew install git python python3 amap automake berkeley-db4 libtool boost miniupnpc openssl pkg-config protobuf qt5 libevent autoconf openssl
cd $HOME
git clone https://github.com/goldtokensa/dependencies.git
cd dependencies
pip3 install -r boto3/requirements.txt -e boto3 -e python-mnemonic -e datadiff-2.0.0 -e pybitcointools -e requests
cd $HOME
git clone https://github.com/commerceblock/ocean.git
cd /ocean
./autogen.sh
./configure
Make
make -j4

#Asset-Mapping
cd $HOME
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
git clone https://github.com/commerceblock/asset-mapping.git
cd asset-mapping
python setup.py install
ln -s $HOME/asset-mapping/macos-scripts/DGLD_Command_Centre.command /$HOME/Desktop

#CB Electrum Wallet
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew install qt5 pyqt5 gettext pip3 python3 python3-pip
cd $HOME
git clone https://github.com/commerceblock/cb-client-wallet.git
cd cb-client-wallet
pip3 install .[fast]
pyrcc5 icons.qrc -o electrum/gui/qt/icons_rc.py
./electrum-env
./run_electrum
