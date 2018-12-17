#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: pyfaith
# email: pyfaith@foxmail.com
# date: 18-12-15
import os
import codecs

def load_city_code():
    '''
    加载映射文件，并将中文"武汉"转换成编码后的格式：“武汉,WHN“
    :param :
    :return:
    '''
    print("映射出发地、目的地...")
    city_codes = {}
    path = os.path.join(os.getcwd(), 'city_code.txt')
    with codecs.open(path, "r", "utf-8") as f:
        for l in f.readlines():
            city = l.split(':')[0]
            code = l.split(':')[1].strip()
            city_codes[city] = city + "," + code
            # print(city_codes)
            # {'克拉玛依': '克拉玛依,KHR'}
    return city_codes

