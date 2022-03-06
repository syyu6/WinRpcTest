# -*- coding:utf-8 -*-
"""
@Author: ThesYu
@File: getdnslog
@Time: 2022/3/5 23:33
@Desc: Everything is possible.
"""
import requests


def GetDNSlog():
    base_res = requests.get("http://www.dnslog.cn/getdomain.php")
    base_domain = base_res.text
    res_cookie = base_res.cookies.get_dict()
    print(base_domain, res_cookie)

def GetDNSlogRes(Cookies):
    res = requests.get("http://www.dnslog.cn/getrecords.php", cookies=Cookies)
    print(res.text)


Cookies = {'PHPSESSID': 'roj91g1frdn3r6noi9f0m2rb23'}

GetDNSlogRes(Cookies)
