import pyaudio
import numpy as np
from pydub import AudioSegment
import wave
import os
import time
"""
实时录制音频并保存为MP3文件

参数:
- format_: 音频采样格式，默认为pyaudio.paInt16。
- channels: 音频通道数，默认为1。
- rate: 音频采样率，默认为16000Hz。
- chunk: 音频数据的缓冲区大小，默认为1024。
- output_filename: 输出的音频文件名，默认为"recording.mp3"。
- response_time_threshold: 响应时间阈值，当持续检测到声音超过该阈值的时间时触发响应，默认为0.3秒。
- end_time_threshold: 结束时间阈值，当持续检测到静音超过该阈值的时间时停止录制，默认为1秒。

注意事项:
- 录制过程中，会实时打印当前音量大小。
- 录制结束后，会将音频保存为WAV文件，然后转换为MP3文件。
- 函数将自动停止录制，当连续检测到静音超过结束时间阈值时。

返回值:
- 如果成功保存音频文件，则返回True；否则返回None。
"""


def real_time_recording_of_audio(
        data_outside,
        format_=pyaudio.paInt16,
        channels=1,
        rate=16000,
        chunk=1024,
        output_filename="recording.mp3",
        output_wav="recording.wav",
        response_time_threshold=0.3,
        end_time_threshold=1,
):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=format_, channels=channels,
                        rate=rate, input=True,
                        frames_per_buffer=chunk)
    frames = []
    mute_times = 0
    non_mute_times = 0
    triggered_response_gate = False


    while( not data_outside['if_begin']) or data_outside['triggered_process'] == 2 :
        data = stream.read(chunk)
        audio_data = np.frombuffer(data, dtype=np.int16)
        volume = np.abs(audio_data).mean()
        # print(f"音量大小: {volume}")

        if not triggered_response_gate:
            if volume > 500:
                frames.append(data)
                non_mute_times += 1
            else:
                non_mute_times = 0
                frames.clear()

        if non_mute_times > response_time_threshold * rate / chunk or triggered_response_gate:
            print('触发响应门')
            frames.append(data)
            triggered_response_gate = True

            if volume < 500:
                mute_times += 1
            else:
                mute_times = 0

            if mute_times > end_time_threshold * rate / chunk:
                stream.stop_stream()
                stream.close()
                audio.terminate()

                wave_file = wave.open(output_wav, 'wb')
                wave_file.setnchannels(channels)
                wave_file.setsampwidth(audio.get_sample_size(format_))
                wave_file.setframerate(rate)
                wave_file.writeframes(b''.join(frames))
                wave_file.close()
                print("WAV文件保存成功.")

                audio = AudioSegment.from_wav(output_wav)
                audio.export(output_filename, format="mp3")
                print("MP3文件保存成功."+output_filename)

                return True
    return False


def delete_mp3_files(directory):
    for file in os.listdir(directory):
        if file.endswith(".mp3"):
            file_path = os.path.join(directory, file)
            os.remove(file_path)
            print(f"Deleted file: {file_path}")


def real_time_recording_of_audio_timeout(
        format_=pyaudio.paInt16,
        channels=1,
        rate=16000,
        chunk=1024,
        output_filename="recording.mp3",
        output_wav="recording.wav",
        response_time_threshold=0.3,
        end_time_threshold=1,
        max_waiting_time=10  # 添加最大等待时间
):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=format_, channels=channels,
                        rate=rate, input=True,
                        frames_per_buffer=chunk)
    frames = []
    mute_times = 0
    non_mute_times = 0
    triggered_response_gate = False

    start_time = time.time()  # 记录开始时间

    while True:
        data = stream.read(chunk)
        audio_data = np.frombuffer(data, dtype=np.int16)
        volume = np.abs(audio_data).mean()
        print(f"音量大小: {volume}")

        if not triggered_response_gate:
            if volume > 500:
                frames.append(data)
                non_mute_times += 1
            else:
                non_mute_times = 0
                frames.clear()

        if non_mute_times > response_time_threshold * rate / chunk or triggered_response_gate:
            print('触发响应门')
            frames.append(data)
            triggered_response_gate = True

            if volume < 500:
                mute_times += 1
            else:
                mute_times = 0

            if mute_times > end_time_threshold * rate / chunk:
                stream.stop_stream()
                stream.close()
                audio.terminate()

                wave_file = wave.open(output_wav, 'wb')
                wave_file.setnchannels(channels)
                wave_file.setsampwidth(audio.get_sample_size(format_))
                wave_file.setframerate(rate)
                wave_file.writeframes(b''.join(frames))
                wave_file.close()
                print("WAV文件保存成功.")

                audio = AudioSegment.from_wav(output_wav)
                audio.export(output_filename, format="mp3")
                print("MP3文件保存成功.")

                return True



# 使用函数


if __name__ == '__main__':
    while real_time_recording_of_audio():
        print('finished')
