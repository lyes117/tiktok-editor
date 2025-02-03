from .base_effect import BaseAudioEffect
import numpy as np
from scipy import signal

class BassBoost(BaseAudioEffect):
    def __init__(self, intensity=0.5):
        super().__init__(intensity)
    
    def apply(self, audio_data, sample_rate):
        # Ensure audio data is valid
        audio_data = self.ensure_valid_audio(audio_data)
        
        # Design low-pass filter
        cutoff = 150  # Hz
        nyquist = sample_rate / 2
        normal_cutoff = cutoff / nyquist
        
        # Create and apply filter
        b, a = signal.butter(4, normal_cutoff, btype='lowpass')
        bass = signal.filtfilt(b, a, audio_data)
        
        # Mix with original
        boost_amount = self.intensity * 2.0  # 0 to 2x boost
        output = audio_data + (bass * boost_amount)
        
        # Normalize to prevent clipping
        output = output / np.max(np.abs(output))
        
        return output
