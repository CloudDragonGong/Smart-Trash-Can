import multiprocessing
import platform
import re
import sys
import threading
import time
from multiprocessing import Process

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer, Qt, QDateTime
import queue


class SmartTrashCanUI(QMainWindow):
    def __init__(self, data_queue,text_queue):
        super().__init__()
        self.captions = None
        self.input_text = None
        self.punctuation_marks = ['.', '!', '?', '，', '。', ',', '、']
        self.setWindowTitle("Smart Trash Can UI")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: black; color: white; font-size: 24px;")  # Set default font size

        self.full_load_labels = {
            '其他垃圾': QLabel("其他垃圾:"),
            '厨余垃圾': QLabel("厨余垃圾:"),
            '可回收垃圾': QLabel("可回收垃圾:"),
            '有害垃圾': QLabel("有害垃圾:")
        }

        self.number_of_launch_labels = {
            '其他垃圾': QLabel("投放次数:"),
            '厨余垃圾': QLabel("投放次数:"),
            '可回收垃圾': QLabel("投放次数:"),
            '有害垃圾': QLabel("投放次数:")
        }

        self.captions_label = QLabel("字幕区域")
        self.captions_label.setAlignment(Qt.AlignCenter)
        self.text_label = QLabel('input_text')
        self.text_label.setAlignment(Qt.AlignCenter)

        self.datetime_label = QLabel()
        self.datetime_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.update_datetime()

        self.layout = QVBoxLayout()
        for label in self.full_load_labels.values():
            label.setAlignment(Qt.AlignCenter)  # Align text to center
            self.layout.addWidget(label)
        for label in self.number_of_launch_labels.values():
            label.setAlignment(Qt.AlignCenter)  # Align text to center
            self.layout.addWidget(label)
        self.layout.addWidget(self.text_label)
        self.layout.addWidget(self.captions_label)
        self.layout.addWidget(self.datetime_label)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.data_queue = data_queue
        self.text_queue = text_queue
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.timeout.connect(self.update_datetime)
        self.update_timer.timeout.connect(self.update_text)
        captions_thread = threading.Thread(target=self.display_captions)
        input_text_thread = threading.Thread(target=self.display_input_text)
        captions_thread.start()
        #input_text_thread.start()
        self.update_timer.start(10)  # Simulated data update interval (1 second)

    def update_text(self):
        if self.text_queue:
            try:
                text =self.text_queue.get_nowait()
                self.input_text = text
                self.show_input_text(self.input_text)
            except queue.Empty:
                pass

    def update_display(self):
        if self.data_queue:
            try:
                data = self.data_queue.get_nowait()  # 设置超时时间，避免一直等待
                self.captions = data['captions']
                full_load_data = data['full_load']
                number_of_launch_data = data['number_of_launch']

                for waste_type, label in self.full_load_labels.items():
                    is_full = full_load_data.get(waste_type, False)
                    label.setText(f"{waste_type}: {'满载' if is_full else '未满'}")

                for i, (waste_type, label) in enumerate(self.number_of_launch_labels.items()):
                    launch_count = number_of_launch_data[i]
                    label.setText(f"{waste_type} 投放次数: {launch_count}")

            except queue.Empty:
                pass
        if self.captions:
            pass
    def update_datetime(self):
        current_datetime = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        self.datetime_label.setText(current_datetime)

    def display_captions(self):
        while True:
            if self.captions:
                if len(self.captions) < 30:
                    self.show_caption(self.captions)
                else:
                    segmentation_captions = self.split_string_by_punctuation(self.captions, self.punctuation_marks)
                    for caption in segmentation_captions:
                        self.show_caption(caption)
                self.captions = None

    def display_input_text(self):
        while True:
            if self.input_text:
                self.show_input_text(self.input_text)
                self.input_text = None

    def show_input_text(self, text):
        self.text_label.setText(text)

    def show_caption(self, caption):
        self.captions_label.setText(caption)
        time.sleep(0.24 * len(caption))
        self.captions_label.setText('')

    def split_string_by_punctuation(self, input_string, punctuation_marks):
        result = []
        current_substring = ""

        for char in input_string:
            if char in punctuation_marks:
                if current_substring:
                    result.append(current_substring.strip())
                    current_substring = ""
            else:
                current_substring += char

        if current_substring:
            result.append(current_substring.strip())

        return result


def UIQ_put(UIQ, UIinformation):
    while True:
        time.sleep(1)
        UIQ.put(UIinformation)


if __name__ == "__main__":
    data_queue = multiprocessing.Queue(1)
    data = {
        'full_load': {
            '其他垃圾': False,
            '厨余垃圾': False,
            '可回收垃圾': False,
            '有害垃圾': False},
        'garbage_type': None,
        'if_begin': False,  # 用于两线程的相互阻断
        'triggered_process': 0,  # 获取被触发的模式（视觉1/语音2）
        'number_of_launch': [0, 0, 0, 0],
        'captions': '大家好我是小龙',
        'input_text': '请说话'
    }
    # multiprocessing.set_start_method("spawn") if platform.system() == 'Darwin' else None  # 或 "forkserver
    subprocess = Process(target=UIQ_put, args=(data_queue, data))
    subprocess.start()
    app = QApplication(sys.argv)
    ui = SmartTrashCanUI(data_queue)
    ui.show()
    sys.exit(app.exec_())
