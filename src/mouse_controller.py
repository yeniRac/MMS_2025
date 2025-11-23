"""Mouse control with gesture detection."""

import pyautogui
import numpy as np
import time
from typing import Optional
from config.settings import Config

class MouseController:
    def __init__(self, config: Config):
        self.config = config
        self.enabled = False
        self.screen_w, self.screen_h = pyautogui.size()
        
        # Smoothing state
        self._ema_x: Optional[float] = None
        self._ema_y: Optional[float] = None
        
        # Click state
        self._is_clicking = False
        self._click_cooldown = 0
        
        # Toggle state (hold pinch for 5 seconds)
        self._toggle_start_time: Optional[float] = None
        self._toggle_in_progress = False
        self.toggle_progress = 0.0
        self._toggle_completed = False  # Flag to prevent multiple toggles
        
        # PyAutoGUI settings
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0
    
    def check_toggle_gesture(self, pinch_distance: float) -> bool:
        """Check for toggle gesture (hold tight pinch for 5 seconds).
        
        Returns:
            True if toggle should occur
        """
        # Very tight pinch for toggle (tighter than click)
        if pinch_distance < self.config.TOGGLE_THRESHOLD:
            if self._toggle_start_time is None:
                self._toggle_start_time = time.time()
                self._toggle_in_progress = True
                self._toggle_completed = False
            
            elapsed = time.time() - self._toggle_start_time
            self.toggle_progress = min(1.0, elapsed / self.config.TOGGLE_DURATION)
            
            # Toggle completed
            if elapsed >= self.config.TOGGLE_DURATION and not self._toggle_completed:
                self._toggle_completed = True
                return True
        else:
            # Reset if pinch released
            if self._toggle_in_progress:
                self._toggle_start_time = None
                self._toggle_in_progress = False
                self._toggle_completed = False
                self.toggle_progress = 0.0
        
        return False
    
    def toggle(self):
        """Toggle mouse control."""
        self.enabled = not self.enabled
        self._ema_x = self._ema_y = None
        # Reset toggle state after toggle
        self._toggle_start_time = None
        self._toggle_in_progress = False
        self._toggle_completed = False
        self.toggle_progress = 0.0
    
    def move_cursor(self, hand_landmarks):
        """Move cursor based on thumb position."""
        if not self.enabled:
            return
        
        # Don't move during toggle gesture
        if self._toggle_in_progress:
            return
        
        thumb = hand_landmarks.landmark[4]
        x = np.clip(thumb.x, self.config.DEADZONE_X, 1.0 - self.config.DEADZONE_X)
        y = np.clip(thumb.y, self.config.DEADZONE_Y, 1.0 - self.config.DEADZONE_Y)
        
        # Normalize to deadzone
        x_range = 1.0 - 2 * self.config.DEADZONE_X
        y_range = 1.0 - 2 * self.config.DEADZONE_Y
        x = (x - self.config.DEADZONE_X) / x_range
        y = (y - self.config.DEADZONE_Y) / y_range
        
        # Screen coordinates
        screen_x = x * self.screen_w
        screen_y = y * self.screen_h
        
        # Exponential smoothing
        alpha = self.config.SMOOTHING / self.config.DEFAULT_SENSITIVITY
        if self._ema_x is None:
            self._ema_x, self._ema_y = screen_x, screen_y
        else:
            self._ema_x = alpha * screen_x + (1 - alpha) * self._ema_x
            self._ema_y = alpha * screen_y + (1 - alpha) * self._ema_y
        
        # Move cursor
        final_x = int(np.clip(self._ema_x, 0, self.screen_w - 1))
        final_y = int(np.clip(self._ema_y, 0, self.screen_h - 1))
        
        try:
            pyautogui.moveTo(final_x, final_y, duration=0, _pause=False)
        except:
            pass
    
    def handle_click(self, pinch_distance: float):
        """Handle click with hysteresis."""
        if not self.enabled:
            return
        
        # Don't click during toggle gesture
        if self._toggle_in_progress:
            return
        
        if self._click_cooldown > 0:
            self._click_cooldown -= 1
            return
        
        # Click threshold should be higher than toggle threshold
        if not self._is_clicking and pinch_distance < self.config.CLICK_THRESHOLD:
            self._is_clicking = True
            self._click_cooldown = self.config.CLICK_COOLDOWN
            try:
                pyautogui.click()
            except:
                pass
        elif self._is_clicking and pinch_distance > self.config.CLICK_THRESHOLD * 1.5:
            self._is_clicking = False