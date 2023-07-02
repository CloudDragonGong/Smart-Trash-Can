from . import stt
from . import tts
from . import real_time_recording_of_audio
from . import response
# import stt
# import tts
# import real_time_recording_of_audio
# import response


import time
import re
import multiprocessing
import pyaudio
import numpy as np
from pydub import AudioSegment
import wave
import os
import openai

class VoiceAssistant(multiprocessing.Process):
    def __init__ (self,gpt_key,voice_assistant_communication_queue,information=None,format_=pyaudio.paInt16,channels=1,rate=160000,chunk=1024,output_filename="recording.mp3",output_wav='recording.wav',response_time_threshold=0.3,end_time_threshold=1):
        super().__init__()
        self.gpt_key= gpt_key
        self.format__=format_
        self.channels=channels
        self.rate=rate
        self.chunk=chunk
        self.output_filename=output_filename
        self.voice_address=output_filename
        self.output_wav=output_wav
        self.response_time_threshold=response_time_threshold
        self.end_time_threshold=end_time_threshold
        self.information=information
        self.voice_assistant_communication_queue=voice_assistant_communication_queue

    def run(self):
        while True:
            if(real_time_recording_of_audio.real_time_recording_of_audio(output_filename=self.output_filename,output_wav=self.output_wav)):
                response.excute(self.voice_address,gpt_key=self.gpt_key,information=self.voice_assistant_communication_queue.get())
                real_time_recording_of_audio.delete_mp3_files('./voice')
                
# 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
if __name__ == '__main__':
    UIinformation = {
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
    voice_assistant = VoiceAssistant(gpt_key="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",information=UIinformation)
    voice_assistant.start()
    voice_assistant.join()
    print('ok')