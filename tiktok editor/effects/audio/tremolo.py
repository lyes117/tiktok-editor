import numpy as np

class Tremolo:
    def __init__(self, frequency=5):
        self.frequency = frequency

    def apply(self, audio_data, sample_rate):
        t = np.arange(len(audio_data)) / sample_rate
        mod = 0.5 * (1 + np.sin(2 * np.pi * self.frequency * t))
        return audio_data * mod
