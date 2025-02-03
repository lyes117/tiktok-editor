from .base_effect import BaseAudioEffect
import numpy as np
from scipy import signal

class Reverb(BaseAudioEffect):
    def __init__(self, intensity=0.5):
        super().__init__(intensity)
    
    def apply(self, audio_data, sample_rate):
        # Ensure audio data is valid
        audio_data = self.ensure_valid_audio(audio_data)
        
        # Calculate delay and decay based on intensity
        delay_seconds = 0.1 + (self.intensity * 0.3)  # 0.1 to 0.4 seconds
        decay = 0.1 + (self.intensity * 0.5)  # 0.1 to 0.6
        
        # Calculate delay in samples
        delay_samples = int(sample_rate * delay_seconds)
        
        # Ensure delay is not longer than audio
        if delay_samples >= len(audio_data):
            delay_samples = len(audio_data) // 4
        
        # Create impulse response
        impulse = np.exp(-decay * np.arange(delay_samples))
        impulse = impulse / np.sum(impulse)  # Normalize
        
        # Apply convolution
        wet = signal.convolve(audio_data, impulse, mode='same')
        
        # Mix dry and wet signals
        mix_ratio = self.intensity
        output = (1 - mix_ratio) * audio_data + mix_ratio * wet
        
        return output
