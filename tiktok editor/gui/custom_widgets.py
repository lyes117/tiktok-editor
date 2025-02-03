from PyQt6.QtWidgets import (QWidget, QPushButton, QLabel, QSlider, 
                           QProgressBar, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from styles.theme import GalaxyTheme
from resources.icons import Icons

class IconButton(QPushButton):
    def __init__(self, icon_name: str, tooltip: str = "", parent=None):
        super().__init__(parent)
        self.setIcon(QIcon(Icons.get_path(icon_name)))
        self.setToolTip(tooltip)
        self.setFixedSize(32, 32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class AnimatedProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._animation_timer = None
        self.setTextVisible(True)
        self.setFormat("%p%")
    
    def start_animation(self):
        if not self._animation_timer:
            from PyQt6.QtCore import QTimer
            self._animation_timer = QTimer()
            self._animation_timer.timeout.connect(self._update_animation)
            self._animation_timer.start(50)
    
    def stop_animation(self):
        if self._animation_timer:
            self._animation_timer.stop()
            self._animation_timer = None
    
    def _update_animation(self):
        value = self.value()
        if value < self.maximum():
            self.setValue(value + 1)
        else:
            self.setValue(0)

class SmoothSlider(QSlider):
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setTracking(True)
        self._animation_timer = None
        self._target_value = 0
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            value = self._pixel_pos_to_value(event.pos())
            self.smooth_set_value(value)
        super().mousePressEvent(event)
    
    def _pixel_pos_to_value(self, pos):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        groove = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider, opt,
            QStyle.SubControl.SC_SliderGroove, self)
        handle = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider, opt,
            QStyle.SubControl.SC_SliderHandle, self)
        
        if self.orientation() == Qt.Orientation.Horizontal:
            slider_length = handle.width()
            slider_min = groove.x()
            slider_max = groove.right() - slider_length + 1
            return self.minimum() + ((self.maximum() - self.minimum()) *
                (pos.x() - slider_min) / (slider_max - slider_min))
        else:
            slider_length = handle.height()
            slider_min = groove.y()
            slider_max = groove.bottom() - slider_length + 1
            return self.minimum() + ((self.maximum() - self.minimum()) *
                (slider_max - pos.y()) / (slider_max - slider_min))
    
    def smooth_set_value(self, value):
        self._target_value = value
        if not self._animation_timer:
            from PyQt6.QtCore import QTimer
            self._animation_timer = QTimer()
            self._animation_timer.timeout.connect(self._update_value)
            self._animation_timer.start(16)  # ~60fps
    
    def _update_value(self):
        current = self.value()
        diff = self._target_value - current
        if abs(diff) < 1:
            self.setValue(int(self._target_value))
            self._animation_timer.stop()
            self._animation_timer = None
        else:
            self.setValue(int(current + diff * 0.2))

class EffectCard(QFrame):
    clicked = pyqtSignal()
    
    def __init__(self, title: str, description: str, icon_name: str = None, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        
        if icon_name:
            icon = QLabel()
            icon.setPixmap(QIcon(Icons.get_path(icon_name)).pixmap(32, 32))
            layout.addWidget(icon, alignment=Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {GalaxyTheme.TEXT_PRIMARY}; font-weight: bold;")
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"color: {GalaxyTheme.TEXT_SECONDARY};")
        layout.addWidget(desc_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setStyleSheet(f"""
            EffectCard {{
                background-color: {GalaxyTheme.BACKGROUND_MEDIUM};
                border: 1px solid {GalaxyTheme.BORDER};
                border-radius: {GalaxyTheme.BORDER_RADIUS};
                padding: {GalaxyTheme.PADDING};
            }}
            
            EffectCard:hover {{
                background-color: {GalaxyTheme.BACKGROUND_LIGHT};
                border-color: {GalaxyTheme.PRIMARY};
            }}
        """)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
