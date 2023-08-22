import cv2
import numpy as np

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

    def open_camera(self):
        self.cap = cv2.VideoCapture(0)
        _, self.frame = self.cap.read()
        try:
            cv2.imwrite('test_cap.png', self.frame)
            return True
        except:
            #print('************error of camera****************')
            return False

    def close_camera(self):
        self.cap.release()

    def classifier(self):
        flag = self.resnet.classify(self.frame)
        #print(f'flag= {flag}')
        if flag == 0:
            self.garbage_type = "其他垃圾"
        elif flag == 1:
            self.garbage_type = "厨余垃圾"
        elif flag == 2:
            self.garbage_type = "可回收垃圾"
        elif flag == 3:
            # if type is harmful waste , calculate the pixel
            pixel_count = self.process_image()
            print(pixel_count)
            if pixel_count > 310000:
                self.garbage_type = "有害垃圾"
            else:
                self.garbage_type = None
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
        #print(f"begin state:{self.data['if_begin']}")
        # continuous identify
        while not self.data['if_begin']:
            if self.open_camera() and self.classifier():
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
        self.server_info_transfer(messages=['update data', self.data])
        print('vision_processing is done')
