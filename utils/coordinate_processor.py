"""Optimized coordinate processing for hand-to-screen mapping."""

import numpy as np


class CoordinateProcessor:
    """Fast coordinate processing with smoothing and dead zone."""
    
    def __init__(self, screen_width, screen_height, smoothing_factor=0.3):
        """Initialize processor with screen dimensions and smoothing.
        
        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            smoothing_factor: EMA smoothing factor (0.1-0.5)
        """
        self.screen_w = screen_width
        self.screen_h = screen_height
        self.smoothing = smoothing_factor
        self.smoothing_comp = 1.0 - smoothing_factor
        
        # Smoothing state
        self.ema_x = None
        self.ema_y = None
        
        # Dead zone state
        self.dead_zone = 0.002
        self.last_raw_x = None
        self.last_raw_y = None
        
        print(f"Coordinate processor: {screen_width}x{screen_height}")
        print(f"Smoothing: {smoothing_factor}, Dead zone: {self.dead_zone}")
    
    def process(self, x, y, sensitivity=2.0):
        """Convert normalized coordinates to screen coordinates with smoothing.
        
        Args:
            x: Normalized x coordinate (0-1)
            y: Normalized y coordinate (0-1)
            sensitivity: Movement sensitivity multiplier
            
        Returns:
            tuple: (final_x, final_y) screen coordinates
        """
        # Apply dead zone
        if self.last_raw_x is not None:
            dx = abs(x - self.last_raw_x)
            dy = abs(y - self.last_raw_y)
            
            if dx < self.dead_zone and dy < self.dead_zone:
                x = self.last_raw_x
                y = self.last_raw_y
        
        self.last_raw_x = x
        self.last_raw_y = y
        
        # Convert to screen coordinates
        screen_x = x * self.screen_w * sensitivity
        screen_y = y * self.screen_h * sensitivity
        
        # Apply exponential moving average
        if self.ema_x is None:
            self.ema_x = screen_x
            self.ema_y = screen_y
        else:
            self.ema_x = self.smoothing * screen_x + self.smoothing_comp * self.ema_x
            self.ema_y = self.smoothing * screen_y + self.smoothing_comp * self.ema_y
        
        # Clamp to screen bounds
        final_x = int(np.clip(self.ema_x, 0, self.screen_w - 1))
        final_y = int(np.clip(self.ema_y, 0, self.screen_h - 1))
        
        return final_x, final_y
    
    def reset(self):
        """Reset smoothing and dead zone state."""
        self.ema_x = None
        self.ema_y = None
        self.last_raw_x = None
        self.last_raw_y = None


class PinchDetector:
    """Pinch gesture detection with hysteresis."""
    
    def __init__(self, click_threshold=0.05, release_threshold=0.07):
        """Initialize detector with click/release thresholds.
        
        Args:
            click_threshold: Distance threshold to trigger click
            release_threshold: Distance threshold to release click
        """
        self.click_threshold = click_threshold
        self.release_threshold = release_threshold
        self.is_pinching = False
        
        self.cooldown_frames = 0
        self.cooldown_duration = 8
    
    def update(self, distance):
        """Update pinch state based on thumb-index distance.
        
        Args:
            distance: Current distance between thumb and index finger
            
        Returns:
            tuple: (is_pinching, just_clicked) state flags
        """
        just_clicked = False
        
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1
        
        # Hysteresis logic
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
        """Reset pinch state and cooldown."""
        self.is_pinching = False
        self.cooldown_frames = 0