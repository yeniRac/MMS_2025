"""Optimized coordinate processing for hand-to-screen mapping."""

import numpy as np


class CoordinateProcessor:
    """Fast coordinate processing with smoothing and dead zone."""
    
    def __init__(self, screen_width, screen_height, smoothing_factor=0.3):
        """Initialize processor with screen dimensions and smoothing."""
        self.screen_w = screen_width
        self.screen_h = screen_height
        self.smoothing = smoothing_factor
        
        self.ema_x = None
        self.ema_y = None
        
        self.dead_zone = 0.002
        self.last_raw_x = None
        self.last_raw_y = None
        
        self.smoothing_comp = 1.0 - smoothing_factor
        
        print(f"Coordinate processor: {screen_width}x{screen_height}")
        print(f"Smoothing: {smoothing_factor}, Dead zone: {self.dead_zone}")
    
    def process(self, x, y, sensitivity=2.0):
        """Convert normalized coordinates to screen coordinates with smoothing."""
        if self.last_raw_x is not None:
            dx = abs(x - self.last_raw_x)
            dy = abs(y - self.last_raw_y)
            
            if dx < self.dead_zone and dy < self.dead_zone:
                x = self.last_raw_x
                y = self.last_raw_y
        
        self.last_raw_x = x
        self.last_raw_y = y
        
        screen_x = x * self.screen_w * sensitivity
        screen_y = y * self.screen_h * sensitivity
        
        if self.ema_x is None:
            self.ema_x = screen_x
            self.ema_y = screen_y
        else:
            self.ema_x = self.smoothing * screen_x + self.smoothing_comp * self.ema_x
            self.ema_y = self.smoothing * screen_y + self.smoothing_comp * self.ema_y
        
        final_x = int(max(0, min(self.ema_x, self.screen_w - 1)))
        final_y = int(max(0, min(self.ema_y, self.screen_h - 1)))
        
        return final_x, final_y
    
    def reset(self):
        """Reset smoothing state."""
        self.ema_x = None
        self.ema_y = None
        self.last_raw_x = None
        self.last_raw_y = None


class PinchDetector:
    """Pinch gesture detection with hysteresis."""
    
    def __init__(self, click_threshold=0.05, release_threshold=0.07):
        """Initialize detector with click/release thresholds."""
        self.click_threshold = click_threshold
        self.release_threshold = release_threshold
        self.is_pinching = False
        
        self.cooldown_frames = 0
        self.cooldown_duration = 8
    
    def update(self, distance):
        """Update pinch state based on thumb-index distance."""
        just_clicked = False
        
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1
        
        if not self.is_pinching:
            if distance < self.click_threshold and self.cooldown_frames == 0:
                self.is_pinching = True
                just_clicked = True
                self.cooldown_frames = self.cooldown_duration
        else:
            if distance > self.release_threshold:
                self.is_pinching = False
        
        return self.is_pinching, just_clicked
    
    def reset(self):
        """Reset pinch state."""
        self.is_pinching = False
        self.cooldown_frames = 0