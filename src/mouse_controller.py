"""Optimized mouse controller with minimal latency.

Handles mouse movement and clicking using exponential moving average
for smooth, responsive control.
"""

import numpy as np
import pyautogui


class MouseController:
    """Ultra-fast mouse control with optimized smoothing."""
    
    def __init__(self, sensitivity=2.0, smoothing_factor=0.3, 
                 deadzone_x=0.15, deadzone_y=0.15):
        """Initialize mouse controller.
        
        Args:
            sensitivity: Movement multiplier (1.0-3.0)
            smoothing_factor: EMA smoothing (0.1-0.5, lower=smoother)
            deadzone_x: Horizontal edge deadzone (0.0-0.3)
            deadzone_y: Vertical edge deadzone (0.0-0.3)
        """
        print("Initializing Mouse Controller...")
        
        self.sensitivity = sensitivity
        self.smoothing_factor = smoothing_factor
        self.enabled = False
        
        # Screen dimensions
        self.screen_w, self.screen_h = pyautogui.size()
        
        # Deadzones for edge stability
        self.deadzone_x = deadzone_x
        self.deadzone_y = deadzone_y
        
        # Exponential moving average for smoothing
        self.ema_x = None
        self.ema_y = None
        
        # Dead zone to ignore tiny movements
        self.dead_zone = 0.002
        self.last_raw_x = None
        self.last_raw_y = None
        
        # Click detection state
        self.is_clicking = False
        self.click_cooldown = 0
        self.click_threshold = 0.05
        self.release_threshold = 0.07
        
        # Disable PyAutoGUI failsafe and pause for performance
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0
        
        print(f"Screen: {self.screen_w}x{self.screen_h}")
        print(f"Sensitivity: {sensitivity}")
        print(f"Smoothing: {smoothing_factor}")
        print(f"Deadzones: X={deadzone_x:.2f}, Y={deadzone_y:.2f}")
        print("Mouse Controller initialized\n")
    
    def _apply_deadzone(self, x, y):
        """Apply deadzone mapping to normalized coordinates.
        
        Args:
            x: Normalized x position (0-1)
            y: Normalized y position (0-1)
            
        Returns:
            tuple: Remapped (x, y) coordinates
        """
        # Map input range to exclude deadzones
        # Input 0.0-1.0 -> Output deadzone_x to (1-deadzone_x)
        x_range = 1.0 - 2 * self.deadzone_x
        y_range = 1.0 - 2 * self.deadzone_y
        
        # Clamp and remap
        x_clamped = np.clip(x, self.deadzone_x, 1.0 - self.deadzone_x)
        y_clamped = np.clip(y, self.deadzone_y, 1.0 - self.deadzone_y)
        
        x_mapped = (x_clamped - self.deadzone_x) / x_range
        y_mapped = (y_clamped - self.deadzone_y) / y_range
        
        return x_mapped, y_mapped
    
    def move_mouse(self, x, y):
        """Move mouse to normalized hand coordinates.
        
        Args:
            x: Normalized x position (0-1)
            y: Normalized y position (0-1)
        """
        if not self.enabled:
            return
        
        # Apply dead zone
        if self.last_raw_x is not None:
            dx = abs(x - self.last_raw_x)
            dy = abs(y - self.last_raw_y)
            
            if dx < self.dead_zone and dy < self.dead_zone:
                return
        
        self.last_raw_x = x
        self.last_raw_y = y
        
        # Apply deadzone mapping
        x_mapped, y_mapped = self._apply_deadzone(x, y)
        
        # Convert to screen coordinates
        screen_x = x_mapped * self.screen_w
        screen_y = y_mapped * self.screen_h
        
        # Apply exponential moving average
        effective_smoothing = self.smoothing_factor / self.sensitivity
        if self.ema_x is None:
            self.ema_x = screen_x
            self.ema_y = screen_y
        else:
            self.ema_x = effective_smoothing * screen_x + (1 - effective_smoothing) * self.ema_x
            self.ema_y = effective_smoothing * screen_y + (1 - effective_smoothing) * self.ema_y
        
        # Clamp to screen bounds
        final_x = int(np.clip(self.ema_x, 0, self.screen_w - 1))
        final_y = int(np.clip(self.ema_y, 0, self.screen_h - 1))
        
        # Move mouse instantly
        try:
            pyautogui.moveTo(final_x, final_y, duration=0, _pause=False)
        except Exception as e:
            print(f"Mouse move error: {e}")
    
    def handle_click(self, pinch_distance):
        """Handle click detection with hysteresis.
        
        Args:
            pinch_distance: Distance between thumb and index finger
            
        Returns:
            bool: True if click just occurred
        """
        if not self.enabled:
            return False
        
        just_clicked = False
        
        if self.click_cooldown > 0:
            self.click_cooldown -= 1
        
        # Hysteresis: different thresholds for press and release
        if not self.is_clicking:
            if pinch_distance < self.click_threshold and self.click_cooldown == 0:
                self.is_clicking = True
                just_clicked = True
                self.click_cooldown = 10
                
                try:
                    pyautogui.click()
                except Exception:
                    pass
        else:
            if pinch_distance > self.release_threshold:
                self.is_clicking = False
        
        return just_clicked
    
    def toggle_enabled(self):
        """Toggle mouse control on/off and reset state."""
        self.enabled = not self.enabled
        
        # Reset state when toggling
        self.ema_x = None
        self.ema_y = None
        self.last_raw_x = None
        self.last_raw_y = None
        self.is_clicking = False
        self.click_cooldown = 0
        
        status = "ENABLED ✓" if self.enabled else "DISABLED"
        separator = "=" * 50
        print(f"\n{separator}")
        print(f"Mouse control: {status}")
        if self.enabled:
            print("Move your thumb to control the cursor!")
        print(f"{separator}\n")
        
        return self.enabled