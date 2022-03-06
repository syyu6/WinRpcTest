# -*- coding:utf-8 -*-
"""
@Author: ThesYu
@File: getdnslog_dig
@Time: 2022/3/5 23:33
@Desc: Everything is possible.
"""
import requests
import json

def GetDNSlog():
    base_res = requests.post("https://dig.pm/new_gen",data="domain=dns.1433.eu.org.").text
    base_domain, res_token = json.loads(base_res)['domain'], json.loads(base_res)['token']
    print(base_domain, res_token)


def GetDNSlogRes(base_domain,res_token):
    datas = {
        'domain': base_domain,
        'token': res_token
    }
    res = requests.post("https://dig.pm/get_results", data=datas)
    # print(res.text)

    res_json = json.loads(res.text)
    for i in res_json:
        ip_temp = str(res_json[i]['subdomain']).split(".")
        del ip_temp[-6:]
        ip = ".".join(ip_temp)
        print(ip)



# GetDNSlog()
# GetDNSlogRes("6ce17c7d.dns.1433.eu.org.", "34rp5xxo88vx")
GetDNSlogRes("0983dc45.dns.1433.eu.org.", "j475zobt6d2u")

# GetDNSlogRes(Cookies)
