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

    def wait_voice(self):
        real_time_recording_of_audio(output_filename='wait_voice_placing.mp3', output_wav='wait_voice_placing.wav')

    def update_data(self):
        self.data['garbage_type'] = self.garbage_type

    def run(self):
        self.embedded_info_transfer(2, self.message_open_can[self.garbage_type])
        self.update_data()
        self.UI_info_transfer()
        while True:
            self.wait_voice()
            self.server_info_transfer(messages={}, mp3_filename='wait_voice_placing.mp3')
            dict_ = self.server_info_recv(mode='dict')
            if dict_['is_over']:
                break
            else:
                self.garbage_type = dict_['garbage_type']
                time.sleep(1)
                self.embedded_info_transfer(2, self.message_open_can[self.garbage_type])
                self.update_data()
                self.UI_info_transfer()
        self.update_data()
        self.UI_info_transfer()
        self.server_info_transfer(messages=['update data', self.data])
