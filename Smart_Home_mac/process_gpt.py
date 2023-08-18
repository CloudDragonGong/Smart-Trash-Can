from model import Model
from socket_server import Server
import stt
import tts


class ProcessChat:
    def __init__(self, ip, port):
        self.data = {
            'full_load': [False, False, True, False]
        }
        self.server = Server(ip, port)
        self.garbage_type = None
        self.receive_mp3_path = r'receive_mp3.mp3'
        self.mode_type_2_mode = {
            '分类模式': 0,
            '成堆投放模式': 1,
            '倒垃圾模式': 2,
            '聊天模式': 3
        }
        self.receive_again_mp3_path = r'receive_again_mp3.mp3'
        self.answer_mp3_path = r'answer_mp3.mp3'
        pass

    def garbage_classify(self, garbage_type: str):
        """

        :param garbage_type:
        :return:
        '其他垃圾'
        '厨余垃圾'
        '可回收垃圾'
        '有害垃圾'
        """
        prompt = f"""
        你是一个智能语音垃圾桶/
        现在你要分类垃圾，分类为/
        1.可回收垃圾 2.有害垃圾 3.其他垃圾 4.厨余垃圾/
        的其中一种，然后后面直接回答属于哪种垃圾即可，回答的格式是/
        “可回收垃圾” ”有害垃圾“ ”其他垃圾“ ”厨余垃圾“/
        一定要注重回答格式！！！
        """
        text = f"""
            {garbage_type}属于什么垃圾？
        """
        model = Model(prompt)
        garbage_type_str = model.response(text)
        if '其他垃圾' in garbage_type_str:
            return '其他垃圾'
        elif '厨余垃圾' in garbage_type_str:
            return '厨余垃圾'
        elif '可回收垃圾' in garbage_type_str:
            return '可回收垃圾'
        else:
            return '有害垃圾'

    def mode_classify(self, text):
        prompt = f"""
        你是智能语音垃圾桶的语音助手，你待会根据接收到的消息，将消息分为下面四种行为类别：/
        1.分类模式：例如“我要投放纸张”/
        2.成堆投放模式：例如“我要投放大量的纸张”，“我要投放成堆的香蕉皮”，“我要连续倾倒厨余垃圾”/
        3.倒垃圾模式：例如“我要清空厨余垃圾桶里的垃圾”，“我要倒掉可回收垃圾桶里的垃圾”/
        4.聊天模式，如果消息的内容和上面的内容没啥关系，那应该就是聊天模式,比如“介绍一下华中科技大学”/
        分完上面四个类别之后，在进行分类/
        提取出消息中的物品，如”纸张“，将其分类为1.可回收垃圾 2.有害垃圾 3.其他垃圾 4.厨余垃圾/
        所以你最后回答的格式是：/
        例如“分类模式，可回收垃圾”。/
        待会接收到了消息，就按照上面我很说的分类就行，其他事情不用干/
        """
        model = Model(prompt)
        response_str = model.response(f"请分类这句话:{text}")
        if '其他垃圾' in response_str:
            garbage_type = '其他垃圾'
        elif '厨余垃圾' in response_str:
            garbage_type = '厨余垃圾'
        elif '可回收垃圾' in response_str:
            garbage_type = '可回收垃圾'
        else:
            garbage_type = '有害垃圾'

        if '分类模式' in response_str:
            return '分类模式', garbage_type
        elif '成堆投放' in response_str:
            return '成堆投放模式', garbage_type
        elif '倒垃圾' in response_str:
            return '倒垃圾模式', garbage_type
        else:
            return '聊天模式', None

    def judge_finished(self, text):
        prompt = f"""
                你是智能语音垃圾桶的语音助手，你待会根据接收到的消息，将消息分为下面5种行为类别：/
                1.分类模式：例如“我要投放纸张”/
                2.成堆投放模式：例如“我要投放大量的纸张”，“我要投放成堆的香蕉皮”，“我要连续倾倒厨余垃圾”/
                3.倒垃圾模式：例如“我要清空厨余垃圾桶里的垃圾”，“我要倒掉可回收垃圾桶里的垃圾”/
                4.投放结束模式：例如“我投放完了”，“我已经完成了投放”，“我已经完成了垃圾/
                5.聊天模式，如果消息的内容和上面的内容没啥关系，那应该就是聊天模式/
                分完上面五个类别之后，在进行分类/
                提取出消息中的物品，如”纸张“，将其分类为1.可回收垃圾 2.有害垃圾 3.其他垃圾 4.厨余垃圾/
                所以你最后回答的格式是：/
                “分类模式，可回收垃圾”,或者：“投放结束模式”/
                待会接收到了消息，就按照上面我很说的分类就行，其他事情不用干/
                """
        model = Model(prompt)
        response_str = model.response(f"请分类这句话:{text}")
        print(response_str)
        if '其他垃圾' in response_str:
            garbage_type = '其他垃圾'
        elif '厨余垃圾' in response_str:
            garbage_type = '厨余垃圾'
        elif '可回收垃圾' in response_str:
            garbage_type = '可回收垃圾'
        else:
            garbage_type = '有害垃圾'

        if '分类模式' in response_str:
            return '分类模式', garbage_type
        elif '成堆投放' in response_str:
            return '成堆投放模式', garbage_type
        elif '倒垃圾' in response_str:
            return '倒垃圾模式', garbage_type
        elif '投放结束模式' in response_str:
            return '投放结束模式', None
        else:
            return '聊天模式', None

    def chat(self, text):

        prompt = f"""
        你现在扮演智能垃圾桶的语音助手，能够和用户进行交流和对话/
        现在垃圾桶的满载情况是{self.data['full_load']}，按顺序是 其他垃圾，厨余垃圾，可回收垃圾，有害垃圾/
        接下来我会进行和你聊天，你如实回答就行，必要时结合垃圾桶的满载情况进行回答
        """
        model = Model(prompt)
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
            self.server.receive_mp3('speech_to_text.mp3')
            text = self.mp3_to_text(file_name='speech_to_text.mp3')
            self.server.send_string(text)
            print(text)
            return False
        elif header == 'text_to_speech':
            str_ = self.server.receive_string()
            self.text_to_mp3(text=str_, file_name='text_to_mp3.mp3')
            self.server.send_mp3('text_to_mp3.mp3')
            return False
        else:
            self.data = self.server.receive_dict()
            return False

    def send_dict(self, mode=None, is_over=False, is_there_mp3_file=False, answer=None):
        dict_ = {
            'mode': mode,
            'garbage_type': self.garbage_type,
            'is_over': is_over,
            'is_there_mp3_file': is_there_mp3_file,
            'answer': answer
        }
        self.server.send_dict(dict_)
        print('send_dict is done')
        return True

    def mp3_to_text(self, file_name):
        return stt.transform(file_name)

    def text_to_mp3(self, text, file_name):
        tts.transform(text, file_name)

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
        self.recv_begin_or_data()
        print('classify_mode is done')

    def stacked_release_mode(self):
        self.server.receive_mp3(self.receive_again_mp3_path)
        text = self.mp3_to_text(self.receive_again_mp3_path)
        mode, garbage_type = self.judge_finished(text)
        if mode == '投放结束模式':
            self.send_dict(is_over=True)
        elif mode == '聊天模式':
            self.send_dict()
        else:
            self.garbage_type = garbage_type
            self.send_dict()
        self.recv_begin_or_data()
        print('stacked_release_mode is done')

    def dumping_mode(self):
        self.server.receive_mp3(self.receive_again_mp3_path)
        text = self.mp3_to_text(self.receive_again_mp3_path)
        mode, garbage_type = self.judge_finished(text)
        if mode == '投放结束模式':
            self.send_dict(is_over=True)
        elif mode == '聊天模式':
            self.send_dict()
        else:
            self.garbage_type = garbage_type
            self.send_dict()
        self.recv_begin_or_data()
        print('dumping_mode is done')
        self.recv_begin_or_data()

    def chat_mode(self, text):
        response_str = self.chat(text)
        self.text_to_mp3(response_str, self.answer_mp3_path)
        self.server.send_mp3(self.answer_mp3_path)
        print('chat_mode is done')

    def end_mode(self):
        print('End of one cycle')

    def run(self):
        while True:
            if self.recv_begin_or_data():
                text = self.mp3_to_text(self.receive_mp3_path)
                mode_type, self.garbage_type = self.mode_classify(text)
                print(mode_type)
                self.send_dict(mode=self.mode_type_2_mode[mode_type])
                self.select_mode(mode_type, text)
                self.end_mode()


if __name__ == '__main__':
    chat = ProcessChat('127.0.0.1', 8001)
    chat.run()
