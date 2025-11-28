"""Mouse control with relative movement (like a real mouse)."""

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
        
        # Relative movement tracking
        self._last_x: Optional[float] = None
        self._last_y: Optional[float] = None
        self._center_x = 0.5  # Center reference point
        self._center_y = 0.5
        
        # Smoothing for delta values
        self._smoothed_dx = 0.0
        self._smoothed_dy = 0.0
        
        # Enhanced click state
        self._is_clicking = False
        self._last_distance = None
        self._distance_velocity = 0.0
        
        # Toggle state
        self._toggle_start_time: Optional[float] = None
        self._toggle_in_progress = False
        self.toggle_progress = 0.0
        self._toggle_completed = False
        
        # PyAutoGUI settings
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0
    
    def check_toggle_gesture(self, pinch_distance: float) -> bool:
        """Check for toggle gesture (spread fingers wide for 2 seconds)."""
        if pinch_distance > self.config.TOGGLE_THRESHOLD:
            if self._toggle_start_time is None:
                self._toggle_start_time = time.time()
                self._toggle_in_progress = True
                self._toggle_completed = False
            
            elapsed = time.time() - self._toggle_start_time
            self.toggle_progress = min(1.0, elapsed / self.config.TOGGLE_DURATION)
            
            if elapsed >= self.config.TOGGLE_DURATION and not self._toggle_completed:
                self._toggle_completed = True
                return True
        else:
            if self._toggle_in_progress:
                self._toggle_start_time = None
                self._toggle_in_progress = False
                self._toggle_completed = False
                self.toggle_progress = 0.0
        
        return False
    
    def toggle(self):
        """Toggle mouse control."""
        # Release mouse button if held when toggling off
        if self.enabled and self._is_clicking:
            try:
                pyautogui.mouseUp()
            except:
                pass
        
        self.enabled = not self.enabled
        # Reset tracking state
        self._last_x = None
        self._last_y = None
        self._smoothed_dx = 0.0
        self._smoothed_dy = 0.0
        self._is_clicking = False
        self._last_distance = None
        self._distance_velocity = 0.0
        self._toggle_start_time = None
        self._toggle_in_progress = False
        self._toggle_completed = False
        self.toggle_progress = 0.0
    
    def move_cursor(self, hand_landmarks):
        """Move cursor using RELATIVE movement (like a real mouse) - INDEX FINGER."""
        if not self.enabled or self._toggle_in_progress:
            return
        
        # Get INDEX FINGER TIP position (landmark 8) instead of thumb
        index_tip = hand_landmarks.landmark[8]
        current_x = index_tip.x
        current_y = index_tip.y
        
        # Apply deadzone around center
        dx_raw = current_x - self._center_x
        dy_raw = current_y - self._center_y
        
        # Deadzone filter
        if abs(dx_raw) < self.config.DEADZONE_X:
            dx_raw = 0
        if abs(dy_raw) < self.config.DEADZONE_Y:
            dy_raw = 0
        
        # If first frame, initialize and don't move
        if self._last_x is None:
            self._last_x = current_x
            self._last_y = current_y
            return
        
        # Calculate delta (change since last frame)
        dx = current_x - self._last_x
        dy = current_y - self._last_y
        
        # Update last position
        self._last_x = current_x
        self._last_y = current_y
        
        # Apply smoothing to deltas
        alpha = self.config.SMOOTHING
        self._smoothed_dx = alpha * dx + (1 - alpha) * self._smoothed_dx
        self._smoothed_dy = alpha * dy + (1 - alpha) * self._smoothed_dy
        
        # Scale by sensitivity and screen size
        move_x = self._smoothed_dx * self.screen_w * self.config.DEFAULT_SENSITIVITY
        move_y = self._smoothed_dy * self.screen_h * self.config.DEFAULT_SENSITIVITY
        
        # Apply movement (relative to current position)
        try:
            pyautogui.moveRel(int(move_x), int(move_y), duration=0, _pause=False)
        except:
            pass
    
    def handle_click(self, pinch_distance: float):
        """Handle click and hold with stable detection."""
        if not self.enabled or self._toggle_in_progress:
            # If disabled, make sure mouse is released
            if self._is_clicking:
                try:
                    pyautogui.mouseUp()
                except:
                    pass
                self._is_clicking = False
            return
        
        # Calculate velocity (rate of change)
        if self._last_distance is not None:
            self._distance_velocity = pinch_distance - self._last_distance
        self._last_distance = pinch_distance
        
        # Use clear thresholds with hysteresis
        press_threshold = self.config.CLICK_THRESHOLD
        release_threshold = self.config.CLICK_THRESHOLD * 1.5  # More forgiving release
        
        if not self._is_clicking:
            # Press down - use velocity for snappiness
            approaching_fast = self._distance_velocity < -0.01
            at_threshold = pinch_distance < press_threshold
            
            if at_threshold or (approaching_fast and pinch_distance < press_threshold * 1.2):
                try:
                    pyautogui.mouseDown()  # Press and HOLD
                    self._is_clicking = True
                except Exception as e:
                    print(f"Error on mouseDown: {e}")
        else:
            # Release - only when fingers clearly separate
            if pinch_distance > release_threshold:
                try:
                    pyautogui.mouseUp()  # Release
                    self._is_clicking = False
                except Exception as e:
                    print(f"Error on mouseUp: {e}")