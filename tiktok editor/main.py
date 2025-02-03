import sys
from PyQt6.QtWidgets import QApplication
import os
from gui.main_window import MainWindow

def ensure_directories():
    """Ensure all necessary directories exist"""
    directories = [
        'effects/visual',
        'effects/audio',
        'processors',
        'utils',
        'gui',
        'temp'
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    # Create necessary directories
    ensure_directories()
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Load and apply the galaxy style
    style_path = 'styles/dark_galaxy.qss'
    if os.path.exists(style_path):
        with open(style_path, 'r') as style_file:
            app.setStyleSheet(style_file.read())
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
