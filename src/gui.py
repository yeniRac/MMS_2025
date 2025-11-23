"""Minimal GUI for status display."""

import cv2
import numpy as np
import time
from config.settings import Config

class StatusGUI:
    def __init__(self, config: Config):
        self.config = config
        self.window_name = "Hand Gesture Mouse Control"
        
        # Colors (BGR)
        self.bg = (45, 45, 45)
        self.text = (255, 255, 255)
        self.accent = (100, 200, 100)
        self.disabled = (100, 100, 100)
        self.click_color = (255, 150, 50)
        
        # FPS tracking
        self.fps = 0.0
        self.frame_count = 0
        self.last_time = time.time()
    
    def create_window(self):
        """Create GUI window."""
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.config.GUI_WIDTH, self.config.GUI_HEIGHT)
    
    def update_fps(self):
        """Update FPS counter."""
        self.frame_count += 1
        current = time.time()
        if current - self.last_time >= 1.0:
            self.fps = self.frame_count / (current - self.last_time)
            self.frame_count = 0
            self.last_time = current
    
    def draw_status(self, enabled: bool, hand_detected: bool, 
                   sensitivity: float, smoothing: float,
                   pinch_distance: float = 0.0, is_clicking: bool = False,
                   toggle_progress: float = 0.0) -> np.ndarray:
        """Draw status display."""
        canvas = np.full((self.config.GUI_HEIGHT, self.config.GUI_WIDTH, 3), 
                        self.bg, dtype=np.uint8)
        
        y = 40
        
        # Title
        self._text(canvas, "HAND GESTURE MOUSE", 20, y, self.accent, 0.7, 2)
        y += 60
        
        # Status panels
        status_color = self.accent if enabled else self.disabled
        status_text = "ENABLED" if enabled else "DISABLED"
        self._panel(canvas, "Mouse Control", status_text, 20, y, status_color)
        y += 60
        
        hand_color = self.accent if hand_detected else self.disabled
        hand_text = "DETECTED" if hand_detected else "NOT DETECTED"
        self._panel(canvas, "Hand", hand_text, 20, y, hand_color)
        y += 60
        
        # Pinch detection (always show)
        click_color = self.click_color if is_clicking else self.text
        click_indicator = " [CLICKING!]" if is_clicking else ""
        pinch_text = f"{pinch_distance:.3f}{click_indicator}" if hand_detected else "---"
        self._panel(canvas, "Pinch Distance", pinch_text, 20, y, click_color)
        y += 60
        
        # Toggle progress bar (always show)
        self._draw_progress_bar(canvas, "Toggle Progress", toggle_progress, 20, y)
        y += 60
        
        # Settings
        self._panel(canvas, "Sensitivity", f"{sensitivity:.1f}", 20, y, self.text)
        y += 50
        self._panel(canvas, "Smoothing", f"{smoothing:.2f}", 20, y, self.text)
        y += 50
        self._panel(canvas, "FPS", f"{self.fps:.0f}", 20, y, self.text)
        
        # Controls
        controls = "M=Toggle | Q=Quit | Hold Tight Pinch 5s=Toggle"
        self._text(canvas, controls, 10, self.config.GUI_HEIGHT - 15, 
                  self.disabled, 0.35)
        
        return canvas
    
    def _text(self, canvas, text, x, y, color, scale=0.5, thick=1):
        """Draw text."""
        cv2.putText(canvas, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                   scale, color, thick, cv2.LINE_AA)
    
    def _panel(self, canvas, label, value, x, y, value_color):
        """Draw label-value panel."""
        self._text(canvas, f"{label}:", x, y, self.text, 0.5, 1)
        self._text(canvas, value, x + 200, y, value_color, 0.6, 2)
    
    def _draw_progress_bar(self, canvas, label, progress, x, y):
        """Draw a progress bar."""
        self._text(canvas, f"{label}:", x, y, self.text, 0.5, 1)
        
        bar_x = x + 200
        bar_y = y - 15
        bar_width = 150
        bar_height = 20
        
        # Background
        cv2.rectangle(canvas, (bar_x, bar_y),
                     (bar_x + bar_width, bar_y + bar_height),
                     (60, 60, 60), -1)
        
        # Progress
        filled_width = int(bar_width * progress)
        cv2.rectangle(canvas, (bar_x, bar_y),
                     (bar_x + filled_width, bar_y + bar_height),
                     self.accent, -1)
        
        # Border
        cv2.rectangle(canvas, (bar_x, bar_y),
                     (bar_x + bar_width, bar_y + bar_height),
                     self.text, 1)
        
        # Percentage
        percentage = f"{int(progress * 100)}%"
        self._text(canvas, percentage, bar_x + bar_width + 10, y,
                  self.accent, 0.5, 1)