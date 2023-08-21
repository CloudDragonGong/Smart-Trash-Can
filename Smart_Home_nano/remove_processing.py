from processing import Processing
from real_time_recording_of_audio import real_time_recording_of_audio
import time


class RemoveProcessing(Processing):
    def __init__(
            self,
            garbage_type,
            **kwargs,
    ):
        super(RemoveProcessing, self).__init__(**kwargs)
        self.garbage_type = garbage_type

    def update_data(self):
        self.data['garbage_type'] = self.garbage_type

    def run(self):
        while self.garbage_type is None:
            self.update_captions('当前是取垃圾桶倒垃圾模式，但是我没听清楚您所说的垃圾种类，请您能在说一遍吗？')
            _,file_path = self.wait_voice(self.data,'remove_processing')
            self.server_info_transfer(messages={},mp3_filename=file_path)
            receive_dict = self.server_info_recv(mode='dict')
            self.garbage_type = receive_dict['garbage_type']
            self.update_input_text(receive_dict['input_text'])
        self.embedded_info_transfer(2, self.message_open_can[self.garbage_type])
        self.update_data()
        self.UI_info_transfer()
        self.update_captions('好的，取出垃圾吧，亲')
        self.server_info_transfer(messages=['update data', self.data])

