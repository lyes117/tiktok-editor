from .base_effect import BaseVisualEffect
import cv2
import numpy as np

class Vignette(BaseVisualEffect):
    def __init__(self, intensity=0.5):
        super().__init__(intensity)
    
    def apply(self, frame):
        rows, cols = frame.shape[:2]
        
        # Generate vignette mask
        kernel_x = cv2.getGaussianKernel(cols, cols/2)
        kernel_y = cv2.getGaussianKernel(rows, rows/2)
        kernel = kernel_y * kernel_x.T
        mask = kernel / kernel.max()
        
        # Apply intensity
        mask = (1 - self.intensity) + (mask * self.intensity)
        
        # Apply mask to each channel
        for i in range(3):
            frame[:,:,i] = frame[:,:,i] * mask
            
        return frame.astype(np.uint8)
