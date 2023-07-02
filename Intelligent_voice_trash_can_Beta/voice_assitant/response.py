from . import stt
from . import tts
from . import prompt

# import stt
# import tts
# import prompt

import time
import re

# def voice_reply(speech):
#     global response
#     mode = 0
#     city = ""
#     t = time.localtime()
#     print(speech)
#     if str.find(speech, "小科"):
#         print("in the wakeup")
#         if str.find(speech, "垃圾分类"):
#             # 执行垃圾分类程序，分类完成告诉垃圾的种类、数量，然后询问是否需要帮助，满载的时候进行提醒
#             response = "好的，正在进行垃圾分类。[p100]"               
#         elif str.find(speech,"天气") or str.find(speech,"气温") or mode == 1:
#             # 接入查询天气的接口
#             if mode != 1:
#                 response = "好的，请您告诉我需要查询的城市。[p100]"
#                 mode = 1
#             else:
#                 # 查询某个城市的天气
#                 city = speech
#                 mode = 0
#         elif str.find(speech,"日期"):
#             # 返回现在日期
#             response = "今天是" + str(t.tm_year) + "年" + str(t.tm_mon) + "月" + str(t.tm_mday) + "日。[p100]"
#         elif str.find(speech,"时间"):
#             # 返回时间
#             response = "现在是北京时间" + str(t.tm_hour) + "点" + str(t.tm_min) + "分" + str(t.tm_sec) + "秒。[p100]"
#         elif str.find(speech,"聊天"):
#             # 接入chatgpt的接口
#             # 实验人工聊天
#             if str.find(speech,"有害垃圾的种类"):
#                 response = "有害垃圾包括废电池、废灯管、废药品、废油漆、废杀虫剂等。[p100]"
#             elif str.find(speech,"可回收垃圾的种类"):
#                 response = "可回收垃圾包括废纸张、废塑料、废玻璃、废金属、废织物等。[p100]"
#             elif str.find(speech,"厨余垃圾的种类"):
#                 response = "厨余垃圾包括剩菜剩饭、果皮、蛋壳、茶渣、骨头等。[p100]"
#             elif str.find(speech,"其他垃圾的种类"):
#                 response = "其他垃圾包括砖瓦陶瓷、渣土、卫生间废纸、烟蒂等。[p100]"
#             elif str.find(speech,"退出")or str.find(speech,"结束"):
#                 response = "再见，祝您生活愉快！[p100]"
#             else:
#                 response = "请问您有什么问题要问我的。[p100]"
#         else:
#             response = "在的，请问我能帮助您什么吗？我可以进行垃圾分类、天气查询、时间查询等功能，还能陪您聊天哦！[p100]"
#     else:
#         response = ""
#     return response
# "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"

# for voiceAssistant.py
# 调用chatgpt，生成回答文字
def voice_reply(speech,gpt_key,information):
    if information==None:
        print('information error')
        exit()
    # information = {'harmful_garbage':1,'kitchen_waste':2,'recyclable_garbage':3,'other_garbage':4}
    gpt = prompt.ChatGPT(gpt_key,information=information)
    return gpt.get_response(speech)


# chatgpt生成文字
def excute(voice_address,gpt_key,information):
    speech = stt.transform(voice_address)
    response = voice_reply(speech=speech,gpt_key=gpt_key,information=information)
    response+='[p100]'
    print(response)
    tts.transform(response=response)


if __name__ == "__main__":
    excute(voice_address=r'./recording.mp3',gpt_key="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")
