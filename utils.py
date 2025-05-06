import log_utils
import numpy as np
import pyaudio
import wave
from scipy.io.wavfile import read
import shlex
import subprocess
import mido
import random
import shutil
from pathlib import Path
import os
with log_utils.no_stderr():
    from basic_pitch.inference import predict_and_save

def generate_id():
    return ''.join([str(random.randint(0, 9)) for _ in range(8)])

def wav_to_np(wav_filename):
    file_contents = read(wav_filename)
    file_data = np.array(file_contents[1])
    return file_data

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

# def convert_to_midi(input_audio, output_filename, ignore_warnings=True):
#     command = f'transkun {input_audio} {output_filename}'
#     command_args = shlex.split(command)
#     if ignore_warnings:
#         subprocess.run(command_args, stderr=subprocess.DEVNULL)
#     else:
#         subprocess.run(command_args)

def convert_to_midi_bp(input_audio, output_dir, bp_model):
    audio_files = [input_audio]
    predict_and_save(
        audio_path_list=audio_files,
        output_directory=output_dir,
        save_midi=True,
        sonify_midi=False,
        save_model_outputs=False,
        save_notes=False,
        model_or_model_path=bp_model,

        minimum_frequency=27.5,
        maximum_frequency=4186,

        onset_threshold=0.7,
        frame_threshold=0.5
    )
    bp_out_path = f'{str(Path(input_audio).with_suffix(""))}_basic_pitch.mid'
    # target_path = f'{str(Path(input_audio).with_suffix(""))}.mid'
    # os.rename(bp_out_path, target_path)
    return bp_out_path

def display_midi(midi_filename):
    mid = mido.MidiFile(midi_filename)
    for msg in mid:
        print(msg)

def combine_midi(midi_filename1, midi_filename2, output_filename):
    START_END_THRESHOLD = 0.25

    mid1 = mido.MidiFile(midi_filename1)
    mid1.tracks = [mido.merge_tracks(mid1.tracks)]

    mid2 = mido.MidiFile(midi_filename2)
    mid2.tracks = [mido.merge_tracks(mid2.tracks)]

    output_mid = mido.MidiFile(midi_filename1)
    track = mido.MidiTrack()
    output_mid.tracks = [track]

    idxs_1 = set()
    notes_1 = set()
    idxs_2 = set()
    notes_2 = set()

    # Extract clipped notes from beginning of second file
    t = 0
    for idx, msg in enumerate(mid2):
        t += msg.time
        if t > START_END_THRESHOLD:
            break

        if msg.type == 'note_on' and msg.velocity != 0:
            notes_2.add(msg.note)
            idxs_2.add(idx)

    # Extract clipped notes from end of first file
    msgs = list(mid1)[::-1]
    t = 0
    for idx, msg in enumerate(msgs[1:], start=1):
        prev_msg = msgs[idx - 1]
        t += prev_msg.time

        if t > START_END_THRESHOLD:
            break

        if msg.type == 'note_on' and msg.velocity == 0:
            front_idx = len(msgs) - 1 - idx
            idxs_1.add(front_idx)
            notes_1.add(msg.note)

    for idx, msg in enumerate(mid1.tracks[0]):
        excluded_note = idx in idxs_1 and msg.note in notes_2
        if msg.type == 'end_of_track' or excluded_note:
            continue
        new_msg = msg.copy()
        track.append(new_msg)

    lost_time = 0
    for idx, msg in enumerate(mid2.tracks[0]):
        excluded_note = idx in idxs_2 and msg.note in notes_1
        if msg.is_meta or excluded_note:
            lost_time += msg.time
            continue
        new_msg = msg.copy()
        if lost_time > 0:
            new_msg.time += lost_time
            lost_time = 0
        track.append(new_msg)

    output_mid.save(output_filename)

def extract_midi(input_data, bp_model, temp_dir='./temps'):
        temp_id = generate_id()
        unique_temp_dir = f'{temp_dir}/{temp_id}'
        os.makedirs(unique_temp_dir, exist_ok=True)

        wav_filename = f'{unique_temp_dir}/{temp_id}.wav'
        # mid_filename = f'{unique_temp_dir}/{temp_id}.mid'

        save_frames_to_file(frame_data=input_data, filename=wav_filename)

        print("Frames saved to file")

        # convert_to_midi(input_audio=wav_filename, output_filename=mid_filename)
        mid_filename = convert_to_midi_bp(input_audio=wav_filename, output_dir=unique_temp_dir, bp_model=bp_model)

        print("Converted to MIDI")

        empty = midi_is_empty(midi_filename=mid_filename)

        serialized_msgs, tpb = serialize_midi_file(midi_filename=mid_filename)
        midi_info = {
            'ticks_per_beat': tpb,
            'messages': serialized_msgs,
            'is_empty': empty
        }

        try:
            shutil.rmtree(unique_temp_dir)
        except FileNotFoundError:
            print(f'{unique_temp_dir} already deleted')

        # for filename in (wav_filename, mid_filename):
        #     try:
        #         os.remove(filename)
        #     except FileNotFoundError:
        #         print(f'{filename} already deleted')

        return midi_info

def serialize_midi_file(midi_filename):
    mid = mido.MidiFile(midi_filename)
    if len(mid.tracks) > 1:
        mid.tracks = [mido.merge_tracks(mid.tracks)]

    msgs = []
    for msg in mid.tracks[0]:
        serialized = msg.dict() if msg.is_meta else str(msg)
        msgs.append(serialized)
    tpb = mid.ticks_per_beat
    return msgs, tpb

def deserialize_midi_file(msgs, ticks_per_beat, out_filename):
    track = mido.MidiTrack()
    mid = mido.MidiFile(ticks_per_beat=ticks_per_beat, tracks=[track])

    for serialized_msg in msgs:
        is_meta = isinstance(serialized_msg, dict)
        if is_meta:
            msg = mido.MetaMessage(**serialized_msg)
        else:
            msg = mido.Message.from_str(serialized_msg)
        track.append(msg)
    mid.save(out_filename)

def midi_is_empty(midi_filename):
    mid = mido.MidiFile(midi_filename)
    for msg in mid:
        if msg.type == 'note_on':
            return False
    return True

if __name__ == '__main__':
    pass

    # mf1 = '../misc/output/scalesA.mid'

    # s, tpb = serialize_midi_file(midi_filename=mf1)
    # # print(s)
    # deserialize_midi_file(msgs=s, ticks_per_beat=tpb, out_filename='./yeet.mid')
    # display_midi('./yeet.mid')
