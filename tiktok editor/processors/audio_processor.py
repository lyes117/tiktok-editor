import numpy as np
import soundfile as sf
import librosa
import torch
import torch.cuda
from concurrent.futures import ThreadPoolExecutor
import os
import logging
from pathlib import Path
import subprocess
from typing import List, Tuple, Optional
import resampy
import time

class AudioProcessor:
    def __init__(self, temp_dir: str):
        self.temp_dir = temp_dir
        self.use_gpu = torch.cuda.is_available()
        self.num_threads = os.cpu_count()
        self.logger = self._setup_logger()
        self.chunk_size = 32768  # Optimal chunk size for audio processing
        
        # Initialize GPU if available
        if self.use_gpu:
            self.device = torch.device('cuda')
            # Warm up GPU
            torch.cuda.empty_cache()
            torch.cuda.init()
        else:
            self.device = torch.device('cpu')
        
        # Create temp directory if it doesn't exist
        os.makedirs(temp_dir, exist_ok=True)
    
    def _setup_logger(self):
        """Setup logging configuration"""
        logger = logging.getLogger('AudioProcessor')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _load_audio(self, audio_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file with format detection and resampling"""
        try:
            # Try soundfile first (faster for WAV files)
            audio_data, sample_rate = sf.read(audio_path)
        except Exception as e:
            self.logger.debug(f"Soundfile failed: {str(e)}, trying librosa...")
            try:
                # Try librosa for other formats
                audio_data, sample_rate = librosa.load(audio_path, sr=None)
            except Exception as e:
                self.logger.debug(f"Librosa failed: {str(e)}, trying FFmpeg...")
                # Last resort: convert to WAV using FFmpeg
                temp_wav = os.path.join(self.temp_dir, f"temp_convert_{int(time.time())}.wav")
                try:
                    subprocess.run([
                        'ffmpeg', '-i', audio_path,
                        '-acodec', 'pcm_s16le',
                        '-ar', '44100',
                        '-ac', '2',
                        '-y',
                        temp_wav
                    ], capture_output=True, check=True)
                    
                    audio_data, sample_rate = sf.read(temp_wav)
                finally:
                    if os.path.exists(temp_wav):
                        os.remove(temp_wav)
        
        # Convert to mono if stereo
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)
        
        # Ensure float32 format
        audio_data = audio_data.astype(np.float32)
        
        # Normalize input audio
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            audio_data = audio_data / max_val
        
        return audio_data, sample_rate
    
    def _process_chunk_gpu(self, chunk: np.ndarray, effects: list, sample_rate: int) -> np.ndarray:
        """Process audio chunk using GPU"""
        try:
            # Move data to GPU
            chunk_tensor = torch.from_numpy(chunk).to(self.device)
            
            # Apply effects
            for effect in effects:
                if hasattr(effect, 'apply_gpu'):
                    # Use GPU implementation if available
                    chunk_tensor = effect.apply_gpu(chunk_tensor)
                else:
                    # Fall back to CPU if no GPU implementation
                    chunk_cpu = chunk_tensor.cpu().numpy()
                    chunk_cpu = effect.apply(chunk_cpu, sample_rate)
                    chunk_tensor = torch.from_numpy(chunk_cpu).to(self.device)
            
            # Move back to CPU
            return chunk_tensor.cpu().numpy()
            
        except Exception as e:
            self.logger.error(f"GPU processing error: {str(e)}")
            # Fall back to CPU processing
            return self._process_chunk_cpu(chunk, effects, sample_rate)
    
    def _process_chunk_cpu(self, chunk: np.ndarray, effects: list, sample_rate: int) -> np.ndarray:
        """Process audio chunk using CPU"""
        try:
            processed_chunk = chunk.copy()
            for effect in effects:
                processed_chunk = effect.apply(processed_chunk, sample_rate)
            return processed_chunk
        except Exception as e:
            self.logger.error(f"CPU processing error: {str(e)}")
            return chunk
    
    def _process_chunk(self, chunk: np.ndarray, effects: list, sample_rate: int) -> np.ndarray:
        """Process a chunk of audio data with GPU acceleration if available"""
        if self.use_gpu:
            return self._process_chunk_gpu(chunk, effects, sample_rate)
        else:
            return self._process_chunk_cpu(chunk, effects, sample_rate)
    
    def process_audio(self, 
                     input_path: str, 
                     output_path: str, 
                     effects: list, 
                     progress_callback=None) -> str:
        """Process audio with parallel chunk processing and GPU acceleration"""
        try:
            start_time = time.time()
            self.logger.info(f"Starting audio processing: {input_path}")
            
            # Load audio
            audio_data, sample_rate = self._load_audio(input_path)
            
            # Split audio into chunks
            total_samples = len(audio_data)
            chunks = [
                audio_data[i:i + self.chunk_size]
                for i in range(0, total_samples, self.chunk_size)
            ]
            
            processed_chunks = []
            total_chunks = len(chunks)
            
            # Process chunks in parallel
            with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                futures = []
                for i, chunk in enumerate(chunks):
                    future = executor.submit(self._process_chunk, chunk, effects, sample_rate)
                    futures.append(future)
                    
                    if progress_callback:
                        progress = (i + 1) / total_chunks * 100
                        progress_callback(progress)
                
                # Collect results in order
                for i, future in enumerate(futures):
                    try:
                        processed_chunk = future.result()
                        processed_chunks.append(processed_chunk)
                        
                        if progress_callback:
                            progress = (i + 1) / total_chunks * 100
                            progress_callback(progress)
                            
                    except Exception as e:
                        self.logger.error(f"Error processing chunk {i}: {str(e)}")
                        # Use original chunk if processing failed
                        processed_chunks.append(chunks[i])
            
            # Combine chunks
            processed_audio = np.concatenate(processed_chunks)
            
            # Final normalization
            max_val = np.max(np.abs(processed_audio))
            if max_val > 0:
                processed_audio = processed_audio / max_val * 0.9
            
            # Save processed audio
            sf.write(output_path, processed_audio, sample_rate)
            
            processing_time = time.time() - start_time
            self.logger.info(f"Audio processing completed in {processing_time:.2f} seconds")
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error processing audio: {str(e)}")
            raise
    
    def cleanup(self):
        """Clean up temporary files and resources"""
        try:
            if self.use_gpu:
                torch.cuda.empty_cache()
            
            if os.path.exists(self.temp_dir):
                for file in os.listdir(self.temp_dir):
                    file_path = os.path.join(self.temp_dir, file)
                    if os.path.isfile(file_path):
                        try:
                            os.unlink(file_path)
                        except Exception as e:
                            self.logger.warning(f"Could not delete {file_path}: {str(e)}")
                try:
                    os.rmdir(self.temp_dir)
                except Exception as e:
                    self.logger.warning(f"Could not delete temp directory: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
