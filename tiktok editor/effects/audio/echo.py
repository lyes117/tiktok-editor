from .base_effect import BaseAudioEffect
import numpy as np

class Echo(BaseAudioEffect):
    def __init__(self, intensity=0.5):
        super().__init__(intensity)
    
    def apply(self, audio_data, sample_rate):
        # Ensure audio data is valid
        audio_data = self.ensure_valid_audio(audio_data)
        
        # Calculate delay based on intensity
        delay_seconds = 0.1 + (self.intensity * 0.3)  # 0.1 to 0.4 seconds
        delay_samples = int(sample_rate * delay_seconds)
        
        # Ensure delay is not longer than audio
        if delay_samples >= len(audio_data):
            delay_samples = len(audio_data) // 4
        
        # Create delayed version
        delayed = np.zeros_like(audio_data)
        delayed[delay_samples:] = audio_data[:-delay_samples]
        
        # Mix original and delayed with intensity
        output = audio_data + (delayed * self.intensity * 0.7)
        
        # Normalize to prevent clipping
        output = output / np.max(np.abs(output))
        
        return output
