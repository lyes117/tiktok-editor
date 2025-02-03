from .base_effect import BaseAudioEffect
import numpy as np

class Compression(BaseAudioEffect):
    def __init__(self, intensity=0.5):
        super().__init__(intensity)
    
    def apply(self, audio_data, sample_rate):
        # Ensure audio data is valid
        audio_data = self.ensure_valid_audio(audio_data)
        
        # Calculate threshold based on intensity
        threshold = 0.5 - (0.3 * self.intensity)  # 0.5 to 0.2
        ratio = 1 + (self.intensity * 3)  # 1:1 to 4:1
        
        # Apply compression
        output = audio_data.copy()
        mask = np.abs(output) > threshold
        output[mask] = np.sign(output[mask]) * (
            threshold + (np.abs(output[mask]) - threshold) / ratio
        )
        
        # Normalize output
        output = output / np.max(np.abs(output))
        
        return output
