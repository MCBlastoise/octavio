from flask import Flask, request
import numpy as np
import pyaudio
import wave

def save_frames_to_file(frame_data, filename):
    audio = pyaudio.PyAudio()
    FORMAT = pyaudio.paInt16
    SAMPLING_RATE = 22050
    NUM_CHANNELS = 1

    waveFile = wave.open(filename, 'wb')
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setnchannels(NUM_CHANNELS)
    waveFile.setframerate(SAMPLING_RATE)
    waveFile.writeframes(bytes(frame_data))
    waveFile.close()

app = Flask(__name__)
file_counter = 0

@app.route("/")
def hello_world():
    return 'Bingo'

@app.route("/piano", methods=['POST'])
def add_piano_music():
    global file_counter

    output_prefix = 'test_out'
    
    reconstructed_arr = np.frombuffer(request.data, dtype=np.float32)
    filename = f'{output_prefix}{file_counter}.wav'
    save_frames_to_file(frame_data=reconstructed_arr, filename=filename)
    file_counter += 1

@app.route("/keyboard", methods=['POST'])
def add_keyboard_music():
    raise NotImplementedError