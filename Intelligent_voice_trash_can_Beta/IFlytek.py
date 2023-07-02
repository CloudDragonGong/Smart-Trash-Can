import time
import urllib.request
import urllib.parse
import json
import hashlib
import base64
import multiprocessing
from voice_assitant.real_time_recording_of_audio import real_time_recording_of_audio
from voice_assitant import stt
from voice_assitant import tts


# 接口地址
url = "http://ltpapi.xfyun.cn/v1/ke"
# 开放平台应用ID
x_appid = "0c946150"
# 开放平台应用接口秘钥
api_key = "dd56dd6e1b3116009b5f819274539c8f"


class IFlytek_assistant(multiprocessing.Process):
    def __init__(
        self,
        output_filename,
        output_wav,
        question_file_path,
        answer_file_path,
        keywords_file_path,
        if_need_update_keywords=True,
        voice_assistant_communication_queue=None,
    ):
        super().__init__()
        self.output_filename = output_filename
        self.output_wav = output_wav
        self.voice_assistant_communication_queue = voice_assistant_communication_queue
        self.answer_file_path = answer_file_path
        self.keywords_file_path=keywords_file_path
        self.list = []
        self.list = self.read_text_file_n(question_file_path)
        print('read over')
        if if_need_update_keywords :self.keywords_of_mate()
        else: self.list_key=self.read_txt_to_list_of_lists(self.keywords_file_path)

    # 输入text，返回关键字列表
    @staticmethod
    def extract_keywords(text):
        body = urllib.parse.urlencode({"text": text}).encode("utf-8")
        param = {"type": "dependent"}
        x_param = base64.b64encode(json.dumps(param).replace(" ", "").encode("utf-8"))
        x_time = str(int(time.time()))
        x_checksum = hashlib.md5(
            api_key.encode("utf-8") + str(x_time).encode("utf-8") + x_param
        ).hexdigest()
        x_header = {
            "X-Appid": x_appid,
            "X-CurTime": x_time,
            "X-Param": x_param,
            "X-CheckSum": x_checksum,
        }
        req = urllib.request.Request(url, body, x_header)
        result = urllib.request.urlopen(req)
        result = result.read().decode("utf-8")
        data = json.loads(result)["data"]
        keywords = [item["word"] for item in data["ke"]]
        return keywords

    # 输入路径，返回字符串内容
    @staticmethod
    def read_text_file(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return content

    @staticmethod
    def read_text_file_n(file_path):
        lines = []
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                lines.append(line.strip())
        return lines

    # 返回相似度是否大于90
    @staticmethod
    def check_similarity(list1, list2):
        if len(list1) != len(list2):
            return False

        total_items = len(list1)
        matching_items = 0

        for item in list1:
            if item in list2:
                matching_items += 1

        similarity_percentage = (matching_items / total_items) * 100

        if similarity_percentage >= 90:
            return True
        else:
            return False

    # 返回配对的下标
    @staticmethod
    def find_matching_index(list_1, list_2):
        overlap=0
        index=0
        for i, sublist in enumerate(list_1):
            intersection = set(sublist) & set(list_2)
            overlap_n = len(intersection) / len(sublist)  # 计算重合率
            if overlap<overlap_n:
                index=i
                overlap=overlap_n
        if overlap >= 0.6:
            return index
        return None

    # 生成关键字配对的列表
    def keywords_of_mate(self):
        self.list_key = [self.extract_keywords(item) for item in self.list]
        self.write_list_of_lists_to_txt(self.list_key,file_path=self.keywords_file_path)

    # 返回回复
    def response(self, text):
        keywords_of_input = self.extract_keywords(text=text)
        index = self.find_matching_index(self.list_key, keywords_of_input)
        if index == None:
            return "不好意思主人，我不明白你在说什么"
        return self.read_line(self.answer_file_path,index)

    # 生成垃圾桶的满载情况
    def analysis_full_load_state(self):

        ## 可回收 厨余垃圾 有害垃圾 其他垃圾
        self.full_load_state = ["未满载", "未满载", "未满载", "未满载"]
   
        if self.information["fullLoadGarbage20s"] == True:
            if self.information["fullLoadGarbage"][2] == True:
                self.full_load_state[0] = "满载"
            else:
                self.full_load_state[0] = "未满载"

            if self.information["fullLoadGarbage"][1] == True:
                self.full_load_state[1] = "满载"
            else:
                self.full_load_state[1] = "未满载"

            if self.information["fullLoadGarbage"][3] == True:
                self.full_load_state[2] = "满载"
            else:
                self.full_load_state[2] = "未满载"

            if self.information["fullLoadGarbage"][0] == True:
                self.full_load_state[3] = "满载"
            else:
                self.full_load_state[3] = "未满载"
        else:
            if self.information["fullLoadGarbage"] == None:
                pass

            elif self.information["fullLoadGarbage"] == 2:
                self.full_load_state[0] = "未满载"

            elif self.information["fullLoadGarbage"] == 1:
                self.full_load_state[1] = "未满载"

            elif self.information["fullLoadGarbage"] == 3:
                self.full_load_state[2] = "未满载"

            elif self.information["fullLoadGarbage"] == 0:
                self.full_load_state[3] = "未满载"

            elif self.information["fullLoadGarbage"] == 12:
                self.full_load_state[0] = "满载"

            elif self.information["fullLoadGarbage"] == 11:
                self.full_load_state[1] = "满载"

            elif self.UIinformation["fullLoadGarbage"] == 13:
                self.full_load_state[2] = "满载"

            elif self.UIinformation["fullLoadGarbage"] == 10:
                self.full_load_state[3] = "满载"

    # 返回语音
    def excute(self, voice_address):
        speech = stt.transform(voice_address)
        response = self.response(text=speech)
        print(self.information)
        response = response.format(information=self.information,full_load_state=self.full_load_state)
        print(response)
        response = response + "。p[200]"
        tts.transform(response=response)

    @staticmethod
    # 读取txt文件中特定的行
    def read_line(file_path, line_number):
        with open(file_path, "r",encoding='utf-8') as file:
            lines = file.readlines()
            if 0 <= line_number < len(lines):
                return lines[line_number].strip()
            else:
                return None
    @staticmethod
    def write_list_of_lists_to_txt(data, file_path):
        with open(file_path, "w",encoding="utf-8") as file:
            for line in data:
                file.write(" ".join(line) + "\n")

    @staticmethod
    def read_txt_to_list_of_lists(file_path):
        data = []
        with open(file_path, "r",encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if line:
                    data.append(line.split(" "))
        return data

    def run(self):
        while True:
            if real_time_recording_of_audio(
                output_filename=self.output_filename, output_wav=self.output_wav
            ):
                
                if self.voice_assistant_communication_queue != None:
                    self.information = self.voice_assistant_communication_queue.get()
                else:
                    self.information = {
                        "garbageCategory": None,
                        "fullLoad": False,
                        "ifSuccess": False,
                        "TotalNumber": 0,
                        "Kitchen waste": 0,
                        "recyclable trash": 0,
                        "hazardous waste": 0,
                        "other garbage": 0,
                        "serialOfGarbage": None,
                        "ifBegin": False,
                        "fullLoadGarbage": None,
                        "fullLoadGarbage20s": False,
                        "countDown": 0,
                    }
                self.analysis_full_load_state()#解析满载情况
                self.excute(self.output_filename)


if __name__ == "__main__":
    assistant = IFlytek_assistant(
        r"voice/response.mp3",
        r"voice/response.wav",
        r"docs/questions.txt",
        r"docs/answers.txt",
        r"docs/keywords.txt",
        if_need_update_keywords=False       
    )
    assistant.start()
