#!/bin/bash

set -x
set -e

sudo apt update

# install developer tools
sudo apt install -fy build-essential cmake unzip pkg-config

# install OpenCV-specific prerequisites
sudo apt install -fy libjpeg-dev libpng-dev libtiff-dev

# install video I/O packages
sudo apt install -fy libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev

# install GTK for highgui module
sudo apt install -fy libgtk-3-dev

# install optimizations
sudo apt install -fy libatlas-base-dev gfortran

cd ~/Downloads

install pip and virtual environments
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

# create a virtual env for cv
mkvirtualenv cv -p python
# change to cv env
workon cv

# install python packages
pip install numpy 

# compile and install opencv
download opencv source code
wget -O opencv.zip https://github.com/opencv/opencv/archive/3.4.1.zip
wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/3.4.1.zip
unzip opencv.zip
unzip opencv_contrib.zip

cd ./opencv-3.4.1/
rm -rf build
mkdir build
cd build
workon cv
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D INSTALL_C_EXAMPLES=ON \
    -D OPENCV_EXTRA_MODULES_PATH=~/Downloads/opencv_contrib-3.4.1/modules \
    -D PYTHON_EXECUTABLE=~/.virtualenvs/cv/bin/python \
    -D BUILD_EXAMPLES=ON ..

make -j4
sudo make install

# add python package in virtual env
sudo sh -c 'echo "/usr/local/lib" >> /etc/ld.so.conf.d/opencv.conf'
cd ~/.virtualenvs/cv/lib/python2.7/site-packages/
ln -s /usr/local/lib/python2.7/site-packages/cv2.so cv2.so
sudo ldconfig

# clean
cd ~/Downloads
rm -rf opencv.zip opencv_contrib.zip opencv-3.4.1 opencv_contrib-3.4.1

