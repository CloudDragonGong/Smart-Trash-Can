#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
import urllib.request
import urllib.parse
import json
import hashlib
import base64
#接口地址
url ="http://ltpapi.xfyun.cn/v1/ke"
#开放平台应用ID
x_appid = "0c946150"
#开放平台应用接口秘钥
api_key = "dd56dd6e1b3116009b5f819274539c8f"
#语言文本
TEXT="我要取出其他垃圾桶"


def extract_keywords(text):
    body = urllib.parse.urlencode({'text': text}).encode('utf-8')
    param = {"type": "dependent"}
    x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode('utf-8'))
    x_time = str(int(time.time()))
    x_checksum = hashlib.md5(api_key.encode('utf-8') + str(x_time).encode('utf-8') + x_param).hexdigest()
    x_header = {'X-Appid': x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum}
    req = urllib.request.Request(url, body, x_header)
    result = urllib.request.urlopen(req)
    result = result.read()
    print(result.decode('utf-8'))
    word_array = [item["word"] for item in json.loads(result.decode('utf-8'))["data"]["ke"]]
    return  word_array


if __name__ == '__main__':
    print(extract_keywords(TEXT))
