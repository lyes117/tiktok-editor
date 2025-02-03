import cv2
import numpy as np

class VisualEffect:
    def __init__(self):
        pass

    def apply(self, frame):
        return frame

class Crop(VisualEffect):
    def apply(self, frame):
        height, width = frame.shape[:2]
        new_width = int(height * 9/16)
        start = (width - new_width) // 2
        return frame[:, start:start+new_width]

class LightBar(VisualEffect):
    def __init__(self):
        self.position = 0
        self.direction = 1
        
    def apply(self, frame):
        height, width = frame.shape[:2]
        frame = frame.copy()
        bar_pos = int(self.position * width)
        frame[:, max(0, bar_pos-2):min(width, bar_pos+2)] += 50
        self.position += 0.01 * self.direction
        if self.position >= 1 or self.position <= 0:
            self.direction *= -1
        return frame

class Blur(VisualEffect):
    def apply(self, frame):
        return cv2.GaussianBlur(frame, (15, 15), 0)

class ColorFilter(VisualEffect):
    def apply(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv[:,:,1] = hsv[:,:,1] * 1.2  # Increase saturation
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
