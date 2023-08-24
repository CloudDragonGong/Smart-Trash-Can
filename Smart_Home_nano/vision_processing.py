import cv2
import numpy as np
import time
from processing import Processing


class VisionProcessing(Processing):
    def __init__(
            self,
            resnet,
            **kwargs,
    ):
        super(VisionProcessing, self).__init__(**kwargs)
        self.resnet = resnet
        self.frame = None
        self.cap = None
        self.mp3_filename = {
            '其他垃圾': r'voice/其他垃圾.mp3',
            '可回收垃圾': r'voice/可回收垃圾.mp3',
            '厨余垃圾': r'voice/厨余垃圾.mp3',
            '有害垃圾': r'voice/有害垃圾.mp3'
        }
        self.background = None

    def init_background(self):
        self.open_camera()
        self.background = self.frame
        self.close_camera()

    def open_camera(self):
        self.cap = cv2.VideoCapture(0)
        _, self.frame = self.cap.read()
        try:
            cv2.imwrite('test_cap.png', self.frame)
            return True
        except:
            return False

    def close_camera(self):
        self.cap.release()

    def detect_object_in_frame(self, background, current_frame, threshold=100):
        diff = cv2.absdiff(background, current_frame)
        _, diff_thresholded = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
        diff_count = np.count_nonzero(diff_thresholded)
        print('*****************************'+str(diff_count) + '**************************')
        return diff_count > 0

    def classifier(self):

        flag = self.resnet.classify(self.frame)
        if flag == 0:
            self.garbage_type = "其他垃圾"
        elif flag == 1:
            self.garbage_type = "厨余垃圾"
        elif flag == 2:
            self.garbage_type = "可回收垃圾"
        elif flag == 3:
            self.garbage_type = "有害垃圾"
        else:
            self.garbage_type = None
        print(self.garbage_type)

        if flag in [0, 1, 2, 3]:
            return True
        else:
            return False

    def update_data(self):
        self.data['garbage_type'] = self.garbage_type

    def identify(self):
        while not self.data['if_begin']:
            if self.open_camera() and self.detect_object_in_frame(self.background, self.frame) and self.classifier():
                cv2.imwrite('cap.png', self.frame)
                self.close_camera()
                self.data['if_begin'] = True
                self.data['triggered_process'] = 1
                return True
            else:
                pass

    def process_image(self):
        gray_image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_image, threshold1=30, threshold2=70)
        _, binary_image = cv2.threshold(edges, 128, 255, cv2.THRESH_BINARY)
        black_pixel_count = np.sum(binary_image == 0)
        return black_pixel_count

    def run(self):
        self.update_captions(self.garbage_type)
        self.data['number_of_launch'][int(self.garbage_type_str_to_num[self.garbage_type])] = \
            self.data['number_of_launch'][int(self.garbage_type_str_to_num[self.garbage_type])] + 1
        self.embedded_info_transfer(1, self.message_open_can[self.garbage_type])
        self.embedded_info_recv()
        self.UI_info_transfer()
        self.update_data()
        time.sleep(1)
        self.server_info_transfer(messages=['update data', self.data])
        print('vision_processing is done')
