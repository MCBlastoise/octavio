import pyaudio
import math
import time
import requests
import numpy as np
from email.utils import formatdate

def identify_recording_device(audio_inst):
    print("----------------------Recording device list---------------------")

    info = audio_inst.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    for i in range(0, num_devices):
        if (audio_inst.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", audio_inst.get_device_info_by_host_api_device_index(0, i).get('name'))
    print("-------------------------------------------------------------")

    device_index = int(input())
    return device_index

def record_audio(format, num_channels, sampling_rate, chunk_secs):
    audio = pyaudio.PyAudio()
    server_url = 'http://127.0.0.1:5000'
    endpoint_url = '/piano'
    request_url = f'{server_url}{endpoint_url}'

    def mic_callback(input_data, frame_count, time_info, flags):
        current_ts = formatdate(timeval=time.time()-chunk_secs, localtime=False, usegmt=True)
        headers = {
            'Content-Type': 'application/octet-stream',
            'Date': current_ts
        }
        r = requests.post(
            request_url,
            data=input_data,
            headers=headers
        )
        return None, pyaudio.paContinue
    
    chunk_frames = int(math.ceil(chunk_secs * sampling_rate))
    device_index = identify_recording_device(audio_inst=audio)
    stream = audio.open(
                        input=True,
                        input_device_index=device_index,
                        format=FORMAT,
                        channels=num_channels,
                        rate=sampling_rate,
                        frames_per_buffer=chunk_frames,
                        stream_callback=mic_callback
    )
    print ("Recording started")

    while stream.is_active():
        pass

if __name__ == '__main__':
    FORMAT = pyaudio.paInt16
    NUM_CHANNELS = 1
    SAMPLING_RATE = 22050
    CHUNK_SECS = 10
    
    record_audio(format=FORMAT, num_channels=NUM_CHANNELS, sampling_rate=SAMPLING_RATE, chunk_secs=CHUNK_SECS)