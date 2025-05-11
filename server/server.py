import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import Flask, request
import numpy as np
import pyaudio
import wave
import utils
import datetime
import pathlib
import logging

root = logging.getLogger()
for handler in root.handlers[:]:
    root.removeHandler(handler)
root.setLevel(logging.CRITICAL)

logger = logging.getLogger("octavio")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(handler)

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

    logger.info(f"MIDI receieved from piano {iid} in session {session_id}")

    session_dir = f'./data/instr_{iid}/session_{session_id}'
    session_exists = os.path.isdir(session_dir)
    os.makedirs(session_dir, exist_ok=True)

    if not session_exists:
        logger.info(f"Session not found, starting one")

        current_date = str(datetime.date.today())
        date_filename = f'{session_dir}/{current_date}.txt'
        pathlib.Path(date_filename).touch()

        midi_filename = f'{session_dir}/running_0.mid'
        utils.deserialize_midi_file(msgs=messages, ticks_per_beat=ticks_per_beat, out_filename=midi_filename)
        logger.info(f"Added starting MIDI to new session")

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
            logger.info(f'{filename} already deleted')

    logger.info(f"Successfully added chunk {chunk} to piano {iid}'s existing session {session_id}")

    utils.display_midi(out_filename)
    return 'Success'

@app.route("/keyboard", methods=['POST'])
def add_keyboard_music():
    raise NotImplementedError
