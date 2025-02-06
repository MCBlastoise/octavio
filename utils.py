from flask import Flask, request
import numpy as np
import pyaudio
import wave
from scipy.io.wavfile import read

def wav_to_np(wav_filename):
    file_contents = read(wav_filename)
    file_data = np.array(file_contents[1])
    return file_data