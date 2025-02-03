class BaseVisualEffect:
    def __init__(self, intensity=0.5):
        self.intensity = intensity
    
    def set_intensity(self, intensity):
        self.intensity = intensity
    
    def apply(self, frame):
        return frame
