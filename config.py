#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: pyfaith
# email: pyfaith@foxmail.com
# date: 18-12-15
import os
import codecs

from urllib import request



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

load_city_code = load_city_code() #使用单例


# 加载席别编码
load_seat_map = {
            "硬座" : "1",
            "硬卧" : "3",
            "软卧" : "4",
            "一等软座" : "7",
            "二等软座" : "8",
            "商务座" : "9",
            "一等座" : "M",
            "二等座" : "O",
            "混编硬座" : "B",
            "特等座" : "P"
        }


# 车次类型选择
load_train_type_dict = {'T': 'T-特快',           # 特快
                    'G': 'GC-高铁/城际',         # 高铁
                    'D': 'D-动车',               # 动车
                    'Z': 'Z-直达',               # 直达
                    'K': 'K-快速'                # 快速
                    }


def proxy_support():
    '''
    获取代理ip
    :return: {"http": "ip_port", "https": "ip_port"}
    '''
    url = "http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?" \
          "spiderId=87394e1ace824820a92e01bd918b849e&" \
          "orderno=YZ2018914679TSpRLu&returnType=1&count=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windos10; win x86_64) "\
        "AppleWebKit/537.36 (KHTML, like Gecko) "\
        "Chrome/70.0.3538.67 Safari/537.36",
    }
    req = request.Request(url, headers=headers)
    with request.urlopen(req) as res:
        data = res.read().decode("utf-8").strip()
        with codecs.open("proxy.txt", "w") as f:
            f.write(data + "\n")
        proxy_dict = {"http": data, "https": data}
        return proxy_dict



__all__ = ["load_city_code", "load_seat_map",
           "load_train_type_dict", "proxy_support",]

