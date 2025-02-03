from .base_effect import BaseAudioEffect
import numpy as np

class Normalize(BaseAudioEffect):
    def __init__(self, intensity=0.5):
        super().__init__(intensity)
    
    def apply(self, audio_data, sample_rate):
        # Ensure audio data is valid
        audio_data = self.ensure_valid_audio(audio_data)
        
        # Find the maximum amplitude
        max_amp = np.max(np.abs(audio_data))
        
        if max_amp > 0:
            # Calculate target amplitude based on intensity
            target_amp = 0.3 + (self.intensity * 0.7)  # 0.3 to 1.0
            
            # Apply normalization
            output = audio_data * (target_amp / max_amp)
            return output
        
        return audio_data
