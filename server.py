from flask import Flask, request
import numpy as np
import pyaudio
import wave
import utils
import datetime
import os
import pathlib

app = Flask(__name__)
file_counter = 0

@app.route("/")
def hello_world():
    return 'Bingo'

@app.route("/piano", methods=['POST'])
def add_piano_music():
    j = request.json

    iid = j['instrument_id']
    session_id = j['session_id']
    chunk = j['chunk']
    messages = j['messages']
    ticks_per_beat = j['ticks_per_beat']

    session_dir = f'./data/instr_{iid}/session_{session_id}'
    session_exists = os.path.isdir(session_dir)
    os.makedirs(session_dir, exist_ok=True)

    if not session_exists:
        current_date = str(datetime.date.today())
        date_filename = f'{session_dir}/{current_date}.txt'
        pathlib.Path(date_filename).touch()

        midi_filename = f'{session_dir}/running_0.mid'
        utils.deserialize_midi_file(msgs=messages, ticks_per_beat=ticks_per_beat, out_filename=midi_filename)

        return 'Success'
    
    files = os.listdir(session_dir)
    running_mid_filename = next( (file for file in files if file.startswith('running') and file.endswith('.mid')), None )

    if running_mid_filename is None:
        return 'Failure'

    running_mid_filepath = f'{session_dir}/{running_mid_filename}'
    temp_mid_filepath = f'{session_dir}/temp_{chunk}.mid'
    out_filename = f'{session_dir}/running_{chunk}.mid'

    utils.deserialize_midi_file(msgs=messages, ticks_per_beat=ticks_per_beat, out_filename=temp_mid_filepath)
    utils.combine_midi(running_mid_filepath, temp_mid_filepath, output_filename=out_filename)

    for filename in (running_mid_filepath, temp_mid_filepath):
        try:
            os.remove(filename)
        except FileNotFoundError:
            print(f'{filename} already deleted')

    utils.display_midi(out_filename)
    return 'Success'

@app.route("/keyboard", methods=['POST'])
def add_keyboard_music():
    raise NotImplementedError