def assemble_media(self, video_path: str, audio_path: str, output_path: str, 
                      progress_callback=None):
        """
        Assemble video and audio into final MP4.
        
        Parameters:
        - video_path: Path to the video file
        - audio_path: Path to the audio file
        - output_path: Path for the final output file
        """
        try:
            if progress_callback:
                progress_callback(0)
            
            # Verify input files
            if not video_path or not os.path.exists(video_path):
                raise Exception(f"Fichier vidéo non trouvé: {video_path}")
            
            self.logger.info(f"Using video: {video_path}")
            self.logger.info(f"Using audio: {audio_path}")
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if audio_path and os.path.exists(audio_path):
                # Combine video and audio
                ffmpeg_cmd = [
                    self._get_ffmpeg_path(),
                    '-i', video_path,       # Video input
                    '-i', audio_path,       # Audio input
                    '-c:v', 'copy',         # Copy video stream
                    '-c:a', 'aac',          # AAC audio codec
                    '-b:a', '192k',         # Audio bitrate
                    '-shortest',            # Match shortest stream
                    '-y',                   # Overwrite output
                    output_path
                ]
            else:
                # Just copy video if no audio
                ffmpeg_cmd = [
                    self._get_ffmpeg_path(),
                    '-i', video_path,
                    '-c:v', 'copy',
                    '-y',
                    output_path
                ]
            
            self.logger.info(f"Executing FFmpeg command: {' '.join(ffmpeg_cmd)}")
            
            # Execute FFmpeg command
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Erreur lors de l'assemblage: {stderr}")
            
            # Verify output file
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise Exception("Fichier de sortie invalide")
            
            if progress_callback:
                progress_callback(100)
            
            self.logger.info("Assemblage terminé avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'assemblage: {str(e)}")
            raise
