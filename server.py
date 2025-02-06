from flask import Flask, request
import numpy as np
import pyaudio
import wave
from utils import save_frames_to_file

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