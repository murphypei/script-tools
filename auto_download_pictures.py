#! -*- coding: utf-8 -*-

''' automatic download, rename and save pictures from Internet for blog writing'''

from __future__ import print_function

import urllib2
import os
import sys

pic_formats = set(["png", "jpg"])


def random_string(n=10):
    return (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(n))))[0:16]


def main(pic_url, save_dir):
    name = pic_url.split('/')[-1]
    format = name.split('.')[-1]

    if format in pic_formats:
        response = urllib2.urlopen(pic_url)
        pic_rw = response.read()
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        dst_pic = '/'.join([save_dir, random_string() + '.' + format])
        print(dst_pic)
        with open(dst_pic, 'wb') as f:
            f.write(pic_rw)
        return dst_pic
    else:
        print("Undefined format")


if __name__ == "__main__":
    dir_path = sys.argv[1]
    pic_url = sys.argv[2]
    dst_pic = main(pic_url, dir_path)
    print(dst_pic)
