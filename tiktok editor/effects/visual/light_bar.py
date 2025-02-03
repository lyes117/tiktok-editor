from .base_effect import BaseVisualEffect
import cv2
import numpy as np

class LightBar(BaseVisualEffect):
    def __init__(self, intensity=0.5):
        super().__init__(intensity)
        self.position = 0
        self.direction = 1
    
    def apply(self, frame):
        height, width = frame.shape[:2]
        frame = frame.copy()
        bar_pos = int(self.position * width)
        frame[:, max(0, bar_pos-2):min(width, bar_pos+2)] += int(50 * self.intensity)
        self.position += 0.01 * self.direction
        if self.position >= 1 or self.position <= 0:
            self.direction *= -1
        return frame
