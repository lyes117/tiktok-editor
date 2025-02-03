from .base_effect import BaseVisualEffect
import cv2

class Mirror(BaseVisualEffect):
    def __init__(self, intensity=0.5):
        super().__init__(intensity)
    
    def apply(self, frame):
        if self.intensity > 0.5:  # Vertical mirror
            return cv2.flip(frame, 0)
        else:  # Horizontal mirror
            return cv2.flip(frame, 1)
