from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, 
                           QSlider, QLabel, QComboBox, QGroupBox, QGridLayout,
                           QScrollArea, QFrame, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal
from effects.visual.crop import VideoRatio
from typing import Dict, Any, Optional

class DraggableEffectList(QFrame):
    effectOrderChanged = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.layout = QVBoxLayout(self)
        self.effects = []
        
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1b2e;
                border: 2px solid #453c7d;
                border-radius: 8px;
                padding: 5px;
            }
        """)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-effect"):
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        if event.mimeData().hasFormat("application/x-effect"):
            index = self._get_drop_index(event.pos().y())
            effect_data = event.mimeData().data("application/x-effect")
            self._insert_effect(index, effect_data)
            event.accept()
            self.effectOrderChanged.emit(self.effects)
    
    def _get_drop_index(self, y: int) -> int:
        for i, effect in enumerate(self.effects):
            if y < effect.pos().y() + effect.height() / 2:
                return i
        return len(self.effects)
    
    def _insert_effect(self, index: int, effect_data: Any):
        effect_widget = EffectWidget.from_data(effect_data)
        self.effects.insert(index, effect_widget)
        self._update_layout()
    
    def _update_layout(self):
        # Clear layout
        while self.layout.count():
            self.layout.takeAt(0)
        
        # Re-add effects
        for effect in self.effects:
            self.layout.addWidget(effect)
        
        self.layout.addStretch()

class EffectSettingsWidget(QWidget):
    settingChanged = pyqtSignal(str, object)
    
    def __init__(self, effect, parent=None):
        super().__init__(parent)
        self.effect = effect
        self.settings: Dict[str, Any] = {}
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Common settings group
        common_group = QGroupBox("Paramètres généraux")
        common_layout = QGridLayout()
        
        # Intensity slider if applicable
        if hasattr(self.effect, 'intensity'):
            intensity_label = QLabel("Intensité:")
            intensity_slider = QSlider(Qt.Orientation.Horizontal)
            intensity_slider.setRange(0, 100)
            intensity_slider.setValue(int(getattr(self.effect, 'intensity', 0.5) * 100))
            intensity_slider.valueChanged.connect(
                lambda v: self._update_setting('intensity', v/100)
            )
            common_layout.addWidget(intensity_label, 0, 0)
            common_layout.addWidget(intensity_slider, 0, 1)
        
        # Effect-specific parameters
        if hasattr(self.effect, 'get_parameters'):
            row = 1
            for param_name, param_info in self.effect.get_parameters().items():
                self._add_parameter_widget(param_name, param_info, common_layout, row)
                row += 1
        
        common_group.setLayout(common_layout)
        layout.addWidget(common_group)
        
        # Apply styling
        self.setStyleSheet("""
            QGroupBox {
                background-color: #1a1b2e;
                border: 1px solid #453c7d;
                border-radius: 6px;
                margin-top: 12px;
                padding: 12px;
            }
            QGroupBox::title {
                color: white;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #8a8db9;
            }
            QSlider::groove:horizontal {
                border: 1px solid #453c7d;
                height: 4px;
                background: #2e1f5e;
                margin: 0px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #6d4ed7;
                border: none;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            QComboBox {
                background-color: #2e1f5e;
                color: white;
                border: 1px solid #453c7d;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(resources/down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
    
    def _add_parameter_widget(self, param_name: str, param_info: dict, layout: QGridLayout, row: int):
        """Add a widget for a specific parameter"""
        label = QLabel(f"{param_info.get('label', param_name)}:")
        layout.addWidget(label, row, 0)
        
        param_type = param_info.get('type', 'float')
        current_value = param_info.get('default', 0)
        
        if param_type == 'float' or param_type == 'int':
            slider = QSlider(Qt.Orientation.Horizontal)
            min_val = param_info.get('min', 0)
            max_val = param_info.get('max', 100)
            
            if param_type == 'float':
                slider.setRange(int(min_val * 100), int(max_val * 100))
                slider.setValue(int(current_value * 100))
                slider.valueChanged.connect(
                    lambda v: self._update_setting(param_name, v/100)
                )
            else:
                slider.setRange(min_val, max_val)
                slider.setValue(current_value)
                slider.valueChanged.connect(
                    lambda v: self._update_setting(param_name, v)
                )
            
            layout.addWidget(slider, row, 1)
            
        elif param_type == 'choice':
            combo = QComboBox()
            for choice in param_info.get('choices', []):
                combo.addItem(str(choice))
            combo.setCurrentText(str(current_value))
            combo.currentTextChanged.connect(
                lambda v: self._update_setting(param_name, v)
            )
            layout.addWidget(combo, row, 1)
        
        elif param_type == 'bool':
            checkbox = QCheckBox()
            checkbox.setChecked(bool(current_value))
            checkbox.stateChanged.connect(
                lambda v: self._update_setting(param_name, bool(v))
            )
            layout.addWidget(checkbox, row, 1)
    
    def _update_setting(self, name: str, value: Any):
        """Update a setting value and emit change signal"""
        self.settings[name] = value
        self.settingChanged.emit(name, value)
        if hasattr(self.effect, 'update_setting'):
            self.effect.update_setting(name, value)

class EffectWidget(QWidget):
    effectChanged = pyqtSignal()
    
    def __init__(self, name, effect_class, callback=None):
        super().__init__()
        self.effect_name = name
        self.effect_class = effect_class
        self.effect_instance = None
        self.callback = callback
        self.settings_widget: Optional[EffectSettingsWidget] = None
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Header with enable/disable and name
        header_layout = QHBoxLayout()
        self.toggle = QCheckBox(self.effect_name)
        self.toggle.stateChanged.connect(self.on_toggle)
        header_layout.addWidget(self.toggle)
        
        # Settings button
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(24, 24)
        settings_btn.clicked.connect(self.toggle_settings)
        header_layout.addWidget(settings_btn)
        
        layout.addLayout(header_layout)
        
        # Settings panel (initially hidden)
        self.settings_container = QWidget()
        self.settings_container.hide()
        layout.addWidget(self.settings_container)
        
        # Special handling for Crop effect
        if self.effect_name == "Crop":
            self._setup_crop_ui()
        
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1b2e;
                border: 1px solid #453c7d;
                border-radius: 5px;
                padding: 5px;
            }
            QCheckBox {
                color: #ffffff;
                font-weight: bold;
                background: transparent;
                border: none;
            }
            QPushButton {
                background-color: #2e1f5e;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3d2b7a;
            }
        """)
    
    def _setup_crop_ui(self):
        """Setup special UI for Crop effect"""
        settings_layout = QVBoxLayout(self.settings_container)
        
        # Ratio selector
        ratio_layout = QHBoxLayout()
        ratio_label = QLabel("Ratio:")
        self.ratio_combo = QComboBox()
        for ratio in VideoRatio:
            self.ratio_combo.addItem(ratio.label, ratio)
        self.ratio_combo.currentIndexChanged.connect(self.on_ratio_change)
        ratio_layout.addWidget(ratio_label)
        ratio_layout.addWidget(self.ratio_combo)
        settings_layout.addLayout(ratio_layout)
        
        # Face tracking toggle
        self.face_track = QCheckBox("Track Face")
        self.face_track.stateChanged.connect(self.on_face_track_change)
        settings_layout.addWidget(self.face_track)
    
    def toggle_settings(self):
        """Toggle visibility of settings panel"""
        if self.settings_container.isHidden():
            self.settings_container.show()
        else:
            self.settings_container.hide()
    
    def on_toggle(self, state):
        if state == Qt.CheckState.Checked.value:
            if self.effect_name == "Crop":
                ratio = self.ratio_combo.currentData()
                track_face = self.face_track.isChecked()
                self.effect_instance = self.effect_class(ratio=ratio, track_face=track_face)
            else:
                self.effect_instance = self.effect_class()
                if self.settings_widget:
                    for name, value in self.settings_widget.settings.items():
                        if hasattr(self.effect_instance, 'update_setting'):
                            self.effect_instance.update_setting(name, value)
        else:
            self.effect_instance = None
        
        if self.callback:
            self.callback()
        self.effectChanged.emit()
    
    def on_ratio_change(self, index):
        if self.toggle.isChecked():
            ratio = self.ratio_combo.currentData()
            track_face = self.face_track.isChecked()
            self.effect_instance = self.effect_class(ratio=ratio, track_face=track_face)
            if self.callback:
                self.callback()
            self.effectChanged.emit()
    
    def on_face_track_change(self, state):
        if self.toggle.isChecked():
            ratio = self.ratio_combo.currentData()
            track_face = self.face_track.isChecked()
            self.effect_instance = self.effect_class(ratio=ratio, track_face=track_face)
            if self.callback:
                self.callback()
            self.effectChanged.emit()
    
    def get_effect(self):
        return self.effect_instance
    
    @classmethod
    def from_data(cls, data):
        """Create an effect widget from serialized data"""
        widget = cls(data['name'], data['effect_class'])
        if 'settings' in data:
            widget.settings_widget = EffectSettingsWidget(data['effect_class'])
            for name, value in data['settings'].items():
                widget.settings_widget._update_setting(name, value)
        return widget
