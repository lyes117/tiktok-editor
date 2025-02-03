from .base_effect import BaseVisualEffect
import cv2
import numpy as np

class ColorFilter(BaseVisualEffect):
    def __init__(self, intensity=0.5):
        super().__init__(intensity)
    
    def apply(self, frame):
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Modify saturation based on intensity
        hsv[:,:,1] = cv2.multiply(hsv[:,:,1], 1 + self.intensity)
        
        # Convert back to BGR
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
