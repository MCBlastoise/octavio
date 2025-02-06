from flask import Flask, request
import numpy as np
import pyaudio
import wave
from scipy.io.wavfile import read

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