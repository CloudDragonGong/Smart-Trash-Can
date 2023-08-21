import queue
import time
import os
import serial
from pydub import AudioSegment
from pydub.playback import play
from multiprocessing import Queue

from real_time_recording_of_audio import real_time_recording_of_audio

'''
agreement of messages from server

dict 
- garbage_type 
- is_over
- is_there_mp3_file
- answer
- mode
- text

agreement of messages to server
- dict
- mp3
''
'''


class Processing:
    def __init__(
            self,
            data,
            client,
            communicate_queue=None,
            serial_port_address="/dev/ttyUSB0",
            serial_baud_rate=9600,
    ):
        self.message_open_can = {
            '其他垃圾': [[0x2C], [0x12], [0x00], [0x5B]],
            '厨余垃圾': [[0x2C], [0x12], [0x01], [0x5B]],
            '可回收垃圾': [[0x2C], [0x12], [0x02], [0x5B]],
            '有害垃圾': [[0x2C], [0x12], [0x03], [0x5B]]
        }
        self.message_close_can = [[0x2C], [0x12], [0x04], [0x00], [0x5B]]
        self.client = client
        self.data = data
        self.communicate_queue = communicate_queue
        self.garbage_type = None
        self.serial_port_address = serial_port_address
        self.ser = self.ser = serial.Serial(serial_port_address, baudrate=serial_baud_rate, timeout=0.5)

    def audio_play(self, file_path):
        sound = AudioSegment.from_mp3(file_path)
        play(sound)

    def wait_voice(self, data, filename):
        output_filename = os.path.join('voice', filename + '.mp3')
        output_wav = os.path.join('voice', filename + '.wav')
        #  ensure data[if_begin]= false or data['triggered_process'] is the right process
        if_ok = real_time_recording_of_audio(data, output_filename=output_filename,
                                             output_wav=output_wav)
        return if_ok, output_filename

    def update_captions(self, caption):
        self.data['captions'] = caption
        self.UI_info_transfer()
        play(AudioSegment.from_mp3(f'voice/{caption}.mp3'))
        self.data['captions'] = ' '
        self.UI_info_transfer()

    def server_info_transfer(self, messages, mp3_filename=None):
        for message in messages:
            if isinstance(message, str):
                self.client.send_string(message)
            elif isinstance(message, dict):
                self.client.send_dict(message)
        if mp3_filename is not None:
            self.client.send_mp3(mp3_filename)
        print(f'server_info_transfer in {self.__class__.__name__} is done')

    def server_info_recv(self, mode, mp3_file_name=None):
        """
        receive the info from server
        Args:
            mode:  dict or mp3
            mp3_file_name: if mode == mp3 ,and mp3_file_name == None,exception by assert

        Returns:
            mode == dict : dict
            else: boolean
        """
        if mode == 'dict':
            dict_ = self.client.receive_dict()
            print(f'server_info_recv in {self.__class__.__name__} is done')
            return dict_
        else:
            assert mp3_file_name is None, 'mp3_file_name is None'
            self.client.receive_mp3(mp3_file_name)
            print(f'server_info_recv in {self.__class__.__name__} is done')
            return True

    def update_input_text(self, text):
        self.data['input_text'] = text
        self.UI_info_transfer()

    def UI_info_transfer(self):
        if self.communicate_queue is not None:
            try:
                self.communicate_queue.put_nowait(self.data)
            except queue.Full:
                print('queue is Full')
        else:
            print('communicate_queue is None')

    def embedded_info_transfer(self, mode, message):
        """

        Args:
            mode:
            - 视觉检测  1
            - 取垃圾桶  2
            - 倾倒垃圾桶  3
            - 倾倒完毕  4
            message:

        Returns:

        """
        mode_info = [[0x01], [0x02], [0x03], [0x04]]  # 补全message
        message.insert(2, mode_info[mode - 1])
        for message_element in message:
            message_element = bytearray(message_element)
            time.sleep(0.1)
            print(message_element)
            self.ser.write(message_element)

        print('embedding_into_transfer is Done')

    def recv(self):
        while True:
            data = self.ser.read(1)
            print(data)
            if data == b"":
                continue
            else:
                break
        return data

    def embedded_info_recv(self):
        """
        data:
        - 0 , 1 包头
        - 2 满载校验位
        - 3 满载垃圾桶编号  00 其他垃圾 01 厨余垃圾  02 可回收垃圾 03 有害垃圾
        - 4 完成校验位
        - 5 包尾
        Returns:

        """
        data = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

        print("开始等待读取")
        for i in range(0, len(data)):
            data[i] = self.recv()
            data[i] = int.from_bytes(data[i], byteorder="big")
            print(data[i])
            # data[i]=ser.read(1)
            # print(data[i])
            # data[i]=int.from_bytes(data[i],byteorder='big')
        print("读取完成")
        garbage_type = ['其他垃圾', '厨余垃圾', ' 可回收垃圾 ', '有害垃圾']
        if data[0] == 0x2C and data[1] == 0x12:
            self.data['full_load'][garbage_type[data[3]]] = bool(data[2])
        else:
            print('包头错误')
        print('embedded_info_transfer is Done')


if __name__ == '__main__':
    pass
