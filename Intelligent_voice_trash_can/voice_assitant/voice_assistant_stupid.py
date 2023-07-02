# from . import stt
# from . import tts
# from . import real_time_recording_of_audio
# from . import response
import pyaudio
from collections.abc import Callable, Iterable, Mapping
from typing import Any
import stt
import tts
import real_time_recording_of_audio
import response
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
            output_filename="recording.mp3",
            output_wav='recording.wav',
            response_time_threshold=0.3,
            end_time_threshold=1,
    ):
        super().__init__()
        self.output_filename=output_filename
        self.output_wav=output_wav

    def excute(self,voice_address):
        speech = stt.transform(voice_address)
        response = self.voice_reply(speech=speech)
        print(response)
        tts.transform(response=response)

    def voice_reply(self,speech):
        if '嘿，小桶' in speech:
            return '我在'
        
    def run(self):
        while True:
            if (real_time_recording_of_audio.real_time_recording_of_audio(output_filename=self.output_filename,output_wav=self.output_wav)):
                    self.excute(self.output_filename)


if __name__ == '__main__':
     assistant = VoiceAssistantStupid()
     assistant.start()
     assistant.join()
     print('ok')
