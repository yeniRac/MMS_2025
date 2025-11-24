"""GUI with HCI standards - compact design with improved usability."""

import cv2
import numpy as np
import time
from config.settings import Config

class StatusGUI:
    def __init__(self, config: Config):
        self.config = config
        self.window_name = "Hand Gesture Mouse Control"
        
        # HCI-compliant color scheme (WCAG AA contrast ratios)
        self.bg = (40, 40, 42)  # Dark background
        self.surface = (55, 55, 58)  # Elevated surface
        self.text_primary = (255, 255, 255)  # White text
        self.text_secondary = (180, 180, 185)  # Muted text
        self.accent_primary = (76, 175, 80)  # Green (success)
        self.accent_danger = (244, 67, 54)  # Red (error/disabled)
        self.accent_warning = (255, 152, 0)  # Orange (warning)
        self.accent_info = (33, 150, 243)  # Blue (info)
        self.slider_track = (70, 70, 75)
        self.slider_fill = (33, 150, 243)
        self.button_default = (66, 66, 70)
        self.button_hover = (85, 85, 90)
        self.button_active = (76, 175, 80)
        self.divider = (80, 80, 85)
        
        # Reduced dimensions for compact layout
        self.width = 420
        self.height = 660
        
        # FPS tracking
        self.fps = 0.0
        self.frame_count = 0
        self.last_time = time.time()
        
        # Camera feed state
        self.show_camera = False
        self.camera_window_name = "Camera Feed"
        
        # Interactive elements state
        self.camera_button_rect = None
        self.button_hovered = False
        self.dragging_slider = None
        
        # Slider configuration with proper ranges
        self.sliders = {
            'sensitivity': {
                'y': 0, 'value': config.DEFAULT_SENSITIVITY,
                'min': 0.5, 'max': 5.0, 'label': 'Sensitivity',
                'unit': 'x'
            },
            'smoothing': {
                'y': 0, 'value': config.SMOOTHING,
                'min': 0.1, 'max': 0.8, 'label': 'Smoothing',
                'unit': ''
            },
            'deadzone': {
                'y': 0, 'value': config.DEADZONE_X,
                'min': 0.0, 'max': 0.3, 'label': 'Deadzone',
                'unit': ''
            },
            'click_threshold': {
                'y': 0, 'value': config.CLICK_THRESHOLD,
                'min': 0.02, 'max': 0.15, 'label': 'Click Threshold',
                'unit': ''
            }
        }
    
    def create_window(self):
        """Create GUI window with proper sizing."""
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.width, self.height)
        cv2.setMouseCallback(self.window_name, self._mouse_callback)
    
    def update_fps(self):
        """Update FPS counter."""
        self.frame_count += 1
        current = time.time()
        if current - self.last_time >= 1.0:
            self.fps = self.frame_count / (current - self.last_time)
            self.frame_count = 0
            self.last_time = current
    
    def _mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events with proper feedback."""
        # Button hover detection
        if event == cv2.EVENT_MOUSEMOVE or event == cv2.EVENT_LBUTTONDOWN:
            if self.camera_button_rect:
                x1, y1, x2, y2 = self.camera_button_rect
                self.button_hovered = (x1 <= x <= x2 and y1 <= y <= y2)
        
        if event == cv2.EVENT_LBUTTONDOWN:
            # Check button click
            if self.camera_button_rect and self.button_hovered:
                self.toggle_camera_feed()
                return
            
            # Check slider interaction
            for name, slider in self.sliders.items():
                slider_y = slider['y']
                if slider_y > 0 and abs(y - slider_y) < 12:
                    self.dragging_slider = name
                    self._update_slider_value(name, x)
        
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.dragging_slider:
                self._update_slider_value(self.dragging_slider, x)
        
        elif event == cv2.EVENT_LBUTTONUP:
            self.dragging_slider = None
    
    def toggle_camera_feed(self):
        """Toggle camera feed window."""
        self.show_camera = not self.show_camera
        if not self.show_camera:
            try:
                cv2.destroyWindow(self.camera_window_name)
            except:
                pass
    
    def handle_window_events(self) -> int:
        """Handle window events. Returns key code or -1."""
        return cv2.waitKey(1) & 0xFF
    
    def _update_slider_value(self, slider_name: str, x: int):
        """Update slider value with proper constraints."""
        slider = self.sliders[slider_name]
        slider_x = 140
        slider_width = self.width - slider_x - 80
        
        # Calculate normalized position
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
        """Draw compact HCI-compliant status display."""
        canvas = np.full((self.height, self.width, 3), self.bg, dtype=np.uint8)
        
        margin = 20
        y = 25
        
        # === HEADER ===
        self._draw_text(canvas, "Hand Gesture Mouse", margin, y, 
                       self.text_primary, 0.7, 2)
        y += 25
        self._draw_text(canvas, "Control Panel", margin, y, 
                       self.text_secondary, 0.5, 1)
        y += 30
        self._draw_divider(canvas, margin, y)
        y += 20
        
        # === STATUS INDICATORS ===
        status_items = [
            ("Mouse Control", enabled, "Active" if enabled else "Disabled"),
            ("Hand Detected", hand_detected, "Yes" if hand_detected else "No"),
        ]
        
        for label, is_active, value in status_items:
            y = self._draw_status_row(canvas, label, is_active, value, margin, y)
        
        # FPS indicator with performance color coding
        fps_color = self.accent_primary if self.fps > 50 else (
            self.accent_warning if self.fps > 30 else self.accent_danger)
        self._draw_indicator(canvas, margin + 8, y - 4, 6, fps_color, True)
        self._draw_text(canvas, "FPS:", margin + 25, y, self.text_secondary, 0.45, 1)
        self._draw_text(canvas, f"{self.fps:.0f}", self.width - margin - 40, y, 
                       fps_color, 0.5, 2)
        y += 25
        
        # Pinch distance with visual feedback
        pinch_color = self.accent_warning if is_clicking else self.text_secondary
        pinch_text = f"{pinch_distance:.3f}" if hand_detected else "---"
        indicator_active = is_clicking and hand_detected
        
        self._draw_indicator(canvas, margin + 8, y - 4, 6, pinch_color, indicator_active)
        self._draw_text(canvas, "Pinch:", margin + 25, y, self.text_secondary, 0.45, 1)
        self._draw_text(canvas, pinch_text, self.width - margin - 60, y, 
                       pinch_color, 0.5, 2)
        if is_clicking:
            self._draw_text(canvas, "[CLICK]", self.width - margin - 60, y + 12, 
                           self.accent_warning, 0.35, 1)
        y += 30
        
        self._draw_divider(canvas, margin, y)
        y += 20
        
        # === TOGGLE GESTURE PROGRESS ===
        self._draw_text(canvas, "Toggle Gesture", margin, y, 
                       self.text_primary, 0.55, 2)
        y += 20
        self._draw_text(canvas, "Hold tight pinch for 5 sec", margin, y, 
                       self.text_secondary, 0.4, 1)
        y += 18
        self._draw_progress_bar(canvas, toggle_progress, margin, y, 
                               self.width - 2 * margin, 20)
        y += 30
        
        self._draw_divider(canvas, margin, y)
        y += 20
        
        # === CAMERA FEED BUTTON ===
        button_text = "Hide Camera" if self.show_camera else "Show Camera"
        button_width = 180
        button_height = 32
        button_x = (self.width - button_width) // 2
        self._draw_button(canvas, button_text, button_x, y, 
                         button_width, button_height)
        y += button_height + 20
        
        self._draw_divider(canvas, margin, y)
        y += 20
        
        # === SETTINGS ===
        self._draw_text(canvas, "Settings", margin, y, self.text_primary, 0.55, 2)
        y += 22
        
        # Interactive sliders
        for name, slider in self.sliders.items():
            slider['y'] = y
            y = self._draw_slider_row(canvas, slider, margin, y,
                                     name == self.dragging_slider)
        
        y += 10
        self._draw_divider(canvas, margin, y)
        y += 18
        
        # === KEYBOARD SHORTCUTS ===
        self._draw_text(canvas, "Shortcuts", margin, y, self.text_primary, 0.55, 2)
        y += 22
        
        shortcuts = [("M", "Toggle Control"), ("Q", "Quit")]
        for key, desc in shortcuts:
            self._draw_shortcut(canvas, key, desc, margin, y)
            y += 24
        
        return canvas
    
    def _draw_text(self, canvas, text, x, y, color, scale=0.5, thickness=1):
        """Draw text with anti-aliasing."""
        cv2.putText(canvas, text, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX,
                   scale, color, thickness, cv2.LINE_AA)
    
    def _draw_divider(self, canvas, x, y):
        """Draw horizontal divider."""
        cv2.line(canvas, (x, y), (self.width - x, y), self.divider, 1)
    
    def _draw_indicator(self, canvas, x, y, radius, color, filled=True):
        """Draw status indicator circle."""
        if filled:
            cv2.circle(canvas, (int(x), int(y)), radius, color, -1)
        cv2.circle(canvas, (int(x), int(y)), radius, self.text_secondary, 1)
    
    def _draw_status_row(self, canvas, label, is_active, value, x, y):
        """Draw status row with indicator."""
        color = self.accent_primary if is_active else self.accent_danger
        self._draw_indicator(canvas, x + 8, y - 4, 6, color, is_active)
        self._draw_text(canvas, f"{label}:", x + 25, y, self.text_secondary, 0.45, 1)
        self._draw_text(canvas, value, self.width - x - 70, y, color, 0.5, 2)
        return y + 25
    
    def _draw_button(self, canvas, text, x, y, width, height):
        """Draw button with proper visual states."""
        if self.show_camera:
            bg_color = self.button_active
            border_color = self.button_active
            text_color = self.text_primary
        elif self.button_hovered:
            bg_color = self.button_hover
            border_color = self.accent_info
            text_color = self.text_primary
        else:
            bg_color = self.button_default
            border_color = self.text_secondary
            text_color = self.text_primary
        
        self.camera_button_rect = (x, y, x + width, y + height)
        
        # Background with rounded corners effect
        cv2.rectangle(canvas, (x, y), (x + width, y + height), bg_color, -1)
        cv2.rectangle(canvas, (x, y), (x + width, y + height), border_color, 2)
        
        # Centered text
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        text_x = x + (width - text_size[0]) // 2
        text_y = y + (height + text_size[1]) // 2
        self._draw_text(canvas, text, text_x, text_y, text_color, 0.5, 1)
    
    def _draw_progress_bar(self, canvas, progress, x, y, width, height):
        """Draw progress bar with gradient."""
        # Background
        cv2.rectangle(canvas, (x, y), (x + width, y + height), 
                     self.slider_track, -1)
        
        # Progress fill
        filled_width = int(width * progress)
        if filled_width > 0:
            # Color based on progress
            if progress < 0.3:
                color = self.accent_danger
            elif progress < 0.7:
                color = self.accent_warning
            else:
                color = self.accent_primary
            
            cv2.rectangle(canvas, (x, y), (x + filled_width, y + height), 
                         color, -1)
        
        # Border
        cv2.rectangle(canvas, (x, y), (x + width, y + height), 
                     self.text_secondary, 1)
        
        # Percentage text
        percentage = f"{int(progress * 100)}%"
        text_size = cv2.getTextSize(percentage, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
        text_x = x + (width - text_size[0]) // 2
        text_y = y + (height + text_size[1]) // 2
        self._draw_text(canvas, percentage, text_x, text_y, self.text_primary, 0.4, 1)
    
    def _draw_slider_row(self, canvas, slider, x, y, is_active):
        """Draw slider with label and value."""
        # Label
        self._draw_text(canvas, slider['label'], x, y, self.text_secondary, 0.45, 1)
        
        # Slider track
        slider_x = x + 120
        slider_y = y - 6
        slider_width = self.width - slider_x - x - 60
        slider_height = 6
        
        # Background track
        cv2.rectangle(canvas, (slider_x, slider_y),
                     (slider_x + slider_width, slider_y + slider_height),
                     self.slider_track, -1)
        
        # Filled portion
        normalized = (slider['value'] - slider['min']) / (slider['max'] - slider['min'])
        filled_width = int(slider_width * normalized)
        
        color = self.accent_info if is_active else self.slider_fill
        if filled_width > 0:
            cv2.rectangle(canvas, (slider_x, slider_y),
                         (slider_x + filled_width, slider_y + slider_height),
                         color, -1)
        
        # Thumb
        thumb_x = slider_x + filled_width
        thumb_y = slider_y + slider_height // 2
        cv2.circle(canvas, (thumb_x, thumb_y), 8, color, -1)
        cv2.circle(canvas, (thumb_x, thumb_y), 8, self.text_primary, 2)
        
        # Value display
        unit = slider.get('unit', '')
        value_text = f"{slider['value']:.2f}{unit}"
        value_x = self.width - x - 50
        self._draw_text(canvas, value_text, value_x, y, color, 0.45, 1)
        
        return y + 35
    
    def _draw_shortcut(self, canvas, key, description, x, y):
        """Draw keyboard shortcut with key badge."""
        # Key badge
        badge_width = 32
        badge_height = 20
        cv2.rectangle(canvas, (x, y - 14), (x + badge_width, y + 6),
                     self.surface, -1)
        cv2.rectangle(canvas, (x, y - 14), (x + badge_width, y + 6),
                     self.text_secondary, 1)
        
        # Key text (centered in badge)
        key_size = cv2.getTextSize(key, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)[0]
        key_x = x + (badge_width - key_size[0]) // 2
        key_y = y
        self._draw_text(canvas, key, key_x, key_y, self.text_primary, 0.45, 1)
        
        # Description
        self._draw_text(canvas, description, x + badge_width + 12, y, 
                       self.text_secondary, 0.45, 1)