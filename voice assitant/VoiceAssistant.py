import stt
import tts
import time
import re
import real_time_recording_of_audio
import response
import multiprocessing
import pyaudio
import numpy as np
from pydub import AudioSegment
import wave
import os
import openai

class VoiceAssistant(multiprocessing.Process):
    def __init__ (self,format_=pyaudio.paInt16,channels=1,rate=44100,chunk=1024,output_filename="recording.mp3",response_time_threshold=0.3,end_time_threshold=1):
        super().__init__()
        self.format__=format_
        self.channels=channels
        self.rate=rate
        self.chunk=chunk
        self.output_filename=output_filename
        self.voice_address=output_filename
        self.response_time_threshold=response_time_threshold
        self.end_time_threshold=end_time_threshold

    def run(self):
        while True:
            if(real_time_recording_of_audio.real_time_recording_of_audio()):
                response.excute(self.voice_address)
                real_time_recording_of_audio.delete_mp3_files('.')
                

if __name__ == '__main__':
    voice_assistant = VoiceAssistant()
    voice_assistant.start()
    voice_assistant.join()
    print('ok')