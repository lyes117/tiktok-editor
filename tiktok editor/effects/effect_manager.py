from typing import Dict, List, Type, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
import os
from pathlib import Path

from effects.visual import (
    Crop, LightBar, ColorFilter, Blur, Mirror, Vignette
)
from effects.audio import (
    PitchShift, Reverb, Echo, BassBoost, Normalize, Compression
)

class EffectCategory(Enum):
    VIDEO = "video"
    AUDIO = "audio"

@dataclass
class EffectParameter:
    name: str
    type: str
    default: Any
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    choices: Optional[List[Any]] = None
    label: Optional[str] = None

@dataclass
class EffectInfo:
    name: str
    category: EffectCategory
    class_ref: Type
    description: str
    parameters: List[EffectParameter]
    icon: Optional[str] = None

class EffectManager:
    def __init__(self):
        self.effects: Dict[str, EffectInfo] = {}
        self.presets: Dict[str, Dict] = {}
        self._register_default_effects()
        self._load_presets()
    
    def _register_default_effects(self):
        """Register all default effects with their parameters"""
        # Video Effects
        self.register_effect(
            name="Crop",
            category=EffectCategory.VIDEO,
            class_ref=Crop,
            description="Recadrer la vidéo avec différents ratios",
            parameters=[
                EffectParameter(
                    name="ratio",
                    type="choice",
                    default="16:9",
                    choices=["16:9", "9:16", "4:3", "1:1", "21:9"],
                    label="Ratio"
                ),
                EffectParameter(
                    name="track_face",
                    type="bool",
                    default=False,
                    label="Suivre le visage"
                )
            ],
            icon="crop.png"
        )
        
        self.register_effect(
            name="Blur",
            category=EffectCategory.VIDEO,
            class_ref=Blur,
            description="Ajouter un effet de flou",
            parameters=[
                EffectParameter(
                    name="intensity",
                    type="float",
                    default=0.5,
                    min_value=0.0,
                    max_value=1.0,
                    label="Intensité"
                )
            ],
            icon="blur.png"
        )
        
        # Add other video effects...
        
        # Audio Effects
        self.register_effect(
            name="Echo",
            category=EffectCategory.AUDIO,
            class_ref=Echo,
            description="Ajouter un effet d'écho",
            parameters=[
                EffectParameter(
                    name="delay",
                    type="float",
                    default=0.3,
                    min_value=0.1,
                    max_value=1.0,
                    label="Délai"
                ),
                EffectParameter(
                    name="feedback",
                    type="float",
                    default=0.5,
                    min_value=0.0,
                    max_value=0.9,
                    label="Retour"
                )
            ],
            icon="echo.png"
        )
        
        # Add other audio effects...
    
    def register_effect(self, name: str, category: EffectCategory, 
                       class_ref: Type, description: str, 
                       parameters: List[EffectParameter], icon: Optional[str] = None):
        """Register a new effect"""
        self.effects[name] = EffectInfo(
            name=name,
            category=category,
            class_ref=class_ref,
            description=description,
            parameters=parameters,
            icon=icon
        )
    
    def get_effect(self, name: str) -> Optional[EffectInfo]:
        """Get effect information by name"""
        return self.effects.get(name)
    
    def get_effects_by_category(self, category: EffectCategory) -> List[EffectInfo]:
        """Get all effects in a category"""
        return [
            effect for effect in self.effects.values()
            if effect.category == category
        ]
    
    def create_effect_instance(self, name: str, **params) -> Any:
        """Create a new instance of an effect with parameters"""
        effect_info = self.get_effect(name)
        if effect_info:
            # Validate parameters
            valid_params = {}
            for param in effect_info.parameters:
                if param.name in params:
                    value = params[param.name]
                    # Type checking
                    if param.type == "float":
                        value = float(value)
                        if param.min_value is not None:
                            value = max(param.min_value, value)
                        if param.max_value is not None:
                            value = min(param.max_value, value)
                    elif param.type == "int":
                        value = int(value)
                    elif param.type == "bool":
                        value = bool(value)
                    elif param.type == "choice" and param.choices:
                        if value not in param.choices:
                            value = param.default
                    valid_params[param.name] = value
                else:
                    valid_params[param.name] = param.default
            
            return effect_info.class_ref(**valid_params)
        return None
    
    def save_preset(self, name: str, effects: List[Dict]):
        """Save an effect preset"""
        self.presets[name] = effects
        self._save_presets()
    
    def get_preset(self, name: str) -> Optional[List[Dict]]:
        """Get an effect preset"""
        return self.presets.get(name)
    
    def get_all_presets(self) -> Dict[str, List[Dict]]:
        """Get all available presets"""
        return self.presets
    
    def _load_presets(self):
        """Load presets from file"""
        preset_file = Path("presets.json")
        if preset_file.exists():
            try:
                with open(preset_file, 'r') as f:
                    self.presets = json.load(f)
            except Exception as e:
                print(f"Error loading presets: {e}")
                self.presets = {}
    
    def _save_presets(self):
        """Save presets to file"""
        preset_file = Path("presets.json")
        try:
            with open(preset_file, 'w') as f:
                json.dump(self.presets, f)
        except Exception as e:
            print(f"Error saving presets: {e}")

class EffectChain:
    def __init__(self, effect_manager: EffectManager):
        self.effect_manager = effect_manager
        self.video_effects: List[Any] = []
        self.audio_effects: List[Any] = []
    
    def add_effect(self, effect_name: str, params: Dict[str, Any] = None):
        """Add an effect to the chain"""
        if params is None:
            params = {}
        
        effect_info = self.effect_manager.get_effect(effect_name)
        if effect_info:
            effect = self.effect_manager.create_effect_instance(effect_name, **params)
            if effect_info.category == EffectCategory.VIDEO:
                self.video_effects.append(effect)
            else:
                self.audio_effects.append(effect)
    
    def remove_effect(self, index: int, category: EffectCategory):
        """Remove an effect from the chain"""
        if category == EffectCategory.VIDEO:
            if 0 <= index < len(self.video_effects):
                self.video_effects.pop(index)
        else:
            if 0 <= index < len(self.audio_effects):
                self.audio_effects.pop(index)
    
    def move_effect(self, old_index: int, new_index: int, category: EffectCategory):
        """Move an effect to a new position in the chain"""
        effects = (self.video_effects if category == EffectCategory.VIDEO 
                  else self.audio_effects)
        if 0 <= old_index < len(effects) and 0 <= new_index < len(effects):
            effect = effects.pop(old_index)
            effects.insert(new_index, effect)
    
    def get_video_effects(self) -> List[Any]:
        """Get all video effects in the chain"""
        return self.video_effects
    
    def get_audio_effects(self) -> List[Any]:
        """Get all audio effects in the chain"""
        return self.audio_effects
    
    def clear(self):
        """Clear all effects"""
        self.video_effects.clear()
        self.audio_effects.clear()
    
    def save_as_preset(self, name: str):
        """Save current chain as a preset"""
        preset_data = {
            'video': [
                {
                    'name': effect.__class__.__name__,
                    'params': effect.__dict__
                }
                for effect in self.video_effects
            ],
            'audio': [
                {
                    'name': effect.__class__.__name__,
                    'params': effect.__dict__
                }
                for effect in self.audio_effects
            ]
        }
        self.effect_manager.save_preset(name, preset_data)
    
    def load_preset(self, name: str):
        """Load a preset into the chain"""
        preset = self.effect_manager.get_preset(name)
        if preset:
            self.clear()
            for effect_data in preset['video']:
                self.add_effect(effect_data['name'], effect_data['params'])
            for effect_data in preset['audio']:
                self.add_effect(effect_data['name'], effect_data['params'])
