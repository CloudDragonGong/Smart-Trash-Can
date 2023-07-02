from . import stt
from . import tts
from . import real_time_recording_of_audio
from . import response
import pyaudio
from collections.abc import Callable, Iterable, Mapping
from typing import Any
# import stt
# import tts
# import real_time_recording_of_audio
# import response
# from voice_assitant import stt
# from voice_assitant import tts
# from voice_assitant import real_time_recording_of_audio
# from voice_assitant import response
import multiprocessing 
from multiprocessing import Process
class VoiceAssistantStupid(multiprocessing.Process):
    def __init__ (
            self,
            voice_assistant_communication_queue=None,
            information=None,
            format_=pyaudio.paInt16,
            channels=1,
            rate=160000,
            chunk=1024,
            output_filename="voice/recording.mp3",
            output_wav='voice/recording.wav',
            response_time_threshold=0.3,
            end_time_threshold=1,
    ):
        super().__init__()
        self.voice_assistant_communication_queue=voice_assistant_communication_queue
        self.output_filename=output_filename
        self.output_wav=output_wav

    def excute(self,voice_address):
        speech = stt.transform(voice_address)
        response = self.voice_reply(speech=speech)
        print(response)
        response=response+'p[200]'
        tts.transform(response=response)

    def voice_reply(self,speech):
        if '小桶子' in speech:
            return '主人我在,您可以询问我垃圾桶的状况或者是垃圾桶的分类方式。'
        elif '垃圾桶' in speech:
            if '状况' in speech:
                return ('可回收垃圾有' + str(self.information['recyclable trash']) +'个。'
                        +'厨余垃圾有' + str(self.information['Kitchen waste'])+'个。'
                        +'有害垃圾有'+ str(self.information['hazardous waste']) + '个。'
                        +'其他垃圾有'+str(self.information['other garbage'])+'个。'
                        +'所有垃圾的总数是'+str(self.information['TotalNumber'])+'个。'
                        +'垃圾桶的满载情况是'+ '满载。' if self.information['fullLoadGarbage']!=None else '未满载。' 
                )
            elif '多少' in speech:
                if '可回收垃圾' in speech:
                    return '可回收垃圾有' + str(self.information['recyclable trash']) +'个。'
                elif '厨余垃圾' in speech:
                    return '厨余垃圾有' + str(self.information['Kitchen waste'])+'个。'
                elif '有害垃圾' in speech:
                    return '有害垃圾有'+ str(self.information['hazardous waste']) + '个。'
                elif '其他垃圾' in speech:
                    return '其他垃圾有'+str(self.information['other garbage'])+'个。'
            elif '满载' in speech:
                return '垃圾桶的满载情况是'+ '满载。' if self.information['fullLoadGarbage']!=None else '未满载。' 
            elif '分类' in speech:
                return '可回收垃圾例如：纸张和纸板，塑料瓶和容器，金属罐和铝箔，玻璃瓶和容器，建筑材料（例如，废木材、砖块）。厨余垃圾（湿垃圾）例如：食物残渣和剩饭剩菜，水果和蔬菜的残余，茶叶渣和咖啡渣，植物的枝叶和花朵。有害垃圾例如：废电池过期的药品，化学品和清洁剂，汽车废油和润滑剂，染发剂和美容产品.其他垃圾（干垃圾）例如：烟蒂和口香糖，硬贝壳（例如螺丝、螺帽），旧衣物和鞋子，塑料袋和包装膜，破碎的陶瓷和玻璃制品'
        else:
            #return '主人，我不明白你的意思'
            return '.'        
        
    def run(self):
        while True:
            if (real_time_recording_of_audio.real_time_recording_of_audio(output_filename=self.output_filename,output_wav=self.output_wav)):
                if (self.voice_assistant_communication_queue !=None) :
                    self.information=self.voice_assistant_communication_queue.get()
                else:
                    self.information={
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
                self.excute(self.output_filename)


if __name__ == '__main__':
    assistant = VoiceAssistantStupid(output_filename='voice/recording.mp3',output_wav='voice/recording.wav')
    assistant.start()
    assistant.join()
    print('ok')
    # voice_assist=voice_assistant_stupid.VoiceAssistantStupid(voice_assistant_communication_queue=voice_assistant_communication_queue)
    # voice_assist.start()
     