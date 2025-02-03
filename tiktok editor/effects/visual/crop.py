import cv2
import numpy as np
import mediapipe as mp
from .base_effect import BaseVisualEffect
from enum import Enum
from dataclasses import dataclass
from typing import Tuple, Optional

class VideoRatio(Enum):
    RATIO_16_9 = (16/9, "16:9")
    RATIO_9_16 = (9/16, "9:16")
    RATIO_4_3 = (4/3, "4:3")
    RATIO_1_1 = (1, "1:1")
    RATIO_21_9 = (21/9, "21:9")

    @property
    def ratio_value(self) -> float:
        return self.value[0]

    @property
    def label(self) -> str:
        return self.value[1]

@dataclass
class CropRegion:
    x: int
    y: int
    width: int
    height: int

class Crop(BaseVisualEffect):
    def __init__(self, ratio: VideoRatio = VideoRatio.RATIO_16_9, track_face: bool = False):
        super().__init__()
        self.ratio = ratio
        self.track_face = track_face
        
        # Initialize face detection if needed
        if self.track_face:
            self.mp_face_detection = mp.solutions.face_detection
            self.face_detection = self.mp_face_detection.FaceDetection(
                model_selection=1,  # 0 for close faces, 1 for far faces
                min_detection_confidence=0.5
            )
            
            # For smoothing face tracking
            self.last_face_region = None
            self.smoothing_factor = 0.3  # Adjust for smoother transitions
            
            # For stabilization
            self.stabilization_buffer = []
            self.buffer_size = 5  # Number of frames to consider for stabilization
    
    def _detect_face(self, frame: np.ndarray) -> Optional[CropRegion]:
        """Detect face in frame using MediaPipe"""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_detection.process(rgb_frame)
            
            if results.detections:
                # Get the first detected face
                detection = results.detections[0]
                bbox = detection.location_data.relative_bounding_box
                
                # Convert relative coordinates to absolute
                frame_height, frame_width = frame.shape[:2]
                x = max(0, int(bbox.xmin * frame_width))
                y = max(0, int(bbox.ymin * frame_height))
                width = min(int(bbox.width * frame_width), frame_width - x)
                height = min(int(bbox.height * frame_height), frame_height - y)
                
                # Add margin around face (75% of face size)
                margin_x = int(width * 0.75)
                margin_y = int(height * 0.75)
                
                # Calculate new dimensions ensuring they stay within frame
                new_x = max(0, x - margin_x)
                new_y = max(0, y - margin_y)
                new_width = min(frame_width - new_x, width + 2 * margin_x)
                new_height = min(frame_height - new_y, height + 2 * margin_y)
                
                # Ensure minimum size
                min_size = min(frame_width, frame_height) // 4
                new_width = max(new_width, min_size)
                new_height = max(new_height, min_size)
                
                return CropRegion(new_x, new_y, new_width, new_height)
            
            return None
            
        except Exception as e:
            print(f"Face detection error: {str(e)}")
            return None
    
    def _smooth_region(self, new_region: CropRegion) -> CropRegion:
        """Apply smoothing to face tracking region"""
        if self.last_face_region is None:
            self.last_face_region = new_region
            return new_region
        
        # Add to stabilization buffer
        self.stabilization_buffer.append(new_region)
        if len(self.stabilization_buffer) > self.buffer_size:
            self.stabilization_buffer.pop(0)
        
        # Calculate average position from buffer
        avg_x = sum(r.x for r in self.stabilization_buffer) / len(self.stabilization_buffer)
        avg_y = sum(r.y for r in self.stabilization_buffer) / len(self.stabilization_buffer)
        avg_w = sum(r.width for r in self.stabilization_buffer) / len(self.stabilization_buffer)
        avg_h = sum(r.height for r in self.stabilization_buffer) / len(self.stabilization_buffer)
        
        # Apply smoothing between last position and average position
        smooth_x = int(self.last_face_region.x * (1 - self.smoothing_factor) + 
                      avg_x * self.smoothing_factor)
        smooth_y = int(self.last_face_region.y * (1 - self.smoothing_factor) + 
                      avg_y * self.smoothing_factor)
        smooth_w = int(self.last_face_region.width * (1 - self.smoothing_factor) + 
                      avg_w * self.smoothing_factor)
        smooth_h = int(self.last_face_region.height * (1 - self.smoothing_factor) + 
                      avg_h * self.smoothing_factor)
        
        # Update last region
        self.last_face_region = CropRegion(smooth_x, smooth_y, smooth_w, smooth_h)
        return self.last_face_region
    
    def _get_crop_dimensions(self, frame: np.ndarray) -> Tuple[int, int, int, int]:
        """Calculate crop dimensions based on ratio and face tracking"""
        height, width = frame.shape[:2]
        target_ratio = self.ratio.ratio_value
        
        if self.track_face:
            face_region = self._detect_face(frame)
            if face_region:
                # Smooth the tracking
                face_region = self._smooth_region(face_region)
                
                # Calculate crop dimensions while maintaining ratio
                if target_ratio > 1:  # Wider than tall
                    crop_height = face_region.height
                    crop_width = int(crop_height * target_ratio)
                else:  # Taller than wide
                    crop_width = face_region.width
                    crop_height = int(crop_width / target_ratio)
                
                # Ensure dimensions are even
                crop_width = (crop_width // 2) * 2
                crop_height = (crop_height // 2) * 2
                
                # Center the crop around face
                x = face_region.x + (face_region.width - crop_width) // 2
                y = face_region.y + (face_region.height - crop_height) // 2
                
                # Ensure within frame bounds
                x = max(0, min(x, width - crop_width))
                y = max(0, min(y, height - crop_height))
                
                return x, y, crop_width, crop_height
            
            # If face detection fails, fall back to center crop
            self.last_face_region = None
            self.stabilization_buffer = []
        
        # Center crop calculation
        if width / height > target_ratio:
            # Image is wider than target ratio
            new_width = int(height * target_ratio)
            new_width = (new_width // 2) * 2  # Ensure even
            x = (width - new_width) // 2
            return x, 0, new_width, height
        else:
            # Image is taller than target ratio
            new_height = int(width / target_ratio)
            new_height = (new_height // 2) * 2  # Ensure even
            y = (height - new_height) // 2
            return 0, y, width, new_height
    
    def apply(self, frame: np.ndarray) -> np.ndarray:
        """Apply crop effect to frame"""
        try:
            x, y, crop_width, crop_height = self._get_crop_dimensions(frame)
            
            # Ensure dimensions are valid
            if crop_width <= 0 or crop_height <= 0:
                return frame
            
            # Ensure we don't exceed frame boundaries
            x = max(0, min(x, frame.shape[1] - crop_width))
            y = max(0, min(y, frame.shape[0] - crop_height))
            
            # Apply crop
            cropped = frame[y:y+crop_height, x:x+crop_width]
            
            # Ensure output dimensions are correct
            if cropped.shape[:2] != (crop_height, crop_width):
                cropped = cv2.resize(cropped, (crop_width, crop_height))
            
            return cropped
            
        except Exception as e:
            print(f"Crop error: {str(e)}")
            return frame
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'face_detection') and self.face_detection:
            self.face_detection.close()
            self.last_face_region = None
            self.stabilization_buffer = []
