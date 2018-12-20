#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: pyfaith
# email: pyfaith@foxmail.com
# date: 18-12-20

import os
import platform
import sys
import subprocess
import configparser
import base64
import time
import requests


class QRLogin(object):
    '''抢票'''

    def __init__(self, proxy_ip="183.154.55.41:48187"):
        self.session = requests.Session()
        self.uuid = None
        # 代理
        self.proxy_support = {} if not proxy_ip else {"http", proxy_ip, "https", proxy_ip}
        self.proxy_support = {'http': 'socks5://127.0.0.1:1080','https': 'socks5://127.0.0.1:1080'}
        self.read_config()


    def main_loop(self):
        '''
        轮训验证二维码登录
        :return:
        '''
        self.get_qrcode()
        while True:
            if self.check_qrcode_login_success:
                self.get_auth_cookie()
                break
            time.sleep(5)

    def read_config(self,config_file='config.ini'):
        '''
        加载匹配
        :param config_file:
        :return:
        '''
        print("加载配置文件...")
        # 补充文件路径，获得config.ini的绝对路径，默认为主程序当前目录
        path = os.path.join(os.getcwd(), config_file)
        cp = configparser.ConfigParser()
        try:
            # 指定读取config.ini编码格式，防止中文乱码（兼容windows）
            cp.read(path, encoding="utf-8")
        except IOError as e:
            print(u'打开配置文件"%s"失败, 请先创建或者拷贝一份配置文件config.ini' % (config_file))
            input('Press any key to continue')
            sys.exit()
        self.user_agent = cp.get("urlInfo", "user_agent")
        self.login_url_qr64 = cp.get("urlInfo", "login_url_qr64")
        self.login_url_checkqr = cp.get("urlInfo", "login_url_checkqr")
        self.login_url_auth = cp.get("urlInfo", "login_url_auth")
        self.login_url_uamauthclient = cp.get("urlInfo", "login_url_uamauthclient")
        self.login_headers = {
            "User-Agent": self.user_agent,
            "Origin": "https://kyfw.12306.cn",
            "Referer": "https://kyfw.12306.cn/otn/resources/login.html",
            "X-Requested-With": "XMLHttpRequest",
        }


    def get_qrcode(self):
        '''
        下载二维码
        :return:
        '''
        data = {
            "appid": "otn",
        }

        # self.session.get("https://kyfw.12306.cn/otn/resources/login.html",headers=headers)
        res = self.session.post(self.login_url_qr64, headers=self.login_headers,
                                data=data, proxies=self.proxy_support)
        data = res.json()
        if data.get("result_code") == "0":
            self.uuid = data.get("uuid")
            # 下载二维码
            image_data = base64.b64decode(data.get("image"))
            with open("qrcode.png", "wb") as f:
                f.write(image_data)
                f.flush()
            self.show_qrcode("qrcode.png")

    @property
    def check_qrcode_login_success(self):
        '''
        查看二维码扫描状态
        :return: bool
        '''
        data = {
            "uuid": self.uuid,
            "appid": "otn",
        }
        res = self.session.post(self.login_url_checkqr, data=data, headers=self.login_headers)
        data = res.json()
        if data.get("result_code") == "2":
            print("登录成功")
            print(res.cookies.get_dict())
            self.uamtk =res.get_dict().get("uamtk") #获取uamtk
            return True
        else:
            print("请扫描二维码登录系统：", data.get("result_message"))

    def get_auth_cookie(self):
        '''
        获取登录成功后的cookie
        :return:
        '''
        data = {
            "appid": "otn",
            "uamtk":self.uamtk,
        }
        res1 = self.session.post(self.login_url_auth, data=data, headers=self.login_headers)
        _data = res1.json()
        apptk = _data.get("apptk") or _data.get("newapptk")

        data = {"tk": apptk}
        res2 = self.session.post(self.login_url_uamauthclient, data=data, headers=self.login_headers)
        # {'apptk': 'q7e1mHvo23tFZGzSxrwkhDmObW5nyHEfgB0tF_Sw4Eo27a2a0',
        # 'result_code': 0,
        # 'result_message': '验证通过',
        # 'username': 'xxx'}

        #保存cookie信息
        with open("cookie.txt", "rb", encoding="utf-8") as f:
            f.write(res2.headers["cookie"])
            f.flush()






    def show_qrcode(self, file_dir):
        '''
        显示二维码
        :return:
        '''
        OS_TYPE = platform.system()  # Windows, Linux, Darwin
        if OS_TYPE == 'Darwin':  # mac
            subprocess.call(['open', file_dir])
        elif OS_TYPE == 'Linux':  # linux
            subprocess.call(['xdg-open', file_dir])
        else:  # windows?
            os.startfile(file_dir)


if __name__ == '__main__':
    t= Ticket()
    t.main_loop()
