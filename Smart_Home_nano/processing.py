import queue
import time
import os
import serial
from pydub import AudioSegment
from pydub.playback import play
from multiprocessing import Queue
from copy import deepcopy

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
            text_queue=None,
            serial_port_address="/dev/ttyUSB0",
            serial_baud_rate=9600,
    ):
        self.text = None
        self.text_queue = text_queue
        self.message_open_can = {
            '其他垃圾': [[0x2C], [0x12], [0x00], [0x5B]],
            '厨余垃圾': [[0x2C], [0x12], [0x01], [0x5B]],
            '可回收垃圾': [[0x2C], [0x12], [0x02], [0x5B]],
            '有害垃圾': [[0x2C], [0x12], [0x03], [0x5B]]
        }
        self.garbage_type_str_to_num = {
            '其他垃圾': 0,
            '厨余垃圾': 1,
            '可回收垃圾': 2,
            '有害垃圾': 3
        }
        self.message_close_can = [[0x2C], [0x12], [0x04], [0x00], [0x5B]]
        self.client = client
        self.data = data
        self.communicate_queue = communicate_queue
        self.garbage_type = None
        self.serial_port_address = serial_port_address
        self.ser = serial.Serial(serial_port_address, baudrate=serial_baud_rate, timeout=0.5)

    def audio_play(self, file_path):
        sound = AudioSegment.from_mp3(file_path)
        play(sound)

    def wait_voice(self, data, filename):
        output_filename = os.path.join('voice', filename + '.mp3')
        output_wav = os.path.join('voice', filename + '.wav')
        #  ensure data[if_begin]= false or data['triggered_process'] is the right process
        if_ok = real_time_recording_of_audio(data, process_class=self, output_filename=output_filename,
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
            time.sleep(0.2)
        if mp3_filename is not None:
            time.sleep(0.2)
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
        self.text = text
        self.UI_text_transfer()

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
        message_copy = deepcopy(message)
        mode_info = [[0x01], [0x02], [0x03], [0x04]]  # 补全message
        message_copy.insert(2, mode_info[mode - 1])
        for message_element in message_copy:
            message_element = bytearray(message_element)
            time.sleep(0.1)
            print(message_element)
            self.ser.write(message_element)

        print('embedding_into_transfer is Done')

    def recv(self):
        start_time = time.time()  # 记录开始时间
        while True:
            data = self.ser.read(1)
            print(data)
            if data == b"":
                elapsed_time = time.time() - start_time  # 计算经过的时间
                if elapsed_time > 15:  # 如果超过15秒，抛出异常
                    raise TimeoutError("No data received for 15 seconds.")
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
            7秒没读到，自动退出
        """
        time.sleep(1)
        data = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

        print("开始等待读取")
        if_begin = False
        recv_num = 0
        try:
            while True:
                data_recv = self.recv()
                data_recv = int.from_bytes(data_recv, byteorder="big")
                print(data_recv)
                if data_recv == 0x2C:
                    if_begin = True
                if if_begin:
                    data[recv_num] = data_recv
                    recv_num = recv_num + 1
                if recv_num == len(data):
                    break
            print("读取完成:" + str(data))
            garbage_type = ['其他垃圾', '厨余垃圾', '可回收垃圾', '有害垃圾']
            if data[0] == 0x2C and data[1] == 0x12:
                self.data['full_load'][garbage_type[data[3]]] = bool(data[2])
            else:
                print('包头错误')
        except TimeoutError as e:
            print(e)
        print('embedded_info_transfer is Done')


if __name__ == '__main__':
    pass
