import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import time
import statistics
import json
import numpy as np
import pyaudio
import log_utils
import scipy.ndimage
import scipy.io

def record_audio(record_seconds):
    CHUNK = 1024
    DEVICE_INDEX = 1
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 22050

    with log_utils.no_stderr():
        p = pyaudio.PyAudio()
    stream = p.open(input=True, input_device_index=DEVICE_INDEX, format=FORMAT, channels=CHANNELS, rate=RATE)

    print('Recording...')
    full_recording = np.empty(RATE * record_seconds)
    for i in range(0, RATE // CHUNK * record_seconds):
        mic_input = stream.read(CHUNK)
        data = np.frombuffer(mic_input, dtype=np.int16)
        start_chunk_pos = i * CHUNK
        end_chunk_position = i * CHUNK + CHUNK
        full_recording[start_chunk_pos : end_chunk_position] = data
    print('Done')

    stream.close()
    p.terminate()

    return full_recording

def rms(arr):
    return (np.sum(np.square(arr)) / np.size(arr)) ** (1/2)

def chunk_and_rms_sound(full_sound, window_size=2048):
    hop_size = window_size // 2

    rmses = []
    for window_start in range(0, len(full_sound), hop_size):
        window_end = window_start + window_size
        window = full_sound[window_start:window_end]
        window_rms = rms(window)
        rmses.append(window_rms)
    return rmses

def measure_calibration():
    noise_trial_duration = 30
    signal_trial_duration = 60

    input('Measuring noise: hit [ENTER] to start')
    noise_trial = record_audio(record_seconds=noise_trial_duration)
    noise_rmses = chunk_and_rms_sound(full_sound=noise_trial)
    noise_quartiles = statistics.quantiles(noise_rmses)
    noise_mean = statistics.mean(noise_rmses)
    noise_std = statistics.stdev(noise_rmses)

    print(f'Noise quartiles: {noise_quartiles}')
    print(f'Noise mean and stdev: {noise_mean}, {noise_std}')

    input('Measuring signal: hit [ENTER] to start')
    signal_trial = record_audio(record_seconds=signal_trial_duration)
    signal_rmses = chunk_and_rms_sound(full_sound=signal_trial)
    baseline_signal_threshold = 2.0
    valid_signal_rmses = [rms for rms in signal_rmses if rms >= baseline_signal_threshold]
    signal_quartiles = statistics.quantiles(valid_signal_rmses)
    signal_mean = statistics.mean(signal_rmses)
    signal_std = statistics.stdev(signal_rmses)

    print(f'Signal quartiles: {signal_quartiles}')
    print(f'Signal mean and stdev: {signal_mean}, {signal_std}')

    return noise_quartiles, noise_mean, noise_std, signal_quartiles, signal_mean, signal_std

def apply_calibration(noise_quartiles, noise_mean, noise_std, signal_quartiles, signal_mean, signal_std):
    with open('./infra.json', 'r') as f:
        j = json.load(f)

    noise_25th, noise_50th, noise_75th = noise_quartiles
    signal_25th, signal_50th, signal_75th = signal_quartiles

    j['NOISE_25TH_PERCENTILE'] = noise_25th
    j['NOISE_50TH_PERCENTILE'] = noise_50th
    j['NOISE_75TH_PERCENTILE'] = noise_75th
    j['NOISE_MEAN'] = noise_mean
    j['NOISE_STD'] = noise_std

    j['SIGNAL_25TH_PERCENTILE'] = signal_25th
    j['SIGNAL_50TH_PERCENTILE'] = signal_50th
    j['SIGNAL_75TH_PERCENTILE'] = signal_75th
    j['SIGNAL_MEAN'] = signal_mean
    j['SIGNAL_STD'] = signal_std

    with open('./infra.json', 'w') as f:
        json.dump(j, f)
        f.write('\n')

def denoise_signal(signal, noise_quartiles, signal_quartiles):
    # Accepts an np.float64 array

    _, noise_median, _ = noise_quartiles
    _, signal_median, _ = signal_quartiles

    alpha = 0.5
    threshold = alpha * signal_median + (1 - alpha) * noise_median

    window_size = 2048
    hop_size = window_size // 2
    window_rmses = np.array(chunk_and_rms_sound(signal, window_size=window_size))
    initial_mask = window_rmses >= threshold

    context = 1
    smoothed_mask = scipy.ndimage.maximum_filter1d(initial_mask, size=2 * context + 1)

    denoised_signal = np.copy(signal)
    for window_start, is_piano in zip(
        range(0, len(signal), hop_size),
        smoothed_mask
    ):
        window_end = window_start + window_size
        if not is_piano:
            denoised_signal[window_start:window_end] = 0

    return denoised_signal

# def read_wav(filename):
#     sample_rate, data = scipy.io.wavfile.read(filename)

#     # Convert to float32 for processing, if it's int16
#     if data.dtype == np.int16:
#         data = data.astype(np.float64)

#     return data, sample_rate

# def write_wav(filename, audio_array):
#     int16_audio = np.int16(audio_array)
#     scipy.io.wavfile.write(filename, 22050, int16_audio)

if __name__ == '__main__':
    ...

    # noise_quartiles, noise_mean, noise_std, signal_quartiles, signal_mean, signal_std = measure_calibration()
    # apply_calibration(noise_quartiles, noise_mean, noise_std, signal_quartiles, signal_mean, signal_std)


    # noise_quartiles = [3.800056535779002, 3.852695381507288, 4.000701825621752]
    # # signal_quartiles = [3.9466968308970776, 5.681249957410223, 16.480802509792568]
    # signal_quartiles = [9.704052657907255, 34.39102564355653, 91.2482854118153]
    # # signal_quartiles = [4.455043171009717, 20, 27.538433453552358]
    # # signal_quartiles = [4.455043171009717, 100, 27.538433453552358]
    # # signal_quartiles = [4.455043171009717, 4.0, 27.538433453552358]

    # # input('Start test:')
    # # signal = record_audio(30)
    # # write_wav('original.wav', signal)

    # # signal, _ = read_wav('./original.wav')
    # ambient, _ = read_wav('./ambient.wav')
    # # print(ambient)
    # # raise NotImplementedError

    # denoised = denoise_signal(signal=ambient, noise_quartiles=noise_quartiles, signal_quartiles=signal_quartiles)
    # write_wav('denoised_ambient.wav', denoised)
