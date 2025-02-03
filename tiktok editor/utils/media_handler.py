import os
import subprocess
import tempfile
import logging
from pathlib import Path

class MediaHandler:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.logger = logging.getLogger('MediaHandler')
    
    def extract_audio(self, video_path):
        """Extract audio from video file"""
        try:
            # Create temp audio path
            temp_audio = os.path.join(self.temp_dir, "temp_audio.wav")
            
            # Ensure input video exists
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            # FFmpeg command to extract audio
            command = [
                'ffmpeg',
                '-i', video_path,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # Audio codec
                '-ar', '44100',  # Sample rate
                '-ac', '2',  # Stereo
                '-y',  # Overwrite output file
                temp_audio
            ]
            
            # Execute FFmpeg command
            result = subprocess.run(
                command,
                capture_output=True,
                text=True
            )
            
            # Check if extraction was successful
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg error: {result.stderr}")
            
            if not os.path.exists(temp_audio):
                raise FileNotFoundError("Audio extraction failed")
            
            return temp_audio
            
        except Exception as e:
            self.logger.error(f"Error extracting audio: {str(e)}")
            raise
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            os.rmdir(self.temp_dir)
        except Exception as e:
            self.logger.error(f"Error cleaning up: {str(e)}")
