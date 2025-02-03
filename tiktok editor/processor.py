import cv2
import numpy as np
from effects.visual_effects import *
from effects.audio_effects import *

class VideoProcessor:
    def __init__(self):
        self.visual_effects = []
        self.audio_effects = []
    
    def add_visual_effect(self, effect):
        self.visual_effects.append(effect)
    
    def add_audio_effect(self, effect):
        self.audio_effects.append(effect)
    
    def process_video(self, input_path, output_path):
        cap = cv2.VideoCapture(input_path)
        
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Apply visual effects
            for effect in self.visual_effects:
                frame = effect.apply(frame)
            
            out.write(frame)
        
        cap.release()
        out.release()
