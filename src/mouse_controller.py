"""Mouse control with gesture detection."""

import pyautogui
import numpy as np
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
        
        # PyAutoGUI settings
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0
    
    def toggle(self):
        """Toggle mouse control."""
        self.enabled = not self.enabled
        self._ema_x = self._ema_y = None
    
    def move_cursor(self, hand_landmarks):
        """Move cursor based on thumb position."""
        if not self.enabled:
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
        
        if self._click_cooldown > 0:
            self._click_cooldown -= 1
            return
        
        if not self._is_clicking and pinch_distance < self.config.CLICK_THRESHOLD:
            self._is_clicking = True
            self._click_cooldown = self.config.CLICK_COOLDOWN
            try:
                pyautogui.click()
            except:
                pass
        elif self._is_clicking and pinch_distance > self.config.CLICK_THRESHOLD * 1.5:
            self._is_clicking = False