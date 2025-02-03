from .base_effect import BaseVisualEffect
import cv2

class Blur(BaseVisualEffect):
    def __init__(self, intensity=0.5):
        super().__init__(intensity)
    
    def apply(self, frame):
        # Calculate kernel size based on intensity (odd numbers only)
        kernel_size = int(self.intensity * 20) * 2 + 1
        return cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)
