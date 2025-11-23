"""GUI with interactive sliders for settings."""

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
        self.slider_bg = (60, 60, 60)
        self.slider_active = (80, 160, 255)
        
        # FPS tracking
        self.fps = 0.0
        self.frame_count = 0
        self.last_time = time.time()
        
        # Slider state
        self.sliders = {
            'sensitivity': {
                'y': 0, 'value': config.DEFAULT_SENSITIVITY,
                'min': 0.5, 'max': 5.0, 'label': 'Sensitivity'
            },
            'smoothing': {
                'y': 0, 'value': config.SMOOTHING,
                'min': 0.1, 'max': 0.8, 'label': 'Smoothing'
            },
            'deadzone': {
                'y': 0, 'value': config.DEADZONE_X,
                'min': 0.0, 'max': 0.3, 'label': 'Deadzone'
            },
            'click_threshold': {
                'y': 0, 'value': config.CLICK_THRESHOLD,
                'min': 0.02, 'max': 0.15, 'label': 'Click Threshold'
            }
        }
        
        self.dragging_slider = None
        cv2.setMouseCallback(self.window_name, self._mouse_callback)
    
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
    
    def _mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for sliders."""
        if event == cv2.EVENT_LBUTTONDOWN:
            # Check if clicking on a slider
            for name, slider in self.sliders.items():
                slider_y = slider['y']
                if slider_y > 0 and abs(y - slider_y) < 15:
                    self.dragging_slider = name
                    self._update_slider_value(name, x)
        
        elif event == cv2.EVENT_MOUSEMOVE and self.dragging_slider:
            self._update_slider_value(self.dragging_slider, x)
        
        elif event == cv2.EVENT_LBUTTONUP:
            self.dragging_slider = None
    
    def handle_window_events(self) -> int:
        """Handle window events without blocking. Returns key code or -1."""
        # Use waitKey(1) to process window events but don't require focus
        return cv2.waitKey(1) & 0xFF
    
    def _update_slider_value(self, slider_name: str, x: int):
        """Update slider value based on mouse position."""
        slider = self.sliders[slider_name]
        slider_x = 150
        slider_width = 300
        
        # Calculate value from position
        pos = max(0, min(slider_width, x - slider_x))
        normalized = pos / slider_width
        value = slider['min'] + normalized * (slider['max'] - slider['min'])
        
        slider['value'] = value
        
        # Update config
        if slider_name == 'sensitivity':
            self.config.DEFAULT_SENSITIVITY = value
        elif slider_name == 'smoothing':
            self.config.SMOOTHING = value
        elif slider_name == 'deadzone':
            self.config.DEADZONE_X = value
            self.config.DEADZONE_Y = value
        elif slider_name == 'click_threshold':
            self.config.CLICK_THRESHOLD = value
    
    def draw_status(self, enabled: bool, hand_detected: bool, 
                   pinch_distance: float = 0.0, is_clicking: bool = False,
                   toggle_progress: float = 0.0) -> np.ndarray:
        """Draw status display with interactive controls."""
        canvas = np.full((self.config.GUI_HEIGHT, self.config.GUI_WIDTH, 3), 
                        self.bg, dtype=np.uint8)
        
        y = 50
        
        # Title
        self._text(canvas, "HAND GESTURE MOUSE CONTROL", 
                  self.config.GUI_WIDTH // 2 - 220, y, self.accent, 0.9, 3)
        y += 70
        
        # Divider
        cv2.line(canvas, (30, y), (self.config.GUI_WIDTH - 30, y), 
                self.accent, 2)
        y += 40
        
        # === STATUS SECTION ===
        self._text(canvas, "STATUS", 40, y, self.accent, 0.7, 2)
        y += 45
        
        # Mouse control status with larger indicator
        status_color = self.accent if enabled else self.disabled
        status_text = "ENABLED" if enabled else "DISABLED"
        cv2.circle(canvas, (50, y - 8), 12, status_color, -1)
        cv2.circle(canvas, (50, y - 8), 12, self.text, 2)
        self._text(canvas, "Mouse Control:", 80, y, self.text, 0.6, 1)
        self._text(canvas, status_text, 280, y, status_color, 0.7, 2)
        y += 50
        
        # Hand detection with indicator
        hand_color = self.accent if hand_detected else self.disabled
        hand_text = "DETECTED" if hand_detected else "NOT DETECTED"
        cv2.circle(canvas, (50, y - 8), 12, hand_color, -1)
        cv2.circle(canvas, (50, y - 8), 12, self.text, 2)
        self._text(canvas, "Hand:", 80, y, self.text, 0.6, 1)
        self._text(canvas, hand_text, 280, y, hand_color, 0.7, 2)
        y += 50
        
        # Pinch distance with visual indicator
        click_color = self.click_color if is_clicking else self.text
        click_indicator = "  [CLICKING!]" if is_clicking else ""
        pinch_text = f"{pinch_distance:.3f}" if hand_detected else "---"
        
        if is_clicking:
            cv2.circle(canvas, (50, y - 8), 12, self.click_color, -1)
            cv2.circle(canvas, (50, y - 8), 12, self.text, 2)
        else:
            cv2.circle(canvas, (50, y - 8), 12, (80, 80, 80), -1)
            cv2.circle(canvas, (50, y - 8), 12, self.text, 1)
        
        self._text(canvas, "Pinch Distance:", 80, y, self.text, 0.6, 1)
        self._text(canvas, pinch_text + click_indicator, 280, y, click_color, 0.7, 2)
        y += 50
        
        # FPS
        self._text(canvas, "FPS:", 80, y, self.text, 0.6, 1)
        fps_color = self.accent if self.fps > 50 else (self.disabled if self.fps > 30 else (100, 100, 255))
        self._text(canvas, f"{self.fps:.0f}", 280, y, fps_color, 0.7, 2)
        y += 60
        
        # Toggle progress bar (larger and more prominent)
        self._text(canvas, "Toggle Progress (Hold Tight Pinch 5s)", 40, y, self.text, 0.6, 1)
        y += 35
        self._draw_progress_bar_large(canvas, toggle_progress, 40, y)
        y += 60
        
        # Divider
        cv2.line(canvas, (30, y), (self.config.GUI_WIDTH - 30, y), 
                self.disabled, 1)
        y += 40
        
        # === SETTINGS SECTION ===
        self._text(canvas, "SETTINGS", 40, y, self.accent, 0.7, 2)
        self._text(canvas, "(Click and Drag Sliders)", 
                  self.config.GUI_WIDTH - 280, y, self.disabled, 0.5, 1)
        y += 50
        
        # Interactive sliders with more spacing
        for name, slider in self.sliders.items():
            slider['y'] = y
            self._draw_slider(canvas, slider['label'], slider['value'],
                            slider['min'], slider['max'], 40, y,
                            name == self.dragging_slider)
            y += 65
        
        y += 20
        
        # Divider
        cv2.line(canvas, (30, y), (self.config.GUI_WIDTH - 30, y), 
                self.disabled, 1)
        y += 30
        
        # === CONTROLS SECTION ===
        self._text(canvas, "CONTROLS", 40, y, self.accent, 0.7, 2)
        y += 40
        
        controls = [
            ("M", "Toggle Mouse Control (Keyboard)"),
            ("Pinch", "Hold Very Tight Pinch 5s to Toggle"),
            ("Q", "Quit Application")
        ]
        
        for key, description in controls:
            # Draw key box
            cv2.rectangle(canvas, (50, y - 20), (110, y + 5), 
                         self.slider_bg, -1)
            cv2.rectangle(canvas, (50, y - 20), (110, y + 5), 
                         self.text, 1)
            self._text(canvas, key, 65, y, self.text, 0.5, 1)
            
            # Draw description
            self._text(canvas, description, 130, y, self.text, 0.5, 1)
            y += 35
        
        return canvas
    
    def _text(self, canvas, text, x, y, color, scale=0.5, thick=1):
        """Draw text."""
        cv2.putText(canvas, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                   scale, color, thick, cv2.LINE_AA)
    
    def _panel(self, canvas, label, value, x, y, value_color):
        """Draw label-value panel."""
        self._text(canvas, f"{label}:", x, y, self.text, 0.5, 1)
        self._text(canvas, str(value), x + 220, y, value_color, 0.6, 2)
    
    def _draw_progress_bar(self, canvas, label, progress, x, y):
        """Draw a progress bar."""
        self._text(canvas, f"{label}:", x, y, self.text, 0.5, 1)
        
        bar_x = x + 220
        bar_y = y - 15
        bar_width = 240
        bar_height = 20
        
        # Background
        cv2.rectangle(canvas, (bar_x, bar_y),
                     (bar_x + bar_width, bar_y + bar_height),
                     (60, 60, 60), -1)
        
        # Progress
        filled_width = int(bar_width * progress)
        if filled_width > 0:
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
                  self.accent if progress > 0 else self.text, 0.5, 1)
    
    def _draw_progress_bar_large(self, canvas, progress, x, y):
        """Draw a large progress bar."""
        bar_width = self.config.GUI_WIDTH - 80
        bar_height = 30
        
        # Background
        cv2.rectangle(canvas, (x, y),
                     (x + bar_width, y + bar_height),
                     self.slider_bg, -1)
        
        # Progress with gradient effect
        filled_width = int(bar_width * progress)
        if filled_width > 0:
            # Create color gradient based on progress
            if progress < 0.5:
                # Yellow to green
                color = (0, int(100 + 155 * progress * 2), int(255 - 155 * progress * 2))
            else:
                # Green
                color = self.accent
            
            cv2.rectangle(canvas, (x, y),
                         (x + filled_width, y + bar_height),
                         color, -1)
        
        # Border
        cv2.rectangle(canvas, (x, y),
                     (x + bar_width, y + bar_height),
                     self.text, 2)
        
        # Percentage text (centered)
        percentage = f"{int(progress * 100)}%"
        text_size = cv2.getTextSize(percentage, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        text_x = x + (bar_width - text_size[0]) // 2
        text_y = y + (bar_height + text_size[1]) // 2
        
        # Shadow for better readability
        self._text(canvas, percentage, text_x + 1, text_y + 1, (0, 0, 0), 0.7, 2)
        self._text(canvas, percentage, text_x, text_y, self.text, 0.7, 2)
    
    def _draw_slider(self, canvas, label, value, min_val, max_val, x, y, active=False):
        """Draw interactive slider."""
        self._text(canvas, f"{label}:", x, y, self.text, 0.6, 1)
        
        slider_x = x + 180
        slider_y = y - 10
        slider_width = self.config.GUI_WIDTH - slider_x - 120
        slider_height = 10
        
        # Background track
        cv2.rectangle(canvas, (slider_x, slider_y),
                     (slider_x + slider_width, slider_y + slider_height),
                     self.slider_bg, -1)
        cv2.rectangle(canvas, (slider_x, slider_y),
                     (slider_x + slider_width, slider_y + slider_height),
                     (80, 80, 80), 1)
        
        # Filled portion
        normalized = (value - min_val) / (max_val - min_val)
        filled_width = int(slider_width * normalized)
        color = self.slider_active if active else self.accent
        
        if filled_width > 0:
            cv2.rectangle(canvas, (slider_x, slider_y),
                         (slider_x + filled_width, slider_y + slider_height),
                         color, -1)
        
        # Thumb
        thumb_x = slider_x + filled_width
        thumb_radius = 10
        cv2.circle(canvas, (thumb_x, slider_y + slider_height // 2),
                  thumb_radius, color, -1)
        cv2.circle(canvas, (thumb_x, slider_y + slider_height // 2),
                  thumb_radius, self.text, 2)
        
        # Value display (right-aligned)
        value_text = f"{value:.2f}"
        value_x = self.config.GUI_WIDTH - 80
        self._text(canvas, value_text, value_x, y, color, 0.6, 2)
