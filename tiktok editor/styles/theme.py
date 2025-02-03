class GalaxyTheme:
    # Couleurs principales
    PRIMARY = "#6d4ed7"
    PRIMARY_LIGHT = "#8a6df3"
    PRIMARY_DARK = "#2e1f5e"
    
    # Couleurs de fond
    BACKGROUND_DARK = "#0a0b1a"
    BACKGROUND_MEDIUM = "#1a1b2e"
    BACKGROUND_LIGHT = "#2e1f5e"
    
    # Couleurs de texte
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#8a8db9"
    TEXT_DISABLED = "#666666"
    
    # Couleurs de bordure
    BORDER = "#453c7d"
    BORDER_LIGHT = "#554c8d"
    
    # Couleurs d'état
    SUCCESS = "#4CAF50"
    WARNING = "#FFC107"
    ERROR = "#f44336"
    
    # Dimensions
    BORDER_RADIUS = "6px"
    PADDING = "8px"
    
    @classmethod
    def get_stylesheet(cls) -> str:
        return f"""
            /* Application générale */
            QMainWindow {{
                background-color: {cls.BACKGROUND_DARK};
            }}
            
            QWidget {{
                color: {cls.TEXT_PRIMARY};
            }}
            
            /* Boutons */
            QPushButton {{
                background-color: {cls.PRIMARY_DARK};
                color: {cls.TEXT_PRIMARY};
                border: none;
                padding: 8px 16px;
                border-radius: {cls.BORDER_RADIUS};
                min-width: 100px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {cls.PRIMARY};
            }}
            
            QPushButton:pressed {{
                background-color: {cls.PRIMARY_DARK};
            }}
            
            QPushButton:disabled {{
                background-color: {cls.BACKGROUND_MEDIUM};
                color: {cls.TEXT_DISABLED};
            }}
            
            /* GroupBox */
            QGroupBox {{
                background-color: {cls.BACKGROUND_MEDIUM};
                border: 1px solid {cls.BORDER};
                border-radius: {cls.BORDER_RADIUS};
                margin-top: 12px;
                padding: 12px;
            }}
            
            QGroupBox::title {{
                color: {cls.TEXT_PRIMARY};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            
            /* Progress Bar */
            QProgressBar {{
                border: 2px solid {cls.BORDER};
                border-radius: {cls.BORDER_RADIUS};
                text-align: center;
                color: {cls.TEXT_PRIMARY};
                background-color: {cls.BACKGROUND_MEDIUM};
            }}
            
            QProgressBar::chunk {{
                background-color: {cls.PRIMARY};
                border-radius: 3px;
            }}
            
            /* Scroll Area */
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            
            QScrollBar:vertical {{
                background-color: {cls.BACKGROUND_MEDIUM};
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {cls.PRIMARY_DARK};
                min-height: 20px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {cls.PRIMARY};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            /* Tabs */
            QTabWidget::pane {{
                border: 2px solid {cls.BORDER};
                border-radius: {cls.BORDER_RADIUS};
                background-color: {cls.BACKGROUND_MEDIUM};
            }}
            
            QTabBar::tab {{
                background-color: {cls.BACKGROUND_MEDIUM};
                color: {cls.TEXT_PRIMARY};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {cls.PRIMARY_DARK};
            }}
            
            QTabBar::tab:hover {{
                background-color: {cls.PRIMARY};
            }}
            
            /* Labels */
            QLabel {{
                color: {cls.TEXT_SECONDARY};
            }}
            
            QLabel#statusLabel {{
                color: {cls.PRIMARY};
                font-weight: bold;
            }}
            
            /* ComboBox */
            QComboBox {{
                background-color: {cls.BACKGROUND_LIGHT};
                color: {cls.TEXT_PRIMARY};
                border: 1px solid {cls.BORDER};
                border-radius: 4px;
                padding: 5px;
                min-width: 100px;
            }}
            
            QComboBox:hover {{
                border-color: {cls.PRIMARY};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            QComboBox::down-arrow {{
                image: url(resources/down_arrow.png);
                width: 12px;
                height: 12px;
            }}
            
            /* Sliders */
            QSlider::groove:horizontal {{
                border: 1px solid {cls.BORDER};
                height: 4px;
                background: {cls.BACKGROUND_LIGHT};
                margin: 0px;
                border-radius: 2px;
            }}
            
            QSlider::handle:horizontal {{
                background: {cls.PRIMARY};
                border: none;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}
            
            QSlider::handle:horizontal:hover {{
                background: {cls.PRIMARY_LIGHT};
            }}
            
            /* CheckBox */
            QCheckBox {{
                color: {cls.TEXT_PRIMARY};
                spacing: 5px;
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {cls.BORDER};
                border-radius: 4px;
                background-color: {cls.BACKGROUND_MEDIUM};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {cls.PRIMARY};
                image: url(resources/check.png);
            }}
            
            QCheckBox::indicator:hover {{
                border-color: {cls.PRIMARY};
            }}
            
            /* Effect Widget */
            .EffectWidget {{
                background-color: {cls.BACKGROUND_MEDIUM};
                border: 1px solid {cls.BORDER};
                border-radius: {cls.BORDER_RADIUS};
                padding: {cls.PADDING};
                margin: 2px;
            }}
            
            .EffectWidget:hover {{
                border-color: {cls.PRIMARY};
            }}
            
            /* Tooltip */
            QToolTip {{
                background-color: {cls.BACKGROUND_DARK};
                color: {cls.TEXT_PRIMARY};
                border: 1px solid {cls.BORDER};
                border-radius: 4px;
                padding: 4px;
            }}
        """
