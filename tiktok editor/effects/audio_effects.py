import numpy as np
from scipy import signal

class AudioEffect:
    def __init__(self):
        pass

    def apply(self, audio_data, sample_rate):
        return audio_data

class PitchShift(AudioEffect):
    def apply(self, audio_data, sample_rate):
        # Simple pitch shift using resampling
        factor = 1.2
        return signal.resample(audio_data, int(len(audio_data) / factor))

class Reverb(AudioEffect):
    def apply(self, audio_data, sample_rate):
        # Simple reverb using convolution
        decay = 0.3
        delay = int(sample_rate * 0.1)
        impulse = np.exp(-decay * np.arange(delay))
        return signal.convolve(audio_data, impulse, mode='same')

class Tremolo(AudioEffect):
    def apply(self, audio_data, sample_rate):
        # Apply amplitude modulation
        t = np.arange(len(audio_data)) / sample_rate
        mod = 0.5 * (1 + np.sin(2 * np.pi * 5 * t))
        return audio_data * mod
