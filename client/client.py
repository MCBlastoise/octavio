import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import log_utils
import logging
# import RPi.GPIO as GPIO
import pyaudio
import math
import time
import requests
import numpy as np
import shutil
import infra
from hardware import OctavioHardware
import utils
with log_utils.no_stderr():
    from basic_pitch import build_icassp_2022_model_path, FilenameSuffix
    from basic_pitch.inference import predict_and_save, Model

root = logging.getLogger()
for handler in root.handlers[:]:
    root.removeHandler(handler)
root.setLevel(logging.CRITICAL)

logger = logging.getLogger("octavio")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(handler)

class OctavioClient:
    format = pyaudio.paInt16
    num_channels = 1
    sampling_rate = 22050
    chunk_secs = 30
    session_cap_minutes = 45
    silence_threshold = 10
    privacy_minutes = 30
    num_server_attempts = 3
    server_retry_wait_seconds = 15
    server_failure_wait_seconds = 60

    temp_dir = './temps'

    # server_url = 'http://127.0.0.1:5001'
    server_url = 'http://octavio-server.mit.edu:5001'
    endpoint_url = '/piano'
    request_url = f'{server_url}{endpoint_url}'

    with log_utils.no_stderr():
        audio = pyaudio.PyAudio()

    _tflite_path = build_icassp_2022_model_path(FilenameSuffix.tflite)
    bp_model = Model(_tflite_path)

    def __init__(self):
        self.privacy_last_requested = None
        self.is_recording = True
        self.stream = None

        self.session = utils.generate_id()
        self.chunks_sent = 0
        self.silence = 0
        self.end_stream_flag = False

        if os.path.isdir(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.temp_dir, exist_ok=True)

        logger.info("AMT model attempting to warm up")

        warmup_frames = np.zeros(self.sampling_rate)
        warmup_filename = f'{self.temp_dir}/warmup.wav'
        utils.save_frames_to_file(warmup_frames, warmup_filename)
        warmup_midi = utils.convert_to_midi_bp(input_audio=warmup_filename, output_dir=self.temp_dir, bp_model=self.bp_model)
        os.remove(warmup_midi)

        logger.info("AMT model successfully warmed up")

        try:
            self.device_index = infra.RECORDING_DEVICE_INDEX
        except NameError:
            self.device_index = self.identify_recording_device()

        self.hardware = OctavioHardware()

        logger.info("System initialized successfully")

    def create_new_session(self):
        session_id = utils.generate_id()
        logger.info(f"Creating new session {self.session}")

        self.session = session_id
        self.chunks_sent = 0
        self.silence = 0



    def end_stream(self):
        self.create_new_session()

        logger.info("System closing audio stream")
        self.stream.close()
        self.stream = None

    def update_session(self, current_time):
        session_duration = (self.chunks_sent * self.chunk_secs) / 60
        if (
            (self.silence >= self.silence_threshold and self.chunks_sent > 0) or
            (session_duration >= self.session_cap_minutes)
        ):
            self.end_stream_flag = True
        elif self.hardware.button_pressed:
            self.privacy_last_requested = current_time
            logger.info(f"User requested privacy")
            self.end_stream_flag = True

    def refresh_client_state(self):
        current_time = time.time()
        self.update_session(current_time)

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
            logger.info("Attempting to extract MIDI")
            midi_info = utils.extract_midi(input_data=input_data, bp_model=self.bp_model, temp_dir=self.temp_dir)
            logger.info("MIDI extracted")

            if midi_info['is_empty']:
                logger.info("MIDI was empty, nothing sent")
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

            logger.info("Attempting to transmit MIDI")

            for i in range(self.num_server_attempts):
                try:
                    r = requests.post(
                        self.request_url,
                        json=request_data,
                        headers=headers
                    )
                except Exception as e:
                    logger.info(f"Failed attempt {i + 1} to contact server with request, retrying...")
                    time.sleep(self.server_retry_wait_seconds)
                else:
                    logger.info("MIDI transmitted successfully")
                    self.chunks_sent += 1
                    return None, pyaudio.paContinue

            logger.info("Failed to contact server with request. Restarting...")
            time.sleep(self.server_failure_wait_seconds)
            self.end_stream_flag = True


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
                logger.info("System starting a new audio stream")
                self.stream = self.record_audio()
            elif self.end_stream_flag:
                self.end_stream_flag = False
                self.end_stream()

if __name__ == '__main__':
    ...

    client = OctavioClient()
    client.run()
