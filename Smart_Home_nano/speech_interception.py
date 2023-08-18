import time
from multiprocessing import Queue

from pydub import AudioSegment
from pydub.playback import play

from real_time_recording_of_audio import real_time_recording_of_audio, real_time_recording_of_audio_timeout
from audio_processing import AudioProcessing
from placing_processing import PlacingProcessing
from remove_processing import RemoveProcessing
from socket_client import Client

"""
speech Interception agreement from server

dict 
- garbage_type 
- is_over
- is_there_mp3_file
- answer
- mode


"""


class SpeechInterception:
    def __init__(self, client, activation_name, data, communicate_queue, serial_port_address="/dev/ttyUSB0"):
        self.communicate_queue = communicate_queue
        self.garbage_type = None
        self.data = data
        self.client = client
        self.name = activation_name
        self.wait_voice_speech_mp3 = r'wait_voice_speech.mp3'
        self.wait_voice_speech_wav = r'wait_voice_speech.wav'
        self.answer_mp3 = r'answer.mp3'
        self.mode = None
        self.serial_port_address = serial_port_address

    def wait_voice(self):
        return real_time_recording_of_audio(output_filename=self.wait_voice_speech_mp3,
                                            output_wav=self.wait_voice_speech_wav)

    def wait_voice_with_timeout(self, timeout=10):
        return real_time_recording_of_audio_timeout(output_filename=self.wait_voice_speech_mp3,
                                                    output_wav=self.wait_voice_speech_wav,
                                                    max_waiting_time=timeout)

    def speech_to_text(self):
        self.client.send_string('speech_to_text')
        self.client.send_mp3(self.wait_voice_speech_mp3)
        text = self.client.receive_string()
        return text

    def text_to_speech(self, text):
        self.client.send_string('text_to_speech')
        self.client.send_string(text)
        self.client.receive_mp3(self.answer_mp3)

    def server_into_transfer(self):
        pass

    def server_info_recv(self):
        pass

    def convey_introductions(self):
        pass

    def identify(self):
        while self.wait_voice() and (not self.data['if_begin']):
            text = self.speech_to_text()
            if self.name in text:
                self.client.send_string('y')
                self.data['if_begin'] = True
                self.data['triggered_process'] = 2
                return True
            else:
                self.client.send_string('n')

    def identity_mode(self):
        self.client.send_mp3(self.wait_voice_speech_mp3)
        dict_ = self.client.receive_dict()
        self.mode = dict_['mode']
        self.garbage_type = dict_['garbage_type']

    def classify_mode(self):
        audio_processing = AudioProcessing(
            garbage_type=self.garbage_type,
            data=self.data,
            client=self.client,
            communicate_queue=self.communicate_queue,
            serial_port_address=self.serial_port_address
        )
        audio_processing.run()

    def placing_mode(self):
        placing_processing = PlacingProcessing(
            garbage_type=self.garbage_type,
            data=self.data,
            communicate_queue=self.communicate_queue,
            client=self.client,
            serial_port_address=self.serial_port_address,
        )
        placing_processing.run()

    def removing_mode(self):
        remove_processing = RemoveProcessing(
            garbage_type=self.garbage_type,
            data=self.data,
            communicate_queue=self.communicate_queue,
            client=self.client,
            serial_port_address=self.serial_port_address
        )
        remove_processing.run()

    def run_mode(self):
        modes = [self.classify_mode, self.placing_mode, self.removing_mode, self.chat_mode]
        modes[self.mode]()

    def chat_mode(self):
        self.client.receive_mp3(self.answer_mp3)
        sound = AudioSegment.from_mp3(self.answer_mp3)
        play(sound)

    def run(self):
        if self.wait_voice_with_timeout():
            self.identity_mode()
            self.run_mode()
        else:
            pass


if __name__ == '__main__':
    data = {
        'full_load': {
            '其他垃圾': False,
            '厨余垃圾': False,
            '可回收垃圾': False,
            '有害垃圾': False},
        'garbage_type': None,
        'if_begin': False,  # 用于两线程的相互阻断
        'triggered_process': 0  # 获取被触发的模式（视觉1/语音2）
    }
    communicate_queue = Queue(1)
    client = Client(ip='127.0.0.1', port=8001)
    speech_interception = SpeechInterception(
        client=client,
        data=data,
        activation_name='小龙',
        communicate_queue=communicate_queue,
        serial_port_address='/dev/tty.Bluetooth-Incoming-Port'
    )
    speech_interception.identify()
