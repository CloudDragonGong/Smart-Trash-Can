import cv2
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
            '其他垃圾': r'',
            '可回收垃圾': r'',
            '厨余垃圾': r'',
            '有害垃圾': r''
        }

    def open_camera(self):
        self.cap = cv2.VideoCapture(0)
        _, self.frame = self.cap.read()

    def close_camera(self):
        self.cap.release()

    def classifier(self):
        flag = self.resnet.classify(self.frame)
        if flag == 0:
            self.garbage_type = "其他垃圾"
        if flag == 1:
            self.garbage_type = "厨余垃圾"
        if flag == 2:
            self.garbage_type = "可回收垃圾"
        if flag == 3:
            self.garbage_type = "有害垃圾"
        else:
            self.garbage_type = None
        if flag in [0, 1, 2, 3]:
            return True
        else:
            return False

    def update_data(self):
        self.data['garbage_type'] = self.garbage_type

    def identify(self):
        # continuous identify
        while not self.data['if_begin']:
            print('camera is working')
            self.open_camera()
            if self.classifier():
                self.close_camera()
                self.data['if_begin'] = True
                self.data['triggered_process'] = 1
                return True
            else:
                pass

    def run(self):
        self.embedded_info_transfer(1, self.message_open_can[self.garbage_type])
        self.embedded_info_recv()
        self.UI_info_transfer()
        self.update_data()
        self.audio_play(self.mp3_filename[self.garbage_type])
        self.server_info_transfer(messages=['update data', self.data])
        print('vision_processing is done')
