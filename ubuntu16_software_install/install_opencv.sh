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

# compile and install opencv
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
    -D PYTHON_EXECUTABLE=/usr/bin/python \
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

