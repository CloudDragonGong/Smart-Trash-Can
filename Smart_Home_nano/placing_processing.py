from processing import Processing
from real_time_recording_of_audio import real_time_recording_of_audio
import time


class PlacingProcessing(Processing):
    def __init__(
            self,
            garbage_type,
            **kwargs
    ):
        super(PlacingProcessing, self).__init__(**kwargs)
        self.garbage_type = garbage_type

    def update_data(self):
        self.data['garbage_type'] = self.garbage_type

    def run(self):
        while self.garbage_type is None:
            self.update_captions('当前是成堆模式，没听清楚您在说什么垃圾，请再次说出您要投放的垃圾')
            _, mp3_filepath = self.wait_voice(self.data, filename='placing_processing')
            self.server_info_transfer(messages={}, mp3_filename=mp3_filepath)
            receive_dict = self.server_info_recv(mode='dict') # receive the text
            self.update_input_text(text=receive_dict['input_text'])  # update text timely
            receive_dict = self.server_info_recv(mode='dict')  # receive the garbage_type
            self.garbage_type = receive_dict['garbage_type']
            self.update_input_text(text=' ')
        self.embedded_info_transfer(3, self.message_open_can[self.garbage_type])
        while True:
            _, mp3_filepath = self.wait_voice(self.data, filename='placing_processing')
            self.server_info_transfer(messages={}, mp3_filename=mp3_filepath)
            dict_ = self.server_info_recv(mode='dict') # receive the text
            self.update_input_text(text=dict_['input_text'])  # update text timely
            dict_ = self.server_info_recv(mode='dict')  # receive the garbage_type and is_over
            self.garbage_type = dict_['garbage_type']
            self.update_input_text(text=' ')
            if dict_['is_over']:
                self.embedded_info_transfer(4, self.message_close_can)
                break
            elif dict_['garbage_type'] is None:
                self.update_captions('请您告诉我是否结束投放？如果没有，请告诉我你接下来要投放的垃圾桶吧')
            else:
                self.data['number_of_launch'][int(self.garbage_type_str_to_num[self.garbage_type])] = \
                    self.data['number_of_launch'][int(self.garbage_type_str_to_num[self.garbage_type])] + 1
                self.embedded_info_transfer(3, self.message_open_can[self.garbage_type])
                self.update_data()
                self.UI_info_transfer()
                self.update_captions('好的，把垃圾扔进来吧，亲')
        self.update_captions('好的')
        self.update_data()
        self.UI_info_transfer()
        self.server_info_transfer(messages=['update data', self.data])
