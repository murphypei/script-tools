#!/usr/bin/env bash

set -e
set -x

sudo mv /etc/apt/source.list /etc/apt/source.list.bak

sudo cp ./source.list /etc/apt/source.list

sudo apt update

sudo apt -y install build-essential 
sudo apt -y install git 
sudo apt -y install wget 
sudo apt -y install openssh-server openssh-client 
sudo apt -y install tmux 
sudo apt -y install curl 
sudo apt -y install supervisor 
sudo apt -y install lrzsz 
sudo apt -y install libxml2-dev 
sudo apt -y install pkg-config libssl-dev libsslcommon2-dev 
sudo apt -y install libbz2-dev 
sudo apt -y install libcurl4-gnutls-dev 
sudo apt -y install libjpeg8-dev 
sudo apt -y install libpng-dev 
sudo apt -y install libfreetype6-dev 
sudo apt -y install libmcrypt-dev 
sudo apt -y install libxslt-dev 
sudo apt -y install libgmp-dev 
sudo apt -y install libreadline-dev

# screen-shot
echo "\n" | sudo add-apt-repository ppa:shutter/ppa
sudo apt-get install shutter