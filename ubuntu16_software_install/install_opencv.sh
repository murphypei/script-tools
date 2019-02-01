#!/usr/bin/env bash

set -x
set -e

OPENCV_VERSION="3.4.1"
OPERATION_DIR=~/tmp
PYTHON_BIN_PATH=$(which python)
APT_UPDATE=false
DOWNLOAD=false

if [ "$APT_UPDATE" = true ] ; then
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
fi

if [[ ! -d ${OPERATION_DIR} ]]; then
    mkdir -p ${OPERATION_DIR}
fi
cd ${OPERATION_DIR}

if [[ "$DOWNLOAD" = true ]] ; then
    # compile and install opencv
    wget -O opencv.zip https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.zip
    wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/${OPENCV_VERSION}.zip
    unzip opencv.zip
    unzip opencv_contrib.zip
fi

cd ./opencv-${OPENCV_VERSION}/
rm -rf build
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D INSTALL_C_EXAMPLES=ON \
    -D OPENCV_EXTRA_MODULES_PATH=${OPERATION_DIR}/opencv_contrib-${OPENCV_VERSION}/modules \
    -D PYTHON_EXECUTABLE=${PYTHON_BIN_PATH} \
    -D BUILD_EXAMPLES=ON ..

make -j4
sudo make install

# add python package in virtual env
# sudo sh -c 'echo "/usr/local/lib" >> /etc/ld.so.conf.d/opencv.conf'
# cd ~/.virtualenvs/cv/lib/python2.7/site-packages/
# ln -s /usr/local/lib/python2.7/site-packages/cv2.so cv2.so
# sudo ldconfig

# clean
cd ${OPERATION_DIR}
rm -rf opencv.zip opencv_contrib.zip opencv-3.4.1 opencv_contrib-3.4.1

