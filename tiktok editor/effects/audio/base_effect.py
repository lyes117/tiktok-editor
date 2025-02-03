import numpy as np

class BaseAudioEffect:
    def __init__(self, intensity=0.5):
        self.intensity = intensity
    
    def set_intensity(self, intensity):
        self.intensity = intensity
    
    def apply(self, audio_data, sample_rate):
        return audio_data
    
    def ensure_valid_audio(self, audio_data):
        """Ensure audio data is valid and in the correct format"""
        if isinstance(audio_data, np.ndarray):
            if len(audio_data.shape) == 1:
                return audio_data
            elif len(audio_data.shape) == 2:
                return np.mean(audio_data, axis=1)  # Convert stereo to mono
        return np.array(audio_data)
