import os

from model import Model
from socket_server import Server
import stt
import tts
from Web_extract_keywords import extract_keywords


class ProcessChat:
    def __init__(self, ip, port):
        self.data = {
            'full_load': [False, False, True, False]
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

        text_keywords = extract_keywords(text)
        garbage_name = text_keywords[0]
        model = Model()
        input = f"""
        请你将“{garbage_name}”分类为1.可回收垃圾 2.有害垃圾 3.其他垃圾 4.厨余垃圾 中的一种/
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

    def match_mode(self, keywords, text):
        for mode, mode_keywords in keywords.items():
            if any(keyword in text for keyword in mode_keywords):
                return mode
        return None

    def mode_classify(self, text):

        text_keywords = extract_keywords(text)
        mode_keywords = {
            '分类模式': ['分类', '一个', '帮我'],
            '成堆投放模式': ['很多', '一堆', '大量', '连续'],
            '取垃圾桶模式': ['取出', '垃圾桶'],
            '聊天模式': []
        }
        mode_type = self.match_mode(mode_keywords, text_keywords)
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
            return mode_type, garbage_type

        elif mode_type == "取垃圾桶模式":
            can_type = {
                '回收': '可回收垃圾',
                '厨余': '厨余垃圾',
                '有害': '有害垃圾',
                '其他': '其他垃圾'
            }
            for keyword, garbage_type in can_type.items():
                if keyword in text:
                    return mode_type, garbage_type
            return mode_type, None
        else:
            return '聊天模式', None

    def judge_finished(self, text):
        if '完' in text:
            return True
        else:
            return False

    def chat(self, text):

        prompt = f"""
        你现在扮演智能垃圾桶的语音助手，能够和用户进行交流和对话/
        现在垃圾桶的满载情况是{self.data['full_load']}，按顺序是 其他垃圾，厨余垃圾，可回收垃圾，有害垃圾/
        {text}
        """
        model = Model()
        response_str = model.response(text)
        return response_str

    def recv_begin_or_data(self):
        header = self.server.receive_string()
        if header == 'y':
            self.server.receive_mp3(self.receive_mp3_path)
            return True
        elif header == 'n':
            return False
        elif header == 'speech_to_text':
            print('开始接收mp3文件')
            self.server.receive_mp3(self.receive_mp3_path)
            text = self.mp3_to_text(file_name=self.receive_mp3_path)
            if text == '':
                text = 'NO_STR'
            self.server.send_string(text)
            print(text)
            return False
        elif header == 'text_to_speech':
            str_ = self.server.receive_string()
            self.text_to_mp3(text=str_, file_name='voice/text_to_mp3.mp3')
            self.server.send_mp3('voice/text_to_mp3.mp3')
            return False
        else:
            self.data = self.server.receive_dict()
            return False

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
        elif mode_type == '倒垃圾模式':
            self.dumping_mode()
        elif mode_type == '聊天模式':
            self.chat_mode(text)
        elif mode_type == '投放结束模式':
            pass

    def classify_mode(self):
        while self.garbage_type is None:
            file_path = self.server.receive_mp3(self.receive_again_mp3_path)
            text = self.mp3_to_text(file_name=file_path)
            self.garbage_type = self.classify(text)
            self.send_dict(text=text)
        self.recv_begin_or_data()
        print('classify_mode is done')

    def stacked_release_mode(self):
        while self.garbage_type is None:
            file_path = self.server.receive_mp3(self.receive_again_mp3_path)
            text = self.mp3_to_text(file_path)
            self.garbage_type = self.classify(text)
            self.send_dict(text=text)
        while True:
            self.server.receive_mp3(self.receive_again_mp3_path)
            text = self.mp3_to_text(self.receive_again_mp3_path)

            if self.judge_finished(text):
                self.send_dict(is_over=True, text=text)
                break
            else:
                self.garbage_type = self.classify(text)
                self.send_dict(text=text)
        self.recv_begin_or_data()
        print('stacked_release_mode is done')

    def dumping_mode(self):
        while self.garbage_type is None:
            self.server.receive_mp3(self.receive_again_mp3_path)
            text = self.mp3_to_text(self.receive_again_mp3_path)
            self.garbage_type = self.classify(text)
            self.send_dict(text=text)
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
