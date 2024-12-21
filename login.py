# -*- coding: utf-8 -*-
import pickle
import agent
from threading import Thread
import time
import requests
from io import BytesIO
from PIL import Image
import os
import urllib3

# 禁用 HTTPS 警告
urllib3.disable_warnings()

headers = {'User-Agent': agent.get_user_agents(), 'Referer': "https://mp.weixin.qq.com/","Host": "mp.weixin.qq.com"}


class showpng(Thread):
    def __init__(self, data):
        Thread.__init__(self)
        self.data = data

    def run(self):
        img = Image.open(BytesIO(self.data)) 
        img.show()

def islogin(session):
    try:
        session.cookies.load(ignore_discard=True)
    except Exception:
        pass
    loginurl = session.get("https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=ask&token=&lang=zh_CN&f=json&ajax=1").json()
    if loginurl['base_resp']['ret'] == 0:
        print('Cookies值有效，无需扫码登录！')
        return session, True
    else:
        print('Cookies值已经失效，请重新扫码登录！')
        return session, False

def gzhlogin():
    """登录微信公众平台"""
    session = requests.Session()
    
    # 禁用代理
    session.proxies = {
        'http': None,
        'https': None
    }
    
    # 禁用 SSL 验证
    session.verify = False
    
    # 设置请求头
    session.headers = {
        'User-Agent': agent.get_user_agents(),
        'Accept': 'application/json, text/plain, */*',
    }
    
    # 写入
    if not os.path.exists('gzhcookies.cookie'):
        with open('gzhcookies.cookie', 'wb') as f:
            pickle.dump(session.cookies, f)
    # 读取
    session.cookies = pickle.load(open('gzhcookies.cookie', 'rb'))
    session, status = islogin(session)
    if not status:
        session = requests.session()
        session.get('https://mp.weixin.qq.com/', headers=headers)
        session.post('https://mp.weixin.qq.com/cgi-bin/bizlogin?action=startlogin', data='userlang=zh_CN&redirect_url=&login_type=3&sessionid={}&token=&lang=zh_CN&f=json&ajax=1'.format(int(time.time() * 1000)), headers=headers)
        loginurl = session.get('https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=getqrcode&random={}'.format(int(time.time() * 1000)))
        dateurl = 'https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=ask&token=&lang=zh_CN&f=json&ajax=1'
        t = showpng(loginurl.content)
        t.start()
        while 1:
            date = session.get(dateurl).json()
            if date['status'] == 0:
                print('二维码未失效，请扫码！')
            elif date['status'] == 6:
                print('已扫码，请确认！')
            if date['status'] == 1:
                print('已确认，登录成功！')
                url = session.post('https://mp.weixin.qq.com/cgi-bin/bizlogin?action=login', data='userlang=zh_CN&redirect_url=&cookie_forbidden=0&cookie_cleaned=1&plugin_used=0&login_type=3&token=&lang=zh_CN&f=json&ajax=1', headers=headers).json()
                session.get('https://mp.weixin.qq.com{}'.format(url['redirect_url']), headers=headers)                
                break
            time.sleep(2)
        with open('gzhcookies.cookie', 'wb') as f:
            pickle.dump(session.cookies, f)
    return session


if __name__ == '__main__':
    gzhlogin()

