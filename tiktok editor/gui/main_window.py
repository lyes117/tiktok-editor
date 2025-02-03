from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QListWidget, QGroupBox, QProgressBar,
                           QTabWidget, QMessageBox, QFileDialog, QLabel,
                           QScrollArea, QApplication, QCheckBox, QSlider)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
import cv2
import os
import sys
import subprocess
import soundfile as sf
import numpy as np
from .video_preview import VideoPreviewWidget
from .audio_preview import AudioWaveformWidget
from .effect_widget import EffectWidget
from effects.visual import Crop, LightBar, ColorFilter, Blur, Mirror, Vignette
from effects.audio import PitchShift, Reverb, Echo, BassBoost, Normalize, Compression
from processors.video_processor import VideoProcessor

class PlaybackState:
    Stopped = 0
    Playing = 1
    Paused = 2

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Galaxy Video Processor")
        self.setMinimumSize(1200, 800)
        
        # Create temp directory
        self.temp_dir = os.path.join(os.getcwd(), 'temp')
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Initialize VideoProcessor and check FFmpeg
        try:
            self.video_processor = VideoProcessor(self.temp_dir)
            ffmpeg_path = self.video_processor._get_ffmpeg_path()
            if not os.path.exists(ffmpeg_path):
                raise Exception("FFmpeg non trouvé")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                "FFmpeg n'est pas installé ou n'est pas accessible.\n"
                "Veuillez installer FFmpeg et vous assurer qu'il est accessible dans le PATH du système."
            )
            sys.exit(1)
        
        # Initialize variables
        self.input_video = None
        self.preview_audio = None
        self.cap = None
        self.audio_player = None
        self.audio_output = None
        
        # Setup UI
        self.initUI()
        
        # Setup preview timer
        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self.update_preview)
        
        # Set style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0b1a;
            }
            QWidget {
                color: #ffffff;
            }
            QPushButton {
                background-color: #2e1f5e;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3d2b7a;
            }
            QPushButton:disabled {
                background-color: #1a1b2e;
                color: #666666;
            }
            QGroupBox {
                color: white;
                border: 2px solid #2e1f5e;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QProgressBar {
                border: 2px solid #2e1f5e;
                border-radius: 5px;
                text-align: center;
                color: white;
                background-color: #1a1b2e;
            }
            QProgressBar::chunk {
                background-color: #6d4ed7;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QTabWidget::pane {
                border: 2px solid #2e1f5e;
                border-radius: 6px;
                background-color: #0d0e23;
            }
            QTabBar::tab {
                background-color: #1a1b2e;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #2e1f5e;
            }
            QTabBar::tab:hover {
                background-color: #3d2b7a;
            }
            QLabel {
                color: #8a8db9;
            }
            QLabel#statusLabel {
                color: #6d4ed7;
                font-weight: bold;
            }
        """)
    
    def initUI(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create top control panel
        self.create_top_panel(main_layout)
        
        # Create tabs
        tabs = QTabWidget()
        tabs.addTab(self.create_video_tab(), "Vidéo")
        tabs.addTab(self.create_audio_tab(), "Audio")
        main_layout.addWidget(tabs)
    
    def create_top_panel(self, parent_layout):
        # Top controls
        top_layout = QHBoxLayout()
        
        # Import/Export buttons
        self.import_btn = QPushButton("Importer Vidéo")
        self.export_btn = QPushButton("Exporter")
        
        self.import_btn.clicked.connect(self.import_video)
        self.export_btn.clicked.connect(self.export_video)
        
        # Initially disable export button
        self.export_btn.setEnabled(False)
        
        # Add buttons to layout
        top_layout.addWidget(self.import_btn)
        top_layout.addWidget(self.export_btn)
        
        # Add status label
        self.status_label = QLabel("Aucune vidéo chargée")
        self.status_label.setObjectName("statusLabel")
        top_layout.addWidget(self.status_label)
        
        top_layout.addStretch()
        
        # Add layout to parent
        parent_layout.addLayout(top_layout)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setMinimumHeight(20)
        parent_layout.addWidget(self.progress_bar)
    
    def create_video_tab(self):
        video_widget = QWidget()
        layout = QHBoxLayout(video_widget)
        layout.setSpacing(10)
        
        # Left panel - Preview
        left_panel = QVBoxLayout()
        self.video_preview = VideoPreviewWidget()
        left_panel.addWidget(self.video_preview)
        
        # Video controls
        video_controls = QHBoxLayout()
        self.play_btn = QPushButton("Lecture")
        self.stop_btn = QPushButton("Stop")
        self.play_btn.clicked.connect(self.play_video)
        self.stop_btn.clicked.connect(self.stop_video)
        
        # Initially disable controls
        self.play_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        
        video_controls.addWidget(self.play_btn)
        video_controls.addWidget(self.stop_btn)
        video_controls.addStretch()
        left_panel.addLayout(video_controls)
        
        layout.addLayout(left_panel, stretch=2)
        
        # Right panel - Effects
        right_panel = QVBoxLayout()
        effects_group = QGroupBox("Effets Vidéo")
        effects_layout = QVBoxLayout()
        
        # Create scrollable area for effects
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.video_effects_layout = QVBoxLayout(scroll_widget)
        
        # Add visual effects
        self.visual_effects = []
        visual_effects_list = [
            ("Crop", Crop),
            ("Light Bar", LightBar),
            ("Color Filter", ColorFilter),
            ("Blur", Blur),
            ("Mirror", Mirror),
            ("Vignette", Vignette)
        ]
        
        for name, effect_class in visual_effects_list:
            effect_widget = EffectWidget(name, effect_class, callback=self.update_preview)
            self.visual_effects.append(effect_widget)
            self.video_effects_layout.addWidget(effect_widget)
        
        self.video_effects_layout.addStretch()
        scroll.setWidget(scroll_widget)
        effects_layout.addWidget(scroll)
        effects_group.setLayout(effects_layout)
        right_panel.addWidget(effects_group)
        
        layout.addLayout(right_panel, stretch=1)
        
        return video_widget
    
    def create_audio_tab(self):
        audio_widget = QWidget()
        layout = QHBoxLayout(audio_widget)
        layout.setSpacing(10)
        
        # Left panel - Waveform
        left_panel = QVBoxLayout()
        self.waveform = AudioWaveformWidget()
        left_panel.addWidget(self.waveform)
        
        # Audio controls
        audio_controls = QHBoxLayout()
        self.audio_play_btn = QPushButton("Lecture")
        self.audio_stop_btn = QPushButton("Stop")
        self.audio_play_btn.clicked.connect(self.play_audio)
        self.audio_stop_btn.clicked.connect(self.stop_audio)
        
        # Initially disable controls
        self.audio_play_btn.setEnabled(False)
        self.audio_stop_btn.setEnabled(False)
        
        # Add time label
        self.audio_time_label = QLabel("00:00 / 00:00")
        
        audio_controls.addWidget(self.audio_play_btn)
        audio_controls.addWidget(self.audio_stop_btn)
        audio_controls.addWidget(self.audio_time_label)
        audio_controls.addStretch()
        left_panel.addLayout(audio_controls)
        
        layout.addLayout(left_panel, stretch=2)
        
        # Right panel - Effects
        right_panel = QVBoxLayout()
        effects_group = QGroupBox("Effets Audio")
        effects_layout = QVBoxLayout()
        
        # Create scrollable area for effects
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.audio_effects_layout = QVBoxLayout(scroll_widget)
        
        # Add audio effects
        self.audio_effects = []
        audio_effects_list = [
            ("Pitch Shift", PitchShift),
            ("Reverb", Reverb),
            ("Echo", Echo),
            ("Bass Boost", BassBoost),
            ("Normalize", Normalize),
            ("Compression", Compression)
        ]
        
        for name, effect_class in audio_effects_list:
            effect_widget = EffectWidget(
                name, 
                effect_class,
                callback=self.preview_audio_with_effects
            )
            self.audio_effects.append(effect_widget)
            self.audio_effects_layout.addWidget(effect_widget)
        
        self.audio_effects_layout.addStretch()
        scroll.setWidget(scroll_widget)
        effects_layout.addWidget(scroll)
        effects_group.setLayout(effects_layout)
        right_panel.addWidget(effects_group)
        
        layout.addLayout(right_panel, stretch=1)
        
        return audio_widget
    
    def preview_audio_with_effects(self):
        """Generate a preview of audio with current effects"""
        if not self.input_video:
            return
            
        try:
            # Stop any current playback
            if self.audio_player and self.audio_player.playbackState() == PlaybackState.Playing:
                self.audio_player.stop()
            
            # Get active audio effects
            active_effects = [
                effect_widget.get_effect() 
                for effect_widget in self.audio_effects 
                if effect_widget.get_effect()
            ]
            
            # Process audio preview
            preview_audio_path = self.video_processor.process_preview_audio(
                self.input_video,
                active_effects
            )
            
            # Update audio player
            if not self.audio_player:
                self.audio_player = QMediaPlayer()
                self.audio_output = QAudioOutput()
                self.audio_player.setAudioOutput(self.audio_output)
                self.audio_player.positionChanged.connect(self.update_audio_time)
                self.audio_player.mediaStatusChanged.connect(self.handle_audio_status)
            
            self.audio_player.setSource(QUrl.fromLocalFile(preview_audio_path))
            
            # Update waveform
            self.waveform.update_waveform(preview_audio_path)
            
            # Store preview audio path for cleanup
            if self.preview_audio and os.path.exists(self.preview_audio):
                try:
                    os.remove(self.preview_audio)
                except:
                    pass
            self.preview_audio = preview_audio_path
            
            # Enable audio controls
            self.audio_play_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la prévisualisation audio: {str(e)}")
    
    def handle_audio_status(self, status):
        """Handle audio player status changes"""
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.audio_play_btn.setEnabled(True)
            self.audio_stop_btn.setEnabled(False)
            self.audio_time_label.setText("00:00 / 00:00")
    
    def import_video(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une vidéo",
            "",
            "Vidéos (*.mp4 *.avi *.mov *.mkv)"
        )
        
        if file_name:
            try:
                self.input_video = file_name
                
                # Update UI
                self.import_btn.setText(os.path.basename(file_name))
                self.status_label.setText("Vidéo chargée: " + os.path.basename(file_name))
                self.export_btn.setEnabled(True)
                
                # Initialize video capture
                if self.cap is not None:
                    self.cap.release()
                self.cap = cv2.VideoCapture(file_name)
                
                # Enable video controls
                self.play_btn.setEnabled(True)
                self.update_preview()
                
                # Generate initial audio preview
                self.preview_audio_with_effects()
                
                QMessageBox.information(self, "Succès", "Vidéo importée avec succès!")
                
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'importation: {str(e)}")
    
    def play_video(self):
        if self.cap is not None:
            self.preview_timer.start(33)  # ~30 fps
            self.play_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
    
    def stop_video(self):
        self.preview_timer.stop()
        if self.cap is not None:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.play_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def play_audio(self):
        if self.input_video:
            # Generate new preview with current effects if not already playing
            if not self.audio_player or self.audio_player.playbackState() != PlaybackState.Playing:
                self.preview_audio_with_effects()
                
                if self.audio_player:
                    self.audio_output.setVolume(1.0)
                    self.audio_player.play()
                    self.audio_play_btn.setEnabled(False)
                    self.audio_stop_btn.setEnabled(True)
    
    def stop_audio(self):
        if self.audio_player:
            self.audio_player.stop()
            self.audio_play_btn.setEnabled(True)
            self.audio_stop_btn.setEnabled(False)
    
    def update_preview(self):
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                # Create a copy of the frame
                processed_frame = frame.copy()
                
                # Apply active effects
                for effect_widget in self.visual_effects:
                    effect = effect_widget.get_effect()
                    if effect:
                        try:
                            processed_frame = effect.apply(processed_frame)
                        except Exception as e:
                            print(f"Erreur lors de l'application de l'effet: {str(e)}")
                
                self.video_preview.update_frame(processed_frame)
            else:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    def update_audio_time(self):
        if self.audio_player and self.audio_player.duration() > 0:
            current = self.audio_player.position() // 1000  # Convert to seconds
            total = self.audio_player.duration() // 1000
            self.audio_time_label.setText(
                f"{current//60:02d}:{current%60:02d} / {total//60:02d}:{total%60:02d}"
            )
    
    def export_video(self):
        if not self.input_video:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord importer une vidéo!")
            return
        
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter la vidéo",
            "",
            "Vidéo MP4 (*.mp4)"
        )
        
        if file_name:
            try:
                # Get active effects
                active_video_effects = [
                    effect_widget.get_effect() 
                    for effect_widget in self.visual_effects 
                    if effect_widget.get_effect()
                ]
                
                active_audio_effects = [
                    effect_widget.get_effect() 
                    for effect_widget in self.audio_effects 
                    if effect_widget.get_effect()
                ]
                
                # Progress callback
                def update_progress(progress):
                    self.progress_bar.setValue(int(progress))
                    self.status_label.setText(f"Export en cours... {int(progress)}%")
                    QApplication.processEvents()
                
                # Process video and audio
                self.status_label.setText("Traitement de la vidéo et de l'audio...")
                self.video_processor.process(
                    self.input_video,
                    file_name,
                    active_video_effects,
                    active_audio_effects,
                    update_progress
                )
                
                self.status_label.setText("Export terminé!")
                QMessageBox.information(self, "Succès", "Vidéo exportée avec succès!")
                
            except Exception as e:
                self.status_label.setText("Erreur lors de l'export!")
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'exportation: {str(e)}")
            finally:
                self.progress_bar.setValue(0)
                self.status_label.setText("Prêt")
    
    def closeEvent(self, event):
        # Stop any audio playback
        if self.audio_player:
            self.audio_player.stop()
            self.audio_player = None
        
        # Release video capture
        if self.cap is not None:
            self.cap.release()
        
        # Cleanup processor
        self.video_processor.cleanup()
        
        # Remove preview audio if exists
        if self.preview_audio and os.path.exists(self.preview_audio):
            try:
                os.remove(self.preview_audio)
            except:
                pass
        
        super().closeEvent(event)
