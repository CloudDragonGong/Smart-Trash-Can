import queue

import serial
from pydub import AudioSegment
from pydub.playback import play
from multiprocessing import Queue
'''
agreement of messages from server

dict 
- garbage_type 
- is_over
- is_there_mp3_file
- answer
- mode

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
            '其他垃圾': [],
            '厨余垃圾': [],
            '可回收垃圾': [],
            '有害垃圾': []
        }
        self.message_close_can = []
        self.client = client
        self.data = data
        self.communicate_queue = communicate_queue
        self.garbage_type = None
        self.serial_port_address = serial_port_address
        self.ser = self.ser = serial.Serial(serial_port_address, baudrate=serial_baud_rate, timeout=0.5)

    def audio_play(self, file_path):
        sound = AudioSegment.from_mp3(file_path)
        play(sound)

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
        if mode == 'dict':
            dict_ = self.client.receive_dict()
            print(f'server_info_recv in {self.__class__.__name__} is done')
            return dict_
        else:
            assert mp3_file_name is None, 'mp3_file_name is None'
            self.client.receive_mp3(mp3_file_name)
            print(f'server_info_recv in {self.__class__.__name__} is done')
            return True


    def UI_info_transfer(self):
        if self.communicate_queue is not None:
            try:
                self.communicate_queue.put_nowait(self.data)
            except queue.Full:
                print('queue is Full')
        else:
            print('communicate_queue is None')

    def embedded_info_transfer(self,mode,message):
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
        print('embedding_into_transfer is Done')

    def embedded_info_recv(self):
        print('embedded_info_transfer is Done')



if __name__ == '__main__':
    pass