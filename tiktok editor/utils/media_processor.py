import cv2
import numpy as np
import librosa
import soundfile as sf
import tempfile
import os
from concurrent.futures import ThreadPoolExecutor

class MediaProcessor:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def extract_audio(self, video_path):
        """Extract audio from video file"""
        temp_audio = os.path.join(self.temp_dir, "temp_audio.wav")
        os.system(f'ffmpeg -i "{video_path}" -vn -acodec pcm_s16le -ar 44100 -ac 2 "{temp_audio}"')
        return temp_audio
    
    def process_video_frame(self, frame, effects):
        """Process a single video frame with effects"""
        for effect in effects:
            frame = effect.apply(frame)
        return frame
    
    def process_audio_segment(self, audio_data, sr, effects):
        """Process an audio segment with effects"""
        for effect in effects:
            audio_data = effect.apply(audio_data, sr)
        return audio_data
