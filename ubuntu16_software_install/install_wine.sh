#!/usr/bin/env bash

set -e
set -x

# support x86 for x64 machine
sudo dpkg --add-architecture i386

wget -nc https://dl.winehq.org/wine-builds/Release.key 

sudo apt-key add Release.key 
sudo apt-add-repository https://dl.winehq.org/wine-builds/ubuntu/ 

sudo apt-get update 
sudo apt-get install –install-recommends winehq-stable 
