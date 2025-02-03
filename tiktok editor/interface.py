from processors.video_processor import VideoProcessor
from processors.audio_processor import AudioProcessor
from utils.media_handler import MediaHandler
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
import logging
import tempfile

class Interface:
    def __init__(self):
        self.setup_logging()
        self.video_processor = VideoProcessor()
        self.audio_processor = AudioProcessor()
        self.media_handler = MediaHandler()
        self.temp_dir = tempfile.mkdtemp()
    
    def setup_logging(self):
        self.logger = logging.getLogger('VideoProcessor')
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        self.logger.addHandler(handler)
    
    def extract_audio(self, video_path):
        """Extract audio from video file"""
        return self.media_handler.extract_audio(video_path)
    
    def add_video_effect(self, effect):
        """Add a video effect to the processing pipeline"""
        self.video_processor.add_effect(effect)
    
    def add_audio_effect(self, effect):
        """Add an audio effect to the processing pipeline"""
        self.audio_processor.add_effect(effect)
    
    def _run_ffmpeg_command(self, command):
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"FFmpeg error: {e.stderr.decode()}")
            raise
    
    def process(self, input_video, output_video):
        try:
            if not os.path.exists(input_video):
                raise FileNotFoundError(f"Input video not found: {input_video}")

            temp_video = os.path.join(self.temp_dir, "temp_video.mp4")
            temp_audio = os.path.join(self.temp_dir, "temp_audio.wav")
            processed_audio = os.path.join(self.temp_dir, "processed_audio.wav")
            
            # Extract audio
            self._run_ffmpeg_command([
                'ffmpeg', '-i', input_video, 
                '-vn', '-acodec', 'pcm_s16le', 
                temp_audio
            ])
            
            # Process video and audio in parallel
            with ThreadPoolExecutor(max_workers=2) as executor:
                video_future = executor.submit(
                    self.video_processor.process,
                    input_video,
                    temp_video
                )
                
                audio_future = executor.submit(
                    self.audio_processor.process,
                    temp_audio,
                    processed_audio
                )
                
                # Wait for both processes to complete
                video_future.result()
                audio_future.result()
            
            # Combine processed video and audio
            self._run_ffmpeg_command([
                'ffmpeg',
                '-i', temp_video,
                '-i', processed_audio,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-b:a', '192k',
                output_video
            ])
            
        except Exception as e:
            self.logger.error(f"Processing error: {str(e)}")
            raise
        finally:
            # Cleanup temp files
            for file in [temp_video, temp_audio, processed_audio]:
                if os.path.exists(file):
                    os.remove(file)
            if os.path.exists(self.temp_dir):
                os.rmdir(self.temp_dir)
    
    def __del__(self):
        """Cleanup when the interface is destroyed"""
        self.media_handler.cleanup()
