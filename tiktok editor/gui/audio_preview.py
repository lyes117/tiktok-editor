import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from io import BytesIO
import os
import numpy as np
import soundfile as sf

class AudioWaveformWidget(QLabel):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(480, 150)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setObjectName("waveformWidget")
        self.setText("Forme d'onde Audio")
        self.setStyleSheet("""
            QLabel {
                background-color: #0d0e23;
                border: 2px solid #453c7d;
                border-radius: 8px;
                color: #6d4ed7;
                font-size: 14px;
            }
        """)
        plt.style.use('dark_background')
    
    def update_waveform(self, audio_path):
        if not audio_path or not os.path.exists(audio_path):
            self.setText("Aucun fichier audio")
            return
            
        try:
            # Load audio file using soundfile
            audio_data, sample_rate = sf.read(audio_path)
            
            # Create figure with dark background
            plt.figure(figsize=(10, 2), facecolor='#0d0e23')
            ax = plt.gca()
            ax.set_facecolor('#0d0e23')
            
            # Plot waveform
            plt.axis('off')
            plt.margins(x=0, y=0.1)
            
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Calculate time array
            times = np.arange(len(audio_data)) / sample_rate
            
            # Plot the waveform
            plt.plot(times, audio_data, color='#6d4ed7', alpha=0.6, linewidth=0.5)
            
            # Add subtle grid
            ax.grid(True, color='#453c7d', alpha=0.3)
            
            # Remove axis spines
            for spine in ax.spines.values():
                spine.set_visible(False)
            
            # Save to buffer
            buf = BytesIO()
            plt.savefig(buf, 
                       format='png', 
                       facecolor='#0d0e23',
                       edgecolor='none',
                       transparent=True,
                       bbox_inches='tight',
                       pad_inches=0,
                       dpi=100)
            buf.seek(0)
            plt.close()
            
            # Convert to QPixmap and display
            waveform_img = QImage.fromData(buf.getvalue())
            pixmap = QPixmap.fromImage(waveform_img)
            
            # Scale pixmap while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.setPixmap(scaled_pixmap)
            
        except Exception as e:
            self.setText(f"Erreur de chargement: {str(e)}")
            print(f"Erreur lors de la génération de la forme d'onde: {str(e)}")
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Update waveform display when widget is resized
        if self.pixmap():
            scaled_pixmap = self.pixmap().scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
