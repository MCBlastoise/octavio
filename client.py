import RPi.GPIO as GPIO
import pyaudio
import math
import time
import requests
import numpy as np
import os
import utils
import infra
from hardware import OctavioHardware
from basic_pitch import build_icassp_2022_model_path, FilenameSuffix
from basic_pitch.inference import predict_and_save, Model

class OctavioClient:
    format = pyaudio.paInt16
    num_channels = 1
    sampling_rate = 22050
    chunk_secs = 5
    silence_threshold = 10

    privacy_minutes = 30

    temp_dir = './temps'

    server_url = 'http://127.0.0.1:5001'
    endpoint_url = '/piano'
    request_url = f'{server_url}{endpoint_url}'

    audio = pyaudio.PyAudio()

    _tflite_path = build_icassp_2022_model_path(FilenameSuffix.tflite)
    bp_model = Model(_tflite_path)
    
    def __init__(self):
        self.hardware = OctavioHardware()
        self.privacy_last_requested = None
        self.is_recording = True
        self.stream = None
        
        self.session = utils.generate_id()
        self.chunks_sent = 0
        self.silence = 0

        os.makedirs(self.temp_dir, exist_ok=True)

        self.device_index = self.identify_recording_device()

    def create_new_session(self):
        self.session = utils.generate_id()
        self.chunks_sent = 0
        self.silence = 0

    def update_session(self):
        if self.silence >= self.silence_threshold and self.chunks_sent > 0:
            self.create_new_session()

    def refresh_client_state(self):
        self.update_session()

        current_time = time.time()
        if self.hardware.button_pressed:
            self.privacy_last_requested = current_time
            self.create_new_session()
        
        self.is_recording = (
            self.privacy_last_requested is None or
            (current_time - self.privacy_last_requested) / 60 >= self.privacy_minutes
        )
        self.hardware.shine_green() if self.is_recording else self.hardware.shine_red()

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

            return None, pyaudio.paContinue
        
        chunk_frames = int(math.ceil(self.chunk_secs * self.sampling_rate))
        stream = self.audio.open(
                            input=True,
                            input_device_index=self.device_index,
                            format=self.format,
                            channels=self.num_channels,
                            rate=self.sampling_rate,
                            frames_per_buffer=chunk_frames,
                            stream_callback=mic_callback
        )
        return stream
    
    def run(self):
        while True:
            self.refresh_client_state()
            if self.stream is None and self.is_recording:
                self.stream = self.record_audio()
            elif self.stream is not None and not self.is_recording:
                self.stream.close()
                self.stream = None

if __name__ == '__main__':
    try:
        client = OctavioClient()
        client.run()
    except KeyboardInterrupt:
        GPIO.cleanup()