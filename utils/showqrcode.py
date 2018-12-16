#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: pyfaith
# email: pyfaith@foxmail.com
# date: 18-10-14

import os, sys, platform, subprocess




OS_TYPE = platform.system() # Windows, Linux, Darwin




def print_qr_iamge(file_dir):
    '''
    使用系统自带图片浏览器打开图片
    :param file_dir: 图片地址
    :return:None
    '''
    if OS_TYPE == 'Darwin': #mac
        subprocess.call(['open', file_dir])
    elif OS_TYPE == 'Linux': #linux
        subprocess.call(['xdg-open', file_dir])
    else: #windows?
        os.startfile(file_dir)







def test():
    print_qr_iamge("../12306_qrcode.png")


if __name__ == '__main__':
    test()