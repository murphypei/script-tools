#!/bin/bash

set -x
set -e

SHELL_DIR="$( cd "$(dirname "$0")" && pwd)"

sudo apt update

cd ~/Downloads

wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
sudo pip install virtualenv virtualenvwrapper
sudo rm -rf ./get-pip.py ~/.cache/pip

# config virtual envs
echo -e "\n# virtualenv and virtualenvwrapper" >> ~/.bashrc
echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.bashrc
echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python" >> ~/.bashrc
echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc

export VIRTUALENVWRAPPER_PYTHON=`which python`
source `which virtualenvwrapper.sh`
source ~/.bashrc 


mkvirtualenv py2 -p /usr/bin/python2
workon cv
pip install -i http://pypi.douban.com/simple/ --trusted-host=pypi.douban.com/simple -r ${SHELL_DIR}/requirements.txt 



