"""Optimized coordinate processing and gesture detection."""

import numpy as np

class CoordinateProcessor:
    """Fast coordinate processing with smoothing and dead zone."""
    
    def __init__(self, screen_width: int, screen_height: int, smoothing: float = 0.3):
        """Initialize processor.
        
        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            smoothing: EMA smoothing factor (0.1-0.5)
        """
        self.screen_w = screen_width
        self.screen_h = screen_height
        self.smoothing = smoothing
        self.smoothing_comp = 1.0 - smoothing
        
        # State
        self.ema_x = self.ema_y = None
        self.last_raw_x = self.last_raw_y = None
        self.dead_zone = 0.002
    
    def process(self, x: float, y: float, sensitivity: float = 2.0) -> tuple:
        """Convert normalized coordinates to screen coordinates with smoothing.
        
        Args:
            x: Normalized x coordinate (0-1)
            y: Normalized y coordinate (0-1)
            sensitivity: Movement sensitivity multiplier
            
        Returns:
            Tuple of (final_x, final_y) screen coordinates
        """
        # Dead zone
        if self.last_raw_x is not None:
            if abs(x - self.last_raw_x) < self.dead_zone and \
               abs(y - self.last_raw_y) < self.dead_zone:
                x, y = self.last_raw_x, self.last_raw_y
        
        self.last_raw_x, self.last_raw_y = x, y
        
        # Screen coordinates
        screen_x = x * self.screen_w * sensitivity
        screen_y = y * self.screen_h * sensitivity
        
        # EMA smoothing
        if self.ema_x is None:
            self.ema_x, self.ema_y = screen_x, screen_y
        else:
            self.ema_x = self.smoothing * screen_x + self.smoothing_comp * self.ema_x
            self.ema_y = self.smoothing * screen_y + self.smoothing_comp * self.ema_y
        
        return (int(np.clip(self.ema_x, 0, self.screen_w - 1)),
                int(np.clip(self.ema_y, 0, self.screen_h - 1)))
    
    def reset(self):
        """Reset all state."""
        self.ema_x = self.ema_y = None
        self.last_raw_x = self.last_raw_y = None


class PinchDetector:
    """Pinch gesture detection with hysteresis."""
    
    def __init__(self, click_threshold: float = 0.05, release_threshold: float = 0.07):
        """Initialize detector.
        
        Args:
            click_threshold: Distance threshold to trigger click
            release_threshold: Distance threshold to release click
        """
        self.click_threshold = click_threshold
        self.release_threshold = release_threshold
        self.is_pinching = False
        self.cooldown_frames = 0
        self.cooldown_duration = 8
    
    def update(self, distance: float) -> tuple:
        """Update pinch state based on distance.
        
        Args:
            distance: Current distance between thumb and index finger
            
        Returns:
            Tuple of (is_pinching, just_clicked) state flags
        """
        just_clicked = False
        
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1
        
        # Hysteresis
        if not self.is_pinching:
            if distance < self.click_threshold and self.cooldown_frames == 0:
                self.is_pinching = True
                just_clicked = True
                self.cooldown_frames = self.cooldown_duration
        elif distance > self.release_threshold:
            self.is_pinching = False
        
        return self.is_pinching, just_clicked
    
    def reset(self):
        """Reset pinch state."""
        self.is_pinching = False
        self.cooldown_frames = 0