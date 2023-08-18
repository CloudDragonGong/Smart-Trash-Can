import time

from processing import Processing


class AudioProcessing(Processing):
    def __init__(
            self,
            garbage_type,
            **kwargs
    ):
        super(AudioProcessing, self).__init__(**kwargs)
        self.garbage_type = garbage_type

    def update_data(self):
        self.data['garbage_type'] = self.garbage_type

    # def server_info_recv(self):
    #     flag = int(self.client.receive_string())
    #     garbage_type_list = ['其他垃圾','厨余垃圾','可回收垃圾','有害垃圾']
    #     self.garbage_type=garbage_type_list[flag]

    def run(self):
        self.embedded_info_transfer(1, self.message_open_can[self.garbage_type])
        self.embedded_info_recv()
        self.update_data()
        self.UI_info_transfer()
        time.sleep(1)
        self.server_info_transfer(messages=['update data', self.data])
