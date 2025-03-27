import pyaudio
import math
import time
import requests
import numpy as np
# import random
# from email.utils import formatdate
import os
import utils
import infra

class OctavioClient:
    format = pyaudio.paInt16
    num_channels = 1
    sampling_rate = 22050
    chunk_secs = 5
    silence_threshold = 10

    server_url = 'http://127.0.0.1:5000'
    endpoint_url = '/piano'
    request_url = f'{server_url}{endpoint_url}'

    audio = pyaudio.PyAudio()
    
    def __init__(self):
        self.session = utils.generate_id()
        self.chunks_sent = 0
        self.silence = 0

    def create_new_session(self):
        self.session = utils.generate_id()
        self.chunks_sent = 0
        self.silence = 0

    def update_session(self):
        if self.silence >= self.silence_threshold and self.chunks_sent > 0:
            self.create_new_session()

    def identify_recording_device(self):
        print("----------------------Recording device list---------------------")

        info = self.audio.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        for i in range(0, num_devices):
            if (self.audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print("Input Device id ", i, " - ", self.audio.get_device_info_by_host_api_device_index(0, i).get('name'))
        print("-------------------------------------------------------------")

        device_index = int(input())
        return device_index

    def record_audio(self):
        def mic_callback(input_data, frame_count, time_info, flags):
            midi_info = utils.extract_midi(input_data=input_data)
            if midi_info['is_empty']:
                print("EMPTY FOUND")
                self.silence += self.chunk_secs
                return None, pyaudio.paContinue
            else:
                self.silence = 0

            request_data = {
                'instrument_id': infra.INSTRUMENT_ID,
                'session_id': self.session,
                'chunk': self.chunks_sent,
                **midi_info
            }
            headers = {
                'Content-Type': 'application/json'
            }
            r = requests.post(
                self.request_url,
                json=request_data,
                headers=headers
            )
            self.chunks_sent += 1

            # current_ts = formatdate(timeval=time.time()-chunk_secs, localtime=False, usegmt=True)
            # headers = {
            #     'Content-Type': 'application/octet-stream',
            #     'Date': current_ts
            # }
            # r = requests.post(
            #     request_url,
            #     data=input_data,
            #     headers=headers
            # )
            return None, pyaudio.paContinue
        
        chunk_frames = int(math.ceil(self.chunk_secs * self.sampling_rate))
        device_index = self.identify_recording_device()
        stream = self.audio.open(
                            input=True,
                            input_device_index=device_index,
                            format=self.format,
                            channels=self.num_channels,
                            rate=self.sampling_rate,
                            frames_per_buffer=chunk_frames,
                            stream_callback=mic_callback
        )
        print ("Recording started")

        while stream.is_active():
            pass
            
            # self.update_session()

if __name__ == '__main__':
    client = OctavioClient()
    client.record_audio()