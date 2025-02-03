from .base_effect import BaseAudioEffect
import numpy as np
from scipy import signal

class PitchShift(BaseAudioEffect):
    def __init__(self, intensity=0.5):
        super().__init__(intensity)
    
    def apply(self, audio_data, sample_rate):
        # Ensure audio data is valid
        audio_data = self.ensure_valid_audio(audio_data)
        
        # Calculate pitch shift factor
        # intensity 0.5 = no shift, <0.5 = down, >0.5 = up
        factor = 0.5 + self.intensity
        
        # Resample the audio
        output_length = int(len(audio_data) / factor)
        output = signal.resample(audio_data, output_length)
        
        # Match original length
        if len(output) > len(audio_data):
            output = output[:len(audio_data)]
        else:
            output = np.pad(output, (0, len(audio_data) - len(output)))
        
        return output
