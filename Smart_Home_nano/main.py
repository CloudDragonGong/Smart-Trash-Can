import multiprocessing
import platform
import sys

from PyQt5.QtWidgets import QApplication

from UI import SmartTrashCanUI
from vision_processing import VisionProcessing
from AI_module import Resnet
from speech_interception import SpeechInterception
from socket_client import Client
from multiprocessing import Process, Queue
import threading

"""
main class for jetson_nano
store data and begin the process
"""


class MyThread(threading.Thread):
    def __init__(self, target):
        super().__init__()
        self._target = target
        self._result = False
        self._event = threading.Event()
        self._should_stop = False

    def run(self):
        if self._target:
            self._result = self._target()
            self._event.set()

    def get_result(self):
        return self._result

    def wait_completion(self):
        self._event.wait()

    def stop(self):
        self._should_stop = True


class Main:
    def __init__(self):
        self.data = {
            'full_load': {
                '其他垃圾': False,
                '厨余垃圾': False,
                '可回收垃圾': False,
                '有害垃圾': False},
            'garbage_type': None,
            'if_begin': False,  # 用于两线程的相互阻断
            'triggered_process': 0,  # 获取被触发的模式（视觉1/语音2）
            'number_of_launch': [0, 0, 0, 0],
            'captions': " ",
            'input_text': '请说话'
        }
        self.communicate_queue = Queue(1)
        self.client = Client(ip='127.0.0.1', port=8001) if platform.system() == 'Darwin' else Client(ip='10.13.4.45',
                                                                                                     port=8001)
        self.resnet = Resnet()
        self.open_port = '/dev/tty.Bluetooth-Incoming-Port' if platform.system() == 'Darwin' else "/dev/ttyUSB0"
        self.vision_processing = VisionProcessing(
            client=self.client,
            data=self.data,
            resnet=self.resnet,
            communicate_queue=self.communicate_queue,
            serial_port_address=self.open_port
        )
        self.speech_interception = SpeechInterception(
            client=self.client,
            data=self.data,
            activation_name='小龙',
            communicate_queue=self.communicate_queue,
            serial_port_address=self.open_port
        )

    def update_data(self):
        self.data['garbage_type'] = None
        self.data['if_begin'] = False  # 用于两线程的相互阻断
        self.data['triggered_process'] = 0  # 获取被触发的模式（视觉1/语音2）

    def run(self):
        self.communicate_queue.put_nowait(self.data)
        while True:
            self.update_data()
            thread1 = threading.Thread(target=self.vision_processing.identify, args=())
            thread2 = threading.Thread(target=self.speech_interception.identify, args=())
            thread1.start()
            thread2.start()
            print('begin two thread')
            thread1.join()
            thread2.join()
            if self.data['triggered_process'] == 1:
                print('vision process')
                self.vision_processing.run()
            elif self.data['triggered_process'] == 2:
                print('speech interception')
                self.speech_interception.run()
            else:
                pass
            self.data['if_begin'] = False
            print('finish a cycle')


def run_ui(data_queue):
    app = QApplication(sys.argv)
    ui = SmartTrashCanUI(data_queue)
    ui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    multiprocessing.set_start_method("spawn") if platform.system() == 'Darwin' else None  # 或 "forkserver"
    main_process = Main()
    ui_process = Process(target=run_ui, args=(main_process.communicate_queue,))
    ui_process.start()
    main_process.run()
    ui_process.join()
    print('is over')
