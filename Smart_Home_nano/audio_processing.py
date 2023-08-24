import time

from processing import Processing


class AudioProcessing(Processing):
    def __init__(
            self,
            garbage_type,
            **kwargs
    ):
        super(AudioProcessing, self).__init__(**kwargs)
        self.garbage_type = garbage_type
        self.mp3_filename = {
            '其他垃圾': r'voice/其他垃圾.mp3',
            '可回收垃圾': r'voice/可回收垃圾.mp3',
            '厨余垃圾': r'voice/厨余垃圾.mp3',
            '有害垃圾': r'voice/有害垃圾.mp3'
        }

    def update_data(self):
        self.data['garbage_type'] = self.garbage_type

    # def server_info_recv(self):
    #     flag = int(self.client.receive_string())
    #     garbage_type_list = ['其他垃圾','厨余垃圾','可回收垃圾','有害垃圾']
    #     self.garbage_type=garbage_type_list[flag]

    def run(self):
        while self.garbage_type is None:
            self.update_captions('当前是分类模式，没听清楚您在说什么，请再次说出您要分类的垃圾')
            _, mp3_filename = self.wait_voice(self.data,filename='audio_processing')

            self.update_input_text('正在识别中')
            self.server_info_transfer(messages={},mp3_filename=mp3_filename)

            receive_dict = self.server_info_recv(mode='dict')   # receive the text
            self.update_input_text(text=receive_dict['input_text'])

            receive_dict = self.server_info_recv(mode='dict')  # receive the garbage type
            self.garbage_type = receive_dict['garbage_type']

            self.update_input_text(' ')
            time.sleep(1)
        self.data['number_of_launch'][int(self.garbage_type_str_to_num[self.garbage_type])] = \
            self.data['number_of_launch'][int(self.garbage_type_str_to_num[self.garbage_type])] + 1
        self.update_input_text(' ')
        self.update_captions(self.garbage_type)
        self.embedded_info_transfer(1, self.message_open_can[self.garbage_type])
        self.embedded_info_recv()
        self.update_data()
        self.UI_info_transfer()
        self.update_input_text(' ')
        time.sleep(1)
        self.server_info_transfer(messages=['update data', self.data])
