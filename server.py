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
    print(request.json)
    return 'Done'

@app.route("/keyboard", methods=['POST'])
def add_keyboard_music():
    raise NotImplementedError