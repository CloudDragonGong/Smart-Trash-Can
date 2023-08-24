import queue
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
- text


"""


class SpeechInterception:
    def __init__(self, client, activation_name, data, communicate_queue, text_queue,
                 serial_port_address="/dev/ttyUSB0"):
        self.text = None
        self.communicate_queue = communicate_queue
        self.text_queue = text_queue
        self.garbage_type = None
        self.data = data
        self.client = client
        self.name = activation_name
        self.wait_voice_speech_mp3 = r'voice/wait_voice_speech.mp3'
        self.wait_voice_speech_wav = r'voice/wait_voice_speech.wav'
        self.answer_mp3 = r'voice/answer.mp3'
        self.mode = None
        self.serial_port_address = serial_port_address

    def wait_voice(self, data):
        return real_time_recording_of_audio(data, self, output_filename=self.wait_voice_speech_mp3,
                                            output_wav=self.wait_voice_speech_wav)

    def wait_voice_with_timeout(self, timeout=10):
        return real_time_recording_of_audio_timeout(process_class=self,output_filename=self.wait_voice_speech_mp3,
                                                    output_wav=self.wait_voice_speech_wav,
                                                    max_waiting_time=timeout)

    def speech_to_text(self):
        self.update_input_text('正在识别说话中')
        if_recv_server = False
        while not if_recv_server:  # 不成功则堵塞
            self.client.send_string('speech_to_text')
            if_recv_server = self.client.receive_dict()['0']  # 接收成功消息
        if if_recv_server:  # 如果接收成功，才继续发送
            time.sleep(0.5)  # for server to receive timely
            self.client.send_mp3(self.wait_voice_speech_mp3)
        text = ''
        while not self.data['if_begin']:
            recv_data = self.client.client_socket.recv(2048)
            if recv_data:
                recv_data = recv_data.decode('utf-8')
                text = recv_data
                return text
        if self.data['if_begin']:  # 中途如果遇到视觉运作，就发送不用理睬的信号，防止扔垃圾的声响影响视觉就检测
            self.client.send_string('n')
        self.update_input_text(' ')
        return text

    def text_to_speech(self, text):
        self.client.send_string('text_to_speech')
        time.sleep(1)
        self.client.send_string(text)
        self.client.receive_mp3(self.answer_mp3)

    def server_into_transfer(self):
        pass

    def server_info_recv(self):
        pass

    def convey_introductions(self):
        pass

    def update_input_text(self, text):
        self.text = text
        self.UI_text_transfer()

    def identify(self):
        while self.wait_voice(self.data):
            text = self.speech_to_text()
            self.update_input_text(text)  # 更新嗨小龙
            if self.name in text and not self.data['if_begin']:
                self.client.send_string('y')
                self.data['if_begin'] = True
                self.data['triggered_process'] = 2
                self.update_captions(caption='我在呢')
                self.update_input_text(' ')
                return True
            elif not self.data['if_begin']:
                self.client.send_string('n')
                self.data['triggered_process'] = 0
                self.data['if_begin'] = False
                self.update_input_text('???????')
                
    def update_captions(self, caption):
        self.data['captions'] = caption
        self.UI_info_transfer()
        play(AudioSegment.from_mp3(f'voice/{caption}.mp3'))
        self.data['captions'] = ' '
        self.UI_info_transfer()

    def UI_text_transfer(self):
        if self.text_queue is not None:
            try:
                if self.text_queue.full():
                    try:
                        self.text_queue.get_nowait()
                    except queue.Empty:
                        pass
                self.text_queue.put_nowait(self.text)
            except queue.Full:
                print('queue is Full')
        else:
            print('text_queue is None')

    def UI_info_transfer(self):
        if self.communicate_queue is not None:
            try:
                self.communicate_queue.put_nowait(self.data)
            except queue.Full:
                print('queue is Full')
        else:
            print('communicate_queue is None')

    def identity_mode(self):
        self.client.send_mp3(self.wait_voice_speech_mp3)
        dict_ = self.client.receive_dict()
        # 更新input字幕
        self.update_input_text(text=dict_['input_text'])
        dict_ = self.client.receive_dict()
        self.mode = dict_['mode']
        self.garbage_type = dict_['garbage_type']

    def classify_mode(self):
        audio_processing = AudioProcessing(
            garbage_type=self.garbage_type,
            data=self.data,
            client=self.client,
            communicate_queue=self.communicate_queue,
            serial_port_address=self.serial_port_address,
            text_queue=self.text_queue
        )
        self.update_captions('好的，正在为您分类')
        self.update_input_text(' ')
        audio_processing.run()

    def placing_mode(self):
        placing_processing = PlacingProcessing(
            garbage_type=self.garbage_type,
            data=self.data,
            communicate_queue=self.communicate_queue,
            text_queue=self.text_queue,
            client=self.client,
            serial_port_address=self.serial_port_address,
        )
        self.update_input_text(' ')
        placing_processing.run()

    def removing_mode(self):
        remove_processing = RemoveProcessing(
            garbage_type=self.garbage_type,
            data=self.data,
            communicate_queue=self.communicate_queue,
            text_queue=self.text_queue,
            client=self.client,
            serial_port_address=self.serial_port_address
        )
        self.update_input_text(' ')
        remove_processing.run()

    def run_mode(self):
        modes = [self.classify_mode, self.placing_mode, self.removing_mode, self.chat_mode]
        modes[self.mode]()

    def chat_mode(self):
        self.update_input_text('正在生成回答')
        # update captions
        self.data['captions'] = self.client.receive_string(length=4096)
        self.client.receive_mp3(self.answer_mp3)
        self.update_input_text(' ')
        self.UI_info_transfer()
        sound = AudioSegment.from_mp3(self.answer_mp3)
        self.data['captions'] = ''
        self.UI_info_transfer()
        play(sound)

    def run(self):
        if self.wait_voice_with_timeout():
            self.update_input_text('正在识别说话中')
            self.identity_mode()
            self.run_mode()
            self.update_input_text(text=' ')
        else:
            self.update_input_text(text=' ')


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
    text_queue = Queue(1)
    client = Client(ip='10.13.4.45', port=8001)
    speech_interception = SpeechInterception(
        client=client,
        data=data,
        activation_name='龙',
        communicate_queue=communicate_queue,
        text_queue=text_queue
    )
    speech_interception.identify()
