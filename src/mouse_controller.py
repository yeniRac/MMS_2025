"""Mouse control with relative movement (like a real mouse) - OPTIMIZED."""

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

        # Pre-calculated constants for performance
        self._release_multiplier = 1.5
        self._velocity_threshold = -0.01
        self._press_multiplier = 1.2

        # PyAutoGUI settings - optimized
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
            pyautogui.mouseUp()

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

    def _get_stable_position(self, hand_landmarks) -> tuple[float, float]:
        """
        Get position from stable landmarks that DON'T move during pinch gestures.
        Excludes thumb (1-4) and index finger (5-8) to avoid click-induced jitter.
        Uses middle, ring, pinky fingers + wrist for rock-solid tracking.
        """
        landmarks = self.config.STABLE_LANDMARKS
        weights = self.config.STABLE_WEIGHTS

        x_sum = 0.0
        y_sum = 0.0
        weight_sum = 0.0

        for idx, weight in zip(landmarks, weights):
            landmark = hand_landmarks.landmark[idx]
            x_sum += landmark.x * weight
            y_sum += landmark.y * weight
            weight_sum += weight

        return x_sum / weight_sum, y_sum / weight_sum

    def move_cursor(self, hand_landmarks):
        """Move cursor using RELATIVE movement with stable (non-pinching) landmarks."""
        if not self.enabled or self._toggle_in_progress:
            return

        # Get position from landmarks that don't move during pinch
        current_x, current_y = self._get_stable_position(hand_landmarks)

        # If first frame, initialize and don't move
        if self._last_x is None:
            self._last_x = current_x
            self._last_y = current_y
            return

        # Calculate delta (change since last frame)
        dx = current_x - self._last_x
        dy = current_y - self._last_y

        # Apply deadzone to deltas
        if abs(dx) < self.config.DEADZONE_X:
            dx = 0
        if abs(dy) < self.config.DEADZONE_Y:
            dy = 0

        # Update last position
        self._last_x = current_x
        self._last_y = current_y

        # Apply smoothing to deltas (inverted so higher = more smoothing)
        alpha = 1.0 - self.config.SMOOTHING
        self._smoothed_dx = alpha * dx + (1 - alpha) * self._smoothed_dx
        self._smoothed_dy = alpha * dy + (1 - alpha) * self._smoothed_dy

        # Scale by sensitivity and screen size
        move_x = self._smoothed_dx * self.screen_w * self.config.DEFAULT_SENSITIVITY
        move_y = self._smoothed_dy * self.screen_h * self.config.DEFAULT_SENSITIVITY

        # Apply movement (relative to current position)
        pyautogui.moveRel(int(move_x), int(move_y), duration=0, _pause=False)

    def handle_click(self, pinch_distance: float):
        """Handle click and hold with stable detection."""
        if not self.enabled or self._toggle_in_progress:
            # If disabled, make sure mouse is released
            if self._is_clicking:
                pyautogui.mouseUp()
                self._is_clicking = False
            return

        # Calculate velocity (rate of change)
        if self._last_distance is not None:
            self._distance_velocity = pinch_distance - self._last_distance
        self._last_distance = pinch_distance

        # Use pre-calculated thresholds
        press_threshold = self.config.CLICK_THRESHOLD
        release_threshold = self.config.CLICK_THRESHOLD * self._release_multiplier

        if not self._is_clicking:
            # Press down - use velocity for snappiness
            approaching_fast = self._distance_velocity < self._velocity_threshold
            at_threshold = pinch_distance < press_threshold

            if at_threshold or (approaching_fast and pinch_distance < press_threshold * self._press_multiplier):
                pyautogui.mouseDown()  # Press and HOLD
                self._is_clicking = True
        else:
            # Release - only when fingers clearly separate
            if pinch_distance > release_threshold:
                pyautogui.mouseUp()  # Release
                self._is_clicking = False