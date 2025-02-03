from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
import cv2

class VideoPreviewWidget(QLabel):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(480, 270)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setObjectName("previewArea")
        self.setText("Aperçu Vidéo")
        self.setStyleSheet("""
            QLabel {
                background-color: #0d0e23;
                border: 2px solid #453c7d;
                border-radius: 8px;
                color: #6d4ed7;
                font-size: 14px;
            }
        """)
    
    def update_frame(self, frame):
        if frame is not None:
            try:
                height, width = frame.shape[:2]
                scale = min(self.width() / width, self.height() / height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                
                # Resize frame
                frame = cv2.resize(frame, (new_width, new_height))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to QImage
                img = QImage(frame.data, frame.shape[1], frame.shape[0], 
                           frame.strides[0], QImage.Format.Format_RGB888)
                
                # Convert to QPixmap and display
                pixmap = QPixmap.fromImage(img)
                self.setPixmap(pixmap)
            except Exception as e:
                self.setText(f"Erreur d'affichage: {str(e)}")
