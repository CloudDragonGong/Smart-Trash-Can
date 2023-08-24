import os
import time

import openai.error

from model import Model
from socket_server import Server
import stt
import tts
from Web_extract_keywords import extract_keywords


class ProcessChat:
    def __init__(self, ip, port):
        self.data = {
            'full_load': [False, False, False, False],
            'number_of_launch': [0, 0, 0, 0]
        }
        self.server = Server(ip, port)
        self.garbage_type = None
        self.receive_mp3_path = r'voice/receive_mp3.mp3'
        self.mode_type_2_mode = {
            '分类模式': 0,
            '成堆投放模式': 1,
            '取垃圾桶模式': 2,
            '聊天模式': 3
        }
        self.receive_again_mp3_path = r'voice/receive_again_mp3.mp3'
        self.answer_mp3_path = r'voice/answer_mp3.mp3'
        pass

    def classify(self, text):

        # text_keywords = extract_keywords(text)
        model = Model()
        input = f"""
        提取出{text}里的垃圾(物品)种类，然后进行分类/
        分类为1.可回收垃圾 2.有害垃圾 3.其他垃圾 4.厨余垃圾 中的一种/
        不用解释原因，直接回答类别
        """
        garbage_type_str = model.response(input)
        keywords_ = {
            "可回收垃圾": "可回收垃圾",
            "有害垃圾": "有害垃圾",
            "其他垃圾": "其他垃圾",
            "厨余垃圾": "厨余垃圾"
        }

        for keyword, category in keywords_.items():
            if keyword in garbage_type_str:
                return category

        return None

    def classify_can_name(self,text):
        keywords_ = {
            "可回收": "可回收垃圾",
            "有害": "有害垃圾",
            "其他": "其他垃圾",
            "厨余": "厨余垃圾",
            '厨房': "厨余垃圾"
        }
        for keyword, category in keywords_.items():
            if keyword in text:
                return category
        return None

    def match_mode(self, input_text):
        prompt = f"你需要将接下来对话的模式分类，分为：1.分类模式（用户请求你将少量的垃圾进行分类），2.成堆投放（连续投放）模式，3.取垃圾桶模式（就是用户明确想请求把垃圾桶取出来然后倒掉里面的垃圾，清空里面的垃圾）4"
        ".聊天模式（不是上面3"
        "种模式的话就是聊天模式，就是除了上面三种模式，其余的就是聊天模式，用户可能会和你闲聊，用户可能还会询问你一些垃圾桶系统的一些状况，例如垃圾桶的满载情况，哪个垃圾桶装满了？0或者投放频率啥的，你就返回聊天模式）"
        model = Model(prompt)
        return model.response(input_text)

    def mode_classify(self, text):
        text_keywords = extract_keywords(text)

        mode_type = self.match_mode(text)

        if mode_type is None:
            mode_type = '聊天模式'
        keywords = ["分类模式", "成堆投放模式"]

        if any(keyword in mode_type for keyword in keywords):
            garbage_name = text_keywords[0]
            print(garbage_name)
            input_1 = f"""
                请你将“{garbage_name}”分类为1.可回收垃圾 2.有害垃圾 3.其他垃圾 4.厨余垃圾 中的一种/
                不用解释原因，直接回答类别
                """
            model = Model()
            garbage_type_str = model.response(input_1)
            print(garbage_type_str)

            def classify_garbage(response_str_):
                keywords_ = {
                    "可回收垃圾": "可回收垃圾",
                    "有害垃圾": "有害垃圾",
                    "其他垃圾": "其他垃圾",
                    "厨余垃圾": "厨余垃圾"
                }

                for keyword, category in keywords_.items():
                    if keyword in response_str_:
                        return category

                return None

            def extract_mode(string):
                keywords_ = {
                    "分类模式": "分类模式",
                    "成堆投放模式": "成堆投放模式",
                }
                for keyword, mode_name in keywords_.items():
                    if keyword in string:
                        return keyword

            garbage_type = classify_garbage(garbage_type_str)
            return extract_mode(mode_type), garbage_type

        elif "取垃圾桶模式" in mode_type:
            can_type = {
                '回收': '可回收垃圾',
                '厨余': '厨余垃圾',
                '有害': '有害垃圾',
                '其他': '其他垃圾'
            }
            for keyword, garbage_type in can_type.items():
                if keyword in text:
                    return "取垃圾桶模式", garbage_type
            return "取垃圾桶模式", None
        else:
            return '聊天模式', None

    def judge_finished(self, text):
        if '完' in text:
            return True
        else:
            return False

    def chat(self, text):
        system_content = f"""
                你是一个智能垃圾桶的语音助手，你可以将帮用户通过视觉分类垃圾，将垃圾分为其他垃圾，厨余垃圾，可回收垃圾和有害垃圾四个类别/
                现在垃圾桶的满载情况是{self.data['full_load']},分别对应着垃圾桶的满载情况,True就是满载，False就是未满载/
                并且满载的垃圾桶不可以投放垃圾了，需要先清理垃圾桶/
                现在垃圾桶的投放情况是{self.data['number_of_launch']},分别对应着：其他垃圾，厨余垃圾，可回收垃圾和有害垃圾四个类别，这是用户的每种垃圾桶投放的次数，你可以根据此来估计用户产生垃圾的量/
                所以你就要根据情况灵活进行应答
                """
        model = Model(system_content)
        response_str = model.response(text)
        return response_str

    def recv_begin_or_data(self):
        try:
            header = self.server.receive_string()
            if header == 'y':
                self.server.receive_mp3(self.receive_mp3_path)
                return True
            elif header == 'n':
                return False
            elif header == 'speech_to_text':
                self.server.send_dict({'0': True})  # 发送接收string成功
                self.server.receive_mp3(self.receive_mp3_path)
                text = self.mp3_to_text(file_name=self.receive_mp3_path)
                print(text)
                if text == '':
                    text = 'NO_STR'
                self.server.send_string(text)  # 发送语音转文字的文字
                return False
            elif header == 'text_to_speech':
                str_ = self.server.receive_string()
                self.text_to_mp3(text=str_, file_name='voice/text_to_mp3.mp3')
                self.server.send_mp3('voice/text_to_mp3.mp3')
                return False
            else:
                self.data = self.server.receive_dict()
                return False
        except Exception:
            self.server.send_dict({'0': False})  # 报错消息string发送，提醒对方再次发送
            print('recv is error')

    def send_dict(self, mode=None, is_over=False, is_there_mp3_file=False, answer=None, text=None):
        dict_ = {
            'mode': mode,
            'garbage_type': self.garbage_type,
            'is_over': is_over,
            'is_there_mp3_file': is_there_mp3_file,
            'answer': answer,
            'input_text': text
        }
        self.server.send_dict(dict_)
        print('send_dict is done')
        return True

    def mp3_to_text(self, file_name):
        # 解决api不稳定的问题
        while True:
            text = stt.transform(file_name)
            if stt.if_right:
                break
        return text

    def text_to_mp3(self, text, file_name):
        while True:
            tts.transform(text, file_name)
            if tts.if_right:
                break

    def select_mode(self, mode_type, text):
        if mode_type == '分类模式':
            self.classify_mode()
        elif mode_type == '成堆投放模式':
            self.stacked_release_mode()
        elif mode_type == '取垃圾桶模式':
            self.dumping_mode()
        elif mode_type == '聊天模式':
            self.chat_mode(text)
        elif mode_type == '投放结束模式':
            pass

    def classify_mode(self):
        while self.garbage_type is None:
            file_path = self.server.receive_mp3(self.receive_again_mp3_path)
            text = self.mp3_to_text(file_name=file_path)
            self.send_dict(text=text)
            self.garbage_type = self.classify(text)
            self.send_dict(text=text)
        self.recv_begin_or_data()
        print('classify_mode is done')

    def stacked_release_mode(self):
        while self.garbage_type is None:
            file_path = self.server.receive_mp3(self.receive_again_mp3_path)
            text = self.mp3_to_text(file_path)
            self.send_dict(text=text)  # send the text
            self.garbage_type = self.classify(text)
            self.send_dict(text=text)  # send the garbage_type
        while True:
            self.server.receive_mp3(self.receive_again_mp3_path)
            text = self.mp3_to_text(self.receive_again_mp3_path)
            self.send_dict(text=text)  # send the text
            if self.judge_finished(text):
                self.send_dict(is_over=True, text=text)  # send the garbage type or over
                break
            else:
                self.garbage_type = self.classify(text)  # send the garbage type or over
                self.send_dict(text=text)
        self.recv_begin_or_data()
        print('stacked_release_mode is done')

    def dumping_mode(self):
        while self.garbage_type is None:
            self.server.receive_mp3(self.receive_again_mp3_path)
            text = self.mp3_to_text(self.receive_again_mp3_path)
            self.send_dict(text=text)  # send the text
            self.garbage_type = self.classify_can_name(text)
            self.send_dict(text=text)  # send the garbage_type
        print('dumping_mode is done')
        self.recv_begin_or_data()

    def chat_mode(self, text):
        response_str = self.chat(text)
        print(response_str)
        self.server.send_string(response_str)
        self.text_to_mp3(response_str, self.answer_mp3_path)
        self.server.send_mp3(self.answer_mp3_path)
        print('chat_mode is done')

    def end_mode(self):
        print('End of one cycle')

    def run(self):
        while True:
            if self.recv_begin_or_data():
                text = self.mp3_to_text(self.receive_mp3_path)
                self.send_dict(text=text)  # 跟新字幕
                print(text)
                mode_type, self.garbage_type = self.mode_classify(text)
                print(f'mode_type is {mode_type} , self.garbage_type is {self.garbage_type}')
                self.send_dict(mode=self.mode_type_2_mode[mode_type], text=text)
                self.select_mode(mode_type, text)
                self.end_mode()


if __name__ == '__main__':
    chat = ProcessChat('0.0.0.0', 8001)
    # chat = ProcessChat('127.0.0.1', 8001)
    # print(chat.mode_classify( '我要取出厨余垃圾桶'))
    chat.run()
