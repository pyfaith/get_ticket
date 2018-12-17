#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: pyfaith
# email: pyfaith@foxmail.com
# date: 18-12-11

import os
import re
import base64
import time
import requests

from utils import showqrcode



class Login12306qrcode(object):
    '''二维码登陆12306, 获取用户cookie,并保存至文件
    setup1: 发送登录请求，用户扫描二维码登录, 获取用户的 uamtk
    setup2： 携带uamtk，进行二次验证，获取用户的apptk（真正的cookie）， "tk=" + apptk
    '''
    def __init__(self):
        self.session = requests.Session()
        self.session.proxies = {"http": "127.0.0.1:1080"}
        self.base_url = "https://kyfw.12306.cn"
        self.initmy12306api = "/otn/index/initMy12306Api"
        self.cookie = None
        self.qr_appid = "otn"
        self.qr_uuid = None
        self.file_cookie = "cookies.txt"
        self.file_qrcode = "qrcode.png"

        # 扫二维码登陆
        self.dict_qr_login = {
            "qr": "/passport/web/create-qr", #未用
            "qr64": "/passport/web/create-qr64",
            "qrcheck": "/passport/web/checkqr",
        }

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windos10; win x86_64) "\
                          "AppleWebKit/537.36 (KHTML, like Gecko) "\
                          "Chrome/70.0.3538.67 Safari/537.36",
        }

        #二次验证tk
        self.auth_passport_url = "https://kyfw.12306.cn/passport/"
        self.dict_auth = {
            'uamtk': 'web/auth/uamtk',
            "uamauthclient": "/otn/uamauthclient"
        }


    def mainloop(self):
        '''
        循环等待用户扫描登录二维码
        :return:
        '''
        # 检查本地缓存cookie是否过期
        if not self.check_local_cookie_isok:
            # 重新获取cookie
            if not self.qr_uuid:
                print("未获取到登录二维码。。。")

            '''查询是否扫码成功'''
            while True:
                rescode = self.get_check_qrcode_status
                print("请扫描二维码图片。。。。", rescode)
                if self.check_is_login(rescode):
                    '''扫码登陆成功'''
                    # 进行二次验证,并更新用户 tk cookie
                    self.auth_uamtk()
                    break
                time.sleep(5)



    @property
    def check_local_cookie_isok(self):
        '''检查本次本保存cookie是否过期'''
        if not os.path.exists(self.file_cookie):
            return False
        with open(self.file_cookie, "r") as ckf:
            self.cookie = ckf.readline().strip()
            headers = self.headers
            headers["Referer"] = "https://kyfw.12306.cn/otn/view/index.html"
            headers["cookie"] = self.cookie
            url = self.base_url + self.initmy12306api
            response = self.session.post(url, headers=headers)
            try:
                response.json()
            except Exception as e:
                print("cookie过期, 请重新扫码登陆...")

                #重新获取登录二维码
                self.get_qrcode
                return False
            else:
                print("cookie未过期。。。请尽快完成购票。")

            return True

    @property
    def get_qrcode(self):

        '''获取登陆二维码, uuid'''

        '''
        // 扫码登录-获取二维码接口
    popup_createQr: function () {
        $.ajax({
            url: popup_url.qr64,
            data: {
                appid: popup_qr_appId
            },
            type: 'POST',
            timeout: 10000,
            success: function(data) {
                if(data && data.result_code === '0' && data.image) {
                    $('#J-qrImg').attr('src', 'data:image/jpg;base64,' + data.image);

                    $('#J-login-code-loading').hide();
                    $('#J-login-code-con').show();
                    $('#J-code-error-mask').hide();
                    $('#J-code-error').hide();

                    popup_t = null
                    popup_s = -1

                    popup_t = setInterval(function () {
                        if (popup_s == '2' || popup_s == '3') {
                            clearInterval(popup_t)
                        } else {
                            // 轮询调用二维码检查接口，直至返回状态为2：登录成功，（已识别且已授权）、3：已失效
                            $.popup_checkQr(data.uuid)
                        }
                    }, 1000)

                } else {
                    // error
                }
            },
            error: function(error) {
                // error
            }
        })
    },
        :return:
        '''

        url = self.base_url + self.dict_qr_login['qr64']
        data = {"appid": self.qr_appid}


        respnose = self.session.post(url, data=data,
                                     headers=self.headers)

        data = respnose.json()

        if data['result_code']  == "0" and data["image"]:
            self.qr_uuid = data["uuid"]
            bdata = base64.b64decode(data["image"]) #bs64解码数据
            '''下载二维码登陆图片'''
            with open(self.file_qrcode, "wb") as f:
                f.write(bdata)
                f.flush()
                showqrcode.print_qr_iamge(self.file_qrcode)

    @property
    def get_check_qrcode_status(self):
        '''获取扫码结果'''
        '''
        {'result_message': '二维码状态查询成功', 'result_code': '0'}

         // 0：未识别、
        // 1：已识别，暂未授权（未点击授权或不授权）、
        // 2：登录成功，（已识别且已授权）、
        // 3：已失效、
        // 5系统异常
        '''

        url = self.base_url + self.dict_qr_login['qrcheck']
        data = {
            "uuid":  self.qr_uuid,
            "appid": self.qr_appid
        }

        response = self.session.post(url, data=data)
        data =  response.json()

        result_code = data["result_code"]
        self.cookie = response.headers.get("Set-Cookie", None) #获取用户cookie 第一次验证
        return result_code


    def check_is_login(self, rescode):
        '''检查是否登陆'''
        '''
         // 0：未识别、
        // 1：已识别，暂未授权（未点击授权或不授权）、
        // 2：登录成功，（已识别且已授权）、
        // 3：已失效、
        // 5系统异常
        '''
        # dict_data = {
        #     "0": "未识别",
        #     "1": "已识别，暂未授权（未点击授权或不授权）",
        #     "2": "登录成功，（已识别且已授权）",
        #     "3": "已失效",
        #     "5": "系统异常",
        # }

        if rescode == "2":
            self.cookie = self.session.cookies.get_dict()['uamtk'] #获取uamtk，接下来进行二次验证
            return True
        return False




    '''二次验证'''
    def auth_uamtk(self):
        '''
        二次验证,获取用户 tk cookie

        :return: user_info = {
                "username": username,
                "apptk": apptk,
                "msg": result_message
            }
        '''

        print(self.session.cookies)
        '''setup1: 获取用户的apptk'''
        url = self.auth_passport_url + self.dict_auth['uamtk']
        data = {"appid": self.qr_appid}
        response = self.session.post(url, data=data,)

        data = response.json()
        # print(data)
        apptk = data["apptk"] or data["newapptk"]



        # setup2:将TK种到自己的Cookies中
        url = self.base_url + self.dict_auth["uamauthclient"]
        data = {"tk": apptk}

        response = self.session.post(url, data=data)
        data = response.json()
        # print(data)
        #{'apptk': 'q7e1mHvo23tFZGzSxrwkhDmObW5nyHEfgB0tF_Sw4Eo27a2a0',
        # 'result_code': 0,
        # 'result_message': '验证通过',
        # 'username': 'xxx'}

        if data["result_code"] == 0:
            username = data["username"]
            apptk = data["apptk"]
            result_message = data["result_message"]
            user_info = {
                "username": username,
                "apptk": apptk,
                "msg": result_message
            }

            '''更新二次验证cookie'''
            self.cookie = "tk=" + apptk

            '''保存cookie信息'''
            if self.cookie:
                with open(self.file_cookie, "w") as ckf:
                    ckf.write(self.cookie)
                    return user_info



if __name__ == '__main__':
    login = Login12306qrcode()
    login.mainloop()