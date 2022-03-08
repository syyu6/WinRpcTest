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


def banner():
    pass

def GetDNSlog():
    base_res = requests.post("https://dig.pm/new_gen",data="domain=dns.1433.eu.org.",timeout=5).text
    base_domain, res_token = json.loads(base_res)['domain'], json.loads(base_res)['token']
    print("[+] GetDNSlogInfo:", base_domain, res_token, '\n')
    return base_domain, res_token


def GetDNSlogRes(base_domain,res_token):
    datas = {
        'domain': base_domain,
        'token': res_token
    }
    try:
        res = requests.post("https://dig.pm/get_results", data=datas,timeout=5)
        res_json = json.loads(res.text)

        if res_json:
            ips = []
            print("\n[+] successful ips: \n")
            for i in res_json:
                ip_temp = str(res_json[i]['subdomain']).split(".")
                del ip_temp[-6:]
                ip = ".".join(ip_temp)
                if ip not in ips:
                    ips.append(ip)
            [print(x) for x in ips]
            if args.output:
                with open(args.output,"w") as op:
                    op.write("\n".join(ips))
            print()
        else:
            print("\n[x] Ips all False!\n")
    except:
        pass


def Dce_IpsFile(filename, domain, username, password, hashes):
    ips = open(filename,"r").readlines()
    for ip in ips:
        Dce_ip(ip.strip(), domain, username, password, hashes)

def Dce_ip(ip, domain ,username, password, hashes):
    global base_domain

    if domain is None:
        domain = ''

    lmhash = ''
    nthash = ''
    if (password is None) & (hashes is None):
        exit("[x] Missing password OR hashes!")

    if hashes is not None:
        try:
            lmhash, nthash = hashes.split(':')
            if (len(lmhash) != 32) & (len(nthash) != 32):
                exit("[x] Hashes Length Error!")
            elif (lmhash is None) | (len(nthash) == 32):
                pass
            elif (nthash is None) | (len(lmhash) == 32):
                pass
            else:
                exit("[x] Hashes Type Error!")

        except:
            exit("[x] Hashes Type Error!")


    ncacn_np = rf'ncacn_np:{ip}[\pipe\spoolss]'
    rpctransport = transport.DCERPCTransportFactory(ncacn_np)

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
        if "LOGON_FAILURE" in str(err):
            print("[-] " + str(ip).ljust(15), "-> ", "LOGON_FAILURE!")
        elif "OBJECT_NAME_NOT_FOUND" in str(err):
            print("[-] " + str(ip).ljust(15), "-> ", "OBJECT_NAME_NOT_FOUND!")
        elif "timed out" in str(err):
            print("[-] " + str(ip).ljust(15), "-> ", "Connection Timeout!")
        elif "getaddrinfo failed" in str(err):
            print("[-] " + str(ip).ljust(15), "-> ", "Wrong IP Address!")
        elif "0x709" in str(err):
            print("[+] " + str(ip).ljust(15), "-> ", "Internet Accessible !!!")
        else:
            print("[-] " + str(ip).ljust(15), "-> ", "Internet Inaccessible.")

if __name__ == '__main__':
    base_domain, res_token = "", ""
    parser = argparse.ArgumentParser(description="Win RPC test")
    parser.add_argument('--target', '-t', type=str, help='TargetIP')
    parser.add_argument('--file', '-f', type=str, help='TargetIpsFile')
    parser.add_argument('--domain', '-d', action="store", type=str, help='Specify domain')
    parser.add_argument('--username', '-u', required=True, type=str, help='UserName')
    parser.add_argument('--password', '-p', action="store", type=str,help='PassWord')
    parser.add_argument('--hashes', '-H', action="store", default=None ,metavar = "LMHASH:NTHASH", help='NTLM hashes, format is LMHASH:NTHASH')
    parser.add_argument('--output', '-o', type=str, help='output')

    args = parser.parse_args()

    if (args.target != None) | (args.file != None):
        try:
            base_domain, res_token = GetDNSlog()
        except:
            exit("[x] get DNSlog domain fail！")

    if args.target:
        Dce_ip(args.target, args.domain , args.username, args.password, args.hashes)
        GetDNSlogRes(base_domain, res_token)

    elif args.file:
        Dce_IpsFile(args.file, args.domain, args.username, args.password, args.hashes)
        GetDNSlogRes(base_domain, res_token)

    else:
        print("[x] Missing Parameters！")
        print("eg: \n\tpython3 WinRPCtest.py -t 192.168.101.10 -u administrator -p admin123")
        print("\tpython3 WinRPCtest.py -f ips.txt -u administrator -p admin123")
        print("\tpython3 WinRpcTest.py -f test.lst -d test.com -u administrator -H e91d2eafde47de62c6c49a012b3a6af1:e91d2eafde47de62c6c49a012b3a6af1")
