import cv2
import numpy as np
import soundfile as sf
import subprocess
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import torch
import torch.cuda
import logging
import time
from typing import Optional, List, Callable
from .audio_processor import AudioProcessor

class ExportProcessor:
    def __init__(self, temp_dir: str):
        self.temp_dir = temp_dir
        self.use_gpu = torch.cuda.is_available()
        self.num_threads = os.cpu_count()
        self.logger = self._setup_logger()
        
        # Initialize GPU if available
        if self.use_gpu:
            try:
                torch.cuda.empty_cache()
                torch.cuda.init()
                self.logger.info("GPU initialized successfully")
            except Exception as e:
                self.logger.warning(f"GPU initialization failed: {str(e)}")
                self.use_gpu = False
        
        # Create temp directory if it doesn't exist
        os.makedirs(temp_dir, exist_ok=True)
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('ExportProcessor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _process_frame_gpu(self, frame: np.ndarray, effects: list) -> np.ndarray:
        try:
            gpu_frame = cv2.cuda_GpuMat()
            gpu_frame.upload(frame)
            
            for effect in effects:
                if hasattr(effect, 'apply_gpu'):
                    gpu_frame = effect.apply_gpu(gpu_frame)
                else:
                    cpu_frame = gpu_frame.download()
                    cpu_frame = effect.apply(cpu_frame)
                    gpu_frame.upload(cpu_frame)
            
            return gpu_frame.download()
        except Exception as e:
            self.logger.error(f"GPU processing error: {str(e)}")
            return self._process_frame_cpu(frame, effects)
    
    def _process_frame_cpu(self, frame: np.ndarray, effects: list) -> np.ndarray:
        try:
            processed_frame = frame.copy()
            for effect in effects:
                processed_frame = effect.apply(processed_frame)
            return processed_frame
        except Exception as e:
            self.logger.error(f"CPU processing error: {str(e)}")
            return frame
    
    def _process_video(self, input_path: str, output_path: str, video_effects: list, 
                      progress_callback: Optional[Callable] = None) -> bool:
        """Process video with effects"""
        cap = None
        out = None
        
        try:
            self.logger.info(f"Processing video: {input_path}")
            
            # Open input video
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                raise Exception("Cannot open input video")
            
            # Get video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            if not out.isOpened():
                raise Exception("Cannot create output video")
            
            frames_processed = 0
            
            with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Process frame
                    if self.use_gpu:
                        processed_frame = self._process_frame_gpu(frame, video_effects)
                    else:
                        processed_frame = self._process_frame_cpu(frame, video_effects)
                    
                    # Write processed frame
                    out.write(processed_frame)
                    
                    # Update progress
                    frames_processed += 1
                    if progress_callback:
                        progress = (frames_processed / total_frames) * 100
                        progress_callback(progress)
            
            self.logger.info("Video processing completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing video: {str(e)}")
            raise
            
        finally:
            if cap is not None:
                cap.release()
            if out is not None:
                out.release()
    
    def _assemble_final_video(self, video_path: str, audio_path: str, output_path: str) -> bool:
        """Assemble final video with FFmpeg"""
        try:
            self.logger.info("Assembling final video")
            
            # Prepare FFmpeg command
            ffmpeg_cmd = [
                'ffmpeg',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-strict', 'experimental',
                '-b:a', '192k',
                '-y',
                output_path
            ]
            
            # Execute command
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"FFmpeg error: {stderr}")
            
            self.logger.info("Final assembly completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Assembly error: {str(e)}")
            raise
    
    def export(self, input_video: str, output_path: str, video_effects: list, 
              audio_effects: Optional[list] = None, temp_audio: Optional[str] = None, 
              progress_callback: Optional[Callable] = None) -> str:
        """Export video with effects"""
        temp_files = []
        
        try:
            # Create temporary files
            timestamp = str(int(time.time()))
            temp_video = os.path.join(self.temp_dir, f"temp_video_{timestamp}.mp4")
            temp_audio_processed = os.path.join(self.temp_dir, f"temp_audio_{timestamp}.wav")
            temp_files.extend([temp_video, temp_audio_processed])
            
            # 1. Process video (60% of progress)
            def video_progress(p):
                if progress_callback:
                    progress_callback(p * 0.6)
            
            if video_effects:
                self.logger.info("Processing video with effects")
                self._process_video(input_video, temp_video, video_effects, video_progress)
            else:
                self.logger.info("No video effects, using original video")
                temp_video = input_video
            
            # 2. Process audio if available (20% of progress)
            audio_to_use = temp_audio
            if temp_audio and audio_effects:
                self.logger.info("Processing audio with effects")
                audio_processor = AudioProcessor(self.temp_dir)
                
                def audio_progress(p):
                    if progress_callback:
                        progress_callback(60 + p * 0.2)
                
                audio_processor.process_audio(
                    temp_audio,
                    temp_audio_processed,
                    audio_effects,
                    audio_progress
                )
                audio_to_use = temp_audio_processed
            
            # 3. Final assembly (20% of progress)
            if progress_callback:
                progress_callback(80)
            
            if audio_to_use:
                self._assemble_final_video(temp_video, audio_to_use, output_path)
            else:
                # If no audio, just copy the video
                if temp_video != input_video:
                    import shutil
                    shutil.copy2(temp_video, output_path)
            
            if progress_callback:
                progress_callback(100)
            
            self.logger.info(f"Export completed: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Export error: {str(e)}")
            raise
            
        finally:
            # Cleanup temporary files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file) and temp_file != input_video:
                        os.remove(temp_file)
                except Exception as e:
                    self.logger.warning(f"Could not delete temporary file {temp_file}: {str(e)}")
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.use_gpu:
                torch.cuda.empty_cache()
            
            if os.path.exists(self.temp_dir):
                for file in os.listdir(self.temp_dir):
                    file_path = os.path.join(self.temp_dir, file)
                    if os.path.isfile(file_path):
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            self.logger.warning(f"Could not delete {file_path}: {str(e)}")
                try:
                    os.rmdir(self.temp_dir)
                except Exception as e:
                    self.logger.warning(f"Could not delete temp directory: {str(e)}")
        except Exception as e:
            self.logger.error(f"Cleanup error: {str(e)}")
