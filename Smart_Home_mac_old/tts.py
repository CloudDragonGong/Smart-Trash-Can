import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import ssl
from wsgiref.handlers import format_date_time
from time import mktime
import _thread as thread
import os
from pydub import AudioSegment
from pydub.playback import play
import time
from datetime import datetime

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识

file_name = 'response.mp3'

global if_right
if_right = True

class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, Text):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.Text = Text
        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"aue": "lame", "auf": "audio/L16;rate=16000", "vcn": "aisjiuxu", "tte": "utf8", "sfl": 1}
        self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-8')), "UTF8")}
        # 使用小语种须使用以下方式，此处的unicode指的是 utf16小端的编码方式，即"UTF-16LE"”
        # self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-16')), "UTF8")}

    # 生成url
    def create_url(self):
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url


# 收到websocket消息的处理
def on_message(ws, message):
    global received_audio
    global file_name
    global if_right
    try:
        message = json.loads(message)
        code = message["code"]
        sid = message["sid"]
        audio = message["data"]["audio"]
        audio = base64.b64decode(audio)
        status = message["data"]["status"]
        # print(message)
        if status == 2:
            print("ws is closed")
            ws.close()
            # 播放音频
            # play_mp3(file_name)
        if code != 0:
            errMsg = message["message"]
            if_right = False
            # print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
        else:
            if_right = True
            with open(file_name, 'ab') as f:
                f.write(audio)
                f.flush()  # 立即将数据写入文件

    except Exception as e:
        if_right = False
        print("receive msg,but parse exception:", e)



def play_mp3(file_path):
    audio = AudioSegment.from_mp3(file_path)
    play(audio)


# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws, A, B):
    print("### closed ###")


# 收到websocket连接建立的处理
def on_open(ws, wsParam):
    global file_name

    def run(*args):
        d = {"common": wsParam.CommonArgs,
             "business": wsParam.BusinessArgs,
             "data": wsParam.Data,
             }
        d = json.dumps(d)
        print("------>开始发送文本数据")
        ws.send(d)
        if os.path.exists(file_name):
            os.remove(file_name)

    thread.start_new_thread(run, ())


def transform(response, file_name_):
    global file_name
    file_name = file_name_
    # 测试时候在此处正确填写相关信息即可运行
    wsParam = Ws_Param(APPID='1eef18f8', APISecret='MTIxZmQ4MGExNmM4ODE5YjQ5ZTVmYWJj',
                       APIKey='f766dbc98966fda0aa45cf042fbcc1bd',
                       Text=response)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = lambda ws: on_open(ws, wsParam)
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


if __name__ == "__main__":
    file_name = '当前是成堆模式，没听清楚您在说什么垃圾，请再次说出您要投放的垃圾'
    file_path = file_name+'.mp3'
    time1 = datetime.now()
    transform(file_name, file_path)
    sound = AudioSegment.from_mp3(file_name)
    play(sound)
    time2 = datetime.now()
    print(time2 - time1)
