"""Professional GUI with clean, well-formatted design."""

import time

import cv2
import numpy as np

from config.settings import Config


class StatusGUI:
    """GUI for hand gesture mouse control status and settings."""

    def __init__(self, config: Config):
        """Initialize the GUI with configuration."""
        self.config = config
        self.window_name = "Hand Gesture Mouse Control"

        # Professional color scheme - consistent blues and grays
        self.bg_primary = (32, 33, 36)  # Dark gray background
        self.bg_secondary = (48, 49, 52)  # Lighter gray for sections
        self.bg_elevated = (60, 61, 64)  # Elevated elements

        self.accent_primary = (66, 133, 244)  # Primary blue
        self.accent_success = (66, 133, 244)  # Success - also blue
        self.accent_warning = (66, 133, 244)  # Warning - also blue
        self.accent_active = (66, 133, 244)  # Active state blue
        self.accent_disabled = (95, 99, 104)  # Disabled gray

        self.text_primary = (241, 243, 244)  # White text
        self.text_secondary = (154, 160, 166)  # Gray text
        self.text_disabled = (95, 99, 104)  # Disabled text

        self.border_light = (95, 99, 104)  # Light borders
        self.border_dark = (60, 64, 67)  # Dark borders

        # Window dimensions - larger and more comfortable
        self.width = 510
        self.height = 830

        # Layout constants
        self.margin = 24
        self.section_spacing = 20
        self.item_spacing = 28

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

        # Double-click tracking for sliders
        self.last_click_time = 0
        self.last_clicked_slider = None
        self.double_click_threshold = 0.5  # seconds

        # Slider configuration
        self.sliders = {
            'sensitivity': {
                'y': 0,
                'value': config.DEFAULT_SENSITIVITY,
                'default': config.DEFAULT_SENSITIVITY,
                'min': 0.5,
                'max': 5.0,
                'label': 'Sensitivity',
                'description': 'Cursor movement speed'
            },
            'smoothing': {
                'y': 0,
                'value': config.SMOOTHING,
                'default': config.SMOOTHING,
                'min': 0.1,
                'max': 0.8,
                'label': 'Smoothing',
                'description': 'Motion smoothness'
            },
            'deadzone': {
                'y': 0,
                'value': config.DEADZONE_X * 100,
                'default': config.DEADZONE_X * 100,
                'min': 0.0,
                'max': 1.0,
                'label': 'Deadzone',
                'description': 'Minimum movement threshold'
            },
            'click_threshold': {
                'y': 0,
                'value': config.CLICK_THRESHOLD,
                'default': config.CLICK_THRESHOLD,
                'min': 0.02,
                'max': 0.15,
                'label': 'Click Threshold',
                'description': 'Pinch distance to click'
            }
        }

        # Audio feedback setup
        self.audio_enabled = True
        try:
            import pygame
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.pygame = pygame
            # Generate toggle sounds
            self._generate_toggle_sounds()
        except ImportError:
            self.audio_enabled = False
            self.pygame = None
            print("pygame not available - audio feedback disabled")
        except Exception as e:
            self.audio_enabled = False
            self.pygame = None
            print(f"Could not initialize audio: {e}")

        # Track last enabled state to detect toggle
        self.last_enabled_state = None
            
    def create_window(self):
        """Create and configure the GUI window."""
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.width, self.height)
        cv2.setMouseCallback(self.window_name, self._mouse_callback)
    
    def _generate_toggle_sounds(self):
        """Generate sounds for enable/disable toggle."""
        import numpy as np
        
        sample_rate = 22050
        
        # Enable sound (rising two-tone beep)
        duration = 0.15
        samples = int(sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        # First tone (lower)
        freq1 = 800
        wave1 = np.sin(2 * np.pi * freq1 * t[:samples//2])
        
        # Second tone (higher)
        freq2 = 1200
        wave2 = np.sin(2 * np.pi * freq2 * t[samples//2:])
        
        # Combine
        wave_enable = np.concatenate([wave1, wave2])
        
        # Apply envelope
        envelope = np.exp(-3 * t)
        wave_enable *= envelope
        
        # Convert to 16-bit audio
        audio_enable = np.array(wave_enable * 32767, dtype=np.int16)
        stereo_enable = np.column_stack((audio_enable, audio_enable))
        
        # Disable sound (falling two-tone beep)
        wave1_disable = np.sin(2 * np.pi * freq2 * t[:samples//2])
        wave2_disable = np.sin(2 * np.pi * freq1 * t[samples//2:])
        wave_disable = np.concatenate([wave1_disable, wave2_disable])
        wave_disable *= envelope
        
        audio_disable = np.array(wave_disable * 32767, dtype=np.int16)
        stereo_disable = np.column_stack((audio_disable, audio_disable))
        
        # Create pygame Sound objects
        self.enable_sound = self.pygame.sndarray.make_sound(stereo_enable)
        self.enable_sound.set_volume(0.4)  # 40% volume
        
        self.disable_sound = self.pygame.sndarray.make_sound(stereo_disable)
        self.disable_sound.set_volume(0.4)  # 40% volume

    def play_toggle_sound(self, enabled: bool):
        """Play sound when mouse control is toggled."""
        if not self.audio_enabled or not self.pygame:
            return
        
        # Check if state has changed
        if self.last_enabled_state is not None and self.last_enabled_state != enabled:
            try:
                if enabled:
                    self.enable_sound.play()
                else:
                    self.disable_sound.play()
            except:
                pass
        
        self.last_enabled_state = enabled

    def update_fps(self):
        """Update frames per second calculation."""
        self.frame_count += 1
        current = time.time()
        
        if current - self.last_time >= 1.0:
            self.fps = self.frame_count / (current - self.last_time)
            self.frame_count = 0
            self.last_time = current
    
    def toggle_camera_feed(self):
        """Toggle the camera feed window visibility."""
        self.show_camera = not self.show_camera
        
        if not self.show_camera:
            try:
                cv2.destroyWindow(self.camera_window_name)
            except:
                pass
    
    def handle_window_events(self) -> int:
        """Handle OpenCV window events. Returns pressed key code or -1."""
        return cv2.waitKey(1) & 0xFF
    
    # =========================================================================
    # MOUSE INTERACTION HANDLING
    # =========================================================================
    
    def _mouse_callback(self, event, x, y, flags, param):
        """Handle all mouse interactions with GUI elements."""
        # Update hover state for button
        if event in (cv2.EVENT_MOUSEMOVE, cv2.EVENT_LBUTTONDOWN):
            self._update_button_hover(x, y)
        
        # Handle mouse button down
        if event == cv2.EVENT_LBUTTONDOWN:
            if self._handle_button_click(x, y):
                return
            self._handle_slider_click(x, y)
        
        # Handle mouse drag
        elif event == cv2.EVENT_MOUSEMOVE:
            self._handle_slider_drag(x)
        
        # Handle mouse button up
        elif event == cv2.EVENT_LBUTTONUP:
            self.dragging_slider = None
    
    def _update_button_hover(self, x: int, y: int):
        """Update button hover state based on mouse position."""
        if self.camera_button_rect:
            x1, y1, x2, y2 = self.camera_button_rect
            self.button_hovered = (x1 <= x <= x2 and y1 <= y <= y2)
    
    def _handle_button_click(self, x: int, y: int) -> bool:
        """Handle button click. Returns True if button was clicked."""
        if self.camera_button_rect and self.button_hovered:
            self.toggle_camera_feed()
            return True
        return False
    
    def _handle_slider_click(self, x: int, y: int):
        """Handle slider click to start dragging or reset on double-click."""
        current_time = time.time()
        
        for name, slider in self.sliders.items():
            slider_track_y = slider['y'] + 28
            if slider_track_y > 0 and abs(y - slider_track_y) < 15:
                # Check for double-click
                if (self.last_clicked_slider == name and 
                    current_time - self.last_click_time < self.double_click_threshold):
                    # Double-click detected - reset to default
                    slider['value'] = slider['default']
                    self._apply_slider_config(name, slider['default'])
                    self.last_clicked_slider = None
                    self.last_click_time = 0
                else:
                    # Single click - start dragging
                    self.dragging_slider = name
                    self._update_slider_value(name, x)
                    self.last_clicked_slider = name
                    self.last_click_time = current_time
                break
    
    def _handle_slider_drag(self, x: int):
        """Handle slider dragging."""
        if self.dragging_slider:
            self._update_slider_value(self.dragging_slider, x)
    
    def _update_slider_value(self, slider_name: str, x: int):
        """Update slider value based on mouse x position."""
        slider = self.sliders[slider_name]
        
        # Calculate slider bounds
        slider_x = self.margin + 160
        slider_width = self.width - slider_x - self.margin - 60
        
        # Clamp position to slider bounds
        pos = max(0, min(slider_width, x - slider_x))
        normalized = pos / slider_width
        
        # Calculate value
        raw_value = slider['min'] + normalized * (slider['max'] - slider['min'])
        
        # Snap to 0.05 increments
        value = round(raw_value / 0.05) * 0.05
        
        # Clamp to min/max
        value = max(slider['min'], min(slider['max'], value))
        
        slider['value'] = value
        
        # Update configuration
        self._apply_slider_config(slider_name, value)
    
    def _apply_slider_config(self, slider_name: str, value: float):
        """Apply slider value to configuration."""
        if slider_name == 'sensitivity':
            self.config.DEFAULT_SENSITIVITY = value
        elif slider_name == 'smoothing':
            self.config.SMOOTHING = value
        elif slider_name == 'deadzone':
            self.config.DEADZONE_X = value / 100  # Scale down for actual use
            self.config.DEADZONE_Y = value / 100
        elif slider_name == 'click_threshold':
            self.config.CLICK_THRESHOLD = value
    
    # =========================================================================
    # MAIN DRAWING FUNCTION
    # =========================================================================
    
    def draw_status(self, enabled: bool, hand_detected: bool,
                pinch_distance: float = 0.0, is_clicking: bool = False,
                toggle_progress: float = 0.0) -> np.ndarray:
        """
        Draw the complete GUI with all status information.
        
        Args:
            enabled: Whether mouse control is enabled
            hand_detected: Whether a hand is currently detected
            pinch_distance: Current pinch distance value
            is_clicking: Whether a click is currently being performed
            toggle_progress: Progress toward toggle gesture (0.0 to 1.0)
        
        Returns:
            NumPy array containing the rendered GUI image
        """
        # Play audio feedback when toggle state changes
        self.play_toggle_sound(enabled)
        
        # Create canvas
        canvas = np.full((self.height, self.width, 3), self.bg_primary, dtype=np.uint8)
        y = self.margin
        
        # Draw header
        y = self._draw_header(canvas, y)
        y += self.section_spacing
        
        # Draw status section
        y = self._draw_status_section(canvas, y, enabled, hand_detected, 
                                      pinch_distance, is_clicking)
        y += self.section_spacing
        
        # Draw toggle gesture section
        y = self._draw_toggle_section(canvas, y, toggle_progress)
        
        # Draw camera button
        y = self._draw_camera_button(canvas, y)
        y += self.section_spacing
        
        # Draw settings section
        y = self._draw_settings_section(canvas, y)
        y += self.section_spacing
        
        # Draw keyboard shortcuts
        y = self._draw_shortcuts_section(canvas, y)
        
        return canvas
    
    # =========================================================================
    # SECTION DRAWING FUNCTIONS
    # =========================================================================
    
    def _draw_header(self, canvas: np.ndarray, y: int) -> int:
        """Draw the header section."""
        y += 8
        
        self._draw_text(canvas, "Hand Gesture Mouse Control",
                       self.margin, y, self.text_primary, 0.8, 2)
        y += 32
        
        # Draw FPS in top right
        fps_text = f"FPS: {self.fps:.0f}"
        fps_color = self._get_fps_color()
        fps_width = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0][0]
        self._draw_text(canvas, fps_text,
                       self.width - self.margin - fps_width, y - 20,
                       fps_color, 0.5, 1)
        
        # Draw separator line
        self._draw_separator(canvas, y)
        y += self.section_spacing
        
        return y
    
    def _draw_status_section(self, canvas: np.ndarray, y: int,
                            enabled: bool, hand_detected: bool,
                            pinch_distance: float, is_clicking: bool) -> int:
        """Draw the status information section."""
        # Section title
        self._draw_text(canvas, "Status", self.margin, y,
                       self.text_secondary, 0.55, 1)
        y += 26
        
        # Mouse control status
        y = self._draw_status_item(canvas, "Mouse Control", y,
                                   "Enabled" if enabled else "Disabled",
                                   self.accent_primary if enabled else self.accent_disabled)
        
        # Hand detection status
        y = self._draw_status_item(canvas, "Hand Detection", y,
                                   "Detected" if hand_detected else "Searching",
                                   self.accent_primary if hand_detected else self.accent_disabled)
        
        # Pinch distance
        pinch_text = f"{pinch_distance:.3f}" if hand_detected else "---"
        pinch_color = self.accent_primary if is_clicking else self.accent_disabled
        y = self._draw_status_item(canvas, "Finger Distance", y, pinch_text, pinch_color)
        
        # Click indicator
        if is_clicking:
            indicator_x = self.width - self.margin - 100
            self._draw_pill(canvas, "CLICKING", indicator_x, y - self.item_spacing + 5,
                          self.accent_primary, self.text_primary)
        
        y += 4
        self._draw_separator(canvas, y)
        y += self.section_spacing
        
        return y
    
    def _draw_toggle_section(self, canvas: np.ndarray, y: int,
                            toggle_progress: float) -> int:
        """Draw the toggle gesture section."""
        # Section title
        self._draw_text(canvas, "Toggle Gesture", self.margin, y,
                       self.text_secondary, 0.55, 1)
        y += 26
        
        # Description
        self._draw_text(canvas, "Spread your fingers to toggle mouse control",
                       self.margin, y, self.text_disabled, 0.45, 1)
        y += 26
        
        # Progress bar
        bar_width = self.width - 2 * self.margin
        y = self._draw_progress_bar(canvas, toggle_progress, self.margin, y, bar_width)
        y += 16
        
        self._draw_separator(canvas, y)
        y += self.section_spacing
        
        return y
    
    def _draw_camera_button(self, canvas: np.ndarray, y: int) -> int:
        """Draw the camera feed toggle button."""
        button_width = self.width - 2 * self.margin
        button_height = 50
        button_text = "Hide Camera Feed" if self.show_camera else "Show Camera Feed"
        
        # Draw button
        self._draw_button(canvas, button_text, self.margin, y,
                         button_width, button_height)
        
        y += button_height + self.section_spacing
        self._draw_separator(canvas, y)
        y += self.section_spacing
        
        return y
    
    def _draw_settings_section(self, canvas: np.ndarray, y: int) -> int:
        """Draw the settings section with sliders."""
        # Section title
        self._draw_text(canvas, "Settings", self.margin, y,
                       self.text_secondary, 0.55, 1)
        
        # Hint text
        hint_width = cv2.getTextSize("Double-click to reset", cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0][0]
        self._draw_text(canvas, "Double-click to reset", 
                       self.width - self.margin - hint_width, y,
                       self.text_disabled, 0.4, 1)
        y += 26
        
        # Draw all sliders
        for name, slider in self.sliders.items():
            slider['y'] = y + 10
            y = self._draw_slider(canvas, slider, self.margin, y,
                                 name == self.dragging_slider)
            y += 10
        
        # Keyboard settings hint
        y += 4
        self._draw_text(canvas, "Keyboard: M = Toggle control  |  Q = Quit", 
                       self.margin, y,
                       self.text_disabled, 0.4, 1)
        y += 16
        
        self._draw_separator(canvas, y)
        y += self.section_spacing
        
        return y
    
    def _draw_shortcuts_section(self, canvas: np.ndarray, y: int) -> int:
        """Draw the keyboard shortcuts section."""
        # Section title
        self._draw_text(canvas, "Keyboard Shortcuts", self.margin, y,
                       self.text_secondary, 0.55, 1)
        y += 26
        
        # Shortcuts
        shortcuts = [
            ("M", "Toggle mouse control"),
            ("Q", "Quit application")
        ]
        
        for key, description in shortcuts:
            y = self._draw_shortcut(canvas, key, description, self.margin, y)
            y += 10
        
        return y
    
    # =========================================================================
    # UI COMPONENT DRAWING FUNCTIONS
    # =========================================================================
    
    def _draw_status_item(self, canvas: np.ndarray, label: str, y: int,
                         value: str, color: tuple) -> int:
        """Draw a single status item row."""
        # Status indicator dot
        dot_x = self.margin + 8
        dot_y = y - 5
        cv2.circle(canvas, (dot_x, dot_y), 5, color, -1)
        cv2.circle(canvas, (dot_x, dot_y), 5, self.border_light, 1)
        
        # Label
        self._draw_text(canvas, label, self.margin + 25, y,
                       self.text_secondary, 0.5, 1)
        
        # Value (right-aligned)
        value_width = cv2.getTextSize(str(value), cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)[0][0]
        self._draw_text(canvas, str(value), self.width - self.margin - value_width, y,
                       self.text_primary, 0.55, 2)
        
        return y + self.item_spacing
    
    def _draw_button(self, canvas: np.ndarray, text: str,
                    x: int, y: int, width: int, height: int):
        """Draw a button with hover and active states."""
        # Determine button appearance
        if self.show_camera:
            bg_color = self.accent_primary
            border_color = self.accent_primary
            text_color = self.text_primary
        elif self.button_hovered:
            bg_color = self.bg_elevated
            border_color = self.accent_primary
            text_color = self.accent_primary
        else:
            bg_color = self.bg_secondary
            border_color = self.border_dark
            text_color = self.text_primary
        
        # Store button rectangle for click detection
        self.camera_button_rect = (x, y, x + width, y + height)
        
        # Draw button background
        cv2.rectangle(canvas, (x, y), (x + width, y + height), bg_color, -1)
        cv2.rectangle(canvas, (x, y), (x + width, y + height), border_color, 2)
        
        # Draw centered text
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)[0]
        text_x = x + (width - text_size[0]) // 2
        text_y = y + (height + text_size[1]) // 2
        self._draw_text(canvas, text, text_x, text_y, text_color, 0.55, 1)
    
    def _draw_progress_bar(self, canvas: np.ndarray, progress: float,
                          x: int, y: int, width: int) -> int:
        """Draw a progress bar."""
        height = 24
        
        # Background
        cv2.rectangle(canvas, (x, y), (x + width, y + height),
                     self.bg_secondary, -1)
        cv2.rectangle(canvas, (x, y), (x + width, y + height),
                     self.border_dark, 1)
        
        # Progress fill
        filled_width = int(width * progress)
        if filled_width > 0:
            fill_color = self.accent_primary
            
            cv2.rectangle(canvas, (x, y), (x + filled_width, y + height),
                         fill_color, -1)
        
        # Percentage text
        percentage_text = f"{int(progress * 100)}%"
        text_size = cv2.getTextSize(percentage_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        text_x = x + (width - text_size[0]) // 2
        text_y = y + (height + text_size[1]) // 2
        self._draw_text(canvas, percentage_text, text_x, text_y,
                       self.text_primary, 0.5, 1)
        
        return y + height
    
    def _draw_slider(self, canvas: np.ndarray, slider: dict,
                    x: int, y: int, is_active: bool) -> int:
        """Draw an interactive slider with label and value."""
        # Label
        self._draw_text(canvas, slider['label'], x, y,
                       self.text_primary, 0.5, 1)
        y += 18
        
        # Description
        self._draw_text(canvas, slider['description'], x, y,
                       self.text_disabled, 0.4, 1)
        y += 20
        
        # Slider track
        slider_x = x + 160
        slider_width = self.width - slider_x - self.margin - 60
        track_height = 6
        track_y = y - 3
        
        # Background track
        cv2.rectangle(canvas, (slider_x, track_y),
                     (slider_x + slider_width, track_y + track_height),
                     self.bg_secondary, -1)
        
        # Calculate fill
        normalized = (slider['value'] - slider['min']) / (slider['max'] - slider['min'])
        filled_width = int(slider_width * normalized)
        
        # Use consistent blue color
        slider_color = self.accent_primary
        
        # Filled track
        if filled_width > 0:
            cv2.rectangle(canvas, (slider_x, track_y),
                         (slider_x + filled_width, track_y + track_height),
                         slider_color, -1)
        
        # Thumb
        thumb_x = slider_x + filled_width
        thumb_y = track_y + track_height // 2
        thumb_size = 16
        cv2.rectangle(canvas, (thumb_x - thumb_size//2, thumb_y - thumb_size//2),
             (thumb_x + thumb_size//2, thumb_y + thumb_size//2),
             slider_color, -1)
        cv2.rectangle(canvas, (thumb_x - thumb_size//2, thumb_y - thumb_size//2),
             (thumb_x + thumb_size//2, thumb_y + thumb_size//2),
             self.text_primary, 2)
        
        # Value display
        value_text = f"{slider['value']:.2f}"
        value_x = self.width - self.margin - 50
        self._draw_text(canvas, value_text, value_x, y,
                       self.text_primary, 0.5, 1)
        
        return y + 28
    
    def _draw_shortcut(self, canvas: np.ndarray, key: str,
                      description: str, x: int, y: int) -> int:
        """Draw a keyboard shortcut item."""
        # Key box
        key_size = 30
        cv2.rectangle(canvas, (x, y - 20), (x + key_size, y + 10),
                     self.bg_secondary, -1)
        cv2.rectangle(canvas, (x, y - 20), (x + key_size, y + 10),
                     self.border_dark, 1)
        
        # Key text (centered)
        key_text_size = cv2.getTextSize(key, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        key_x = x + (key_size - key_text_size[0]) // 2
        self._draw_text(canvas, key, key_x, y, self.text_primary, 0.5, 1)
        
        # Description
        self._draw_text(canvas, description, x + key_size + 15, y,
                       self.text_secondary, 0.5, 1)
        
        return y + 30
    
    def _draw_pill(self, canvas: np.ndarray, text: str,
                  x: int, y: int, bg_color: tuple, text_color: tuple):
        """Draw a pill-shaped badge."""
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
        padding = 8
        width = text_size[0] + padding * 2
        height = 20
        
        # Background
        cv2.rectangle(canvas, (x, y), (x + width, y + height), bg_color, -1)
        
        # Text
        text_x = x + padding
        text_y = y + (height + text_size[1]) // 2
        self._draw_text(canvas, text, text_x, text_y, text_color, 0.4, 1)
    
    # =========================================================================
    # UTILITY FUNCTIONS
    # =========================================================================
    
    def _draw_text(self, canvas: np.ndarray, text: str,
                  x: int, y: int, color: tuple, scale: float = 0.5,
                  thickness: int = 1):
        """Draw text with anti-aliasing."""
        cv2.putText(canvas, str(text), (int(x), int(y)),
                   cv2.FONT_HERSHEY_SIMPLEX, scale, color,
                   thickness, cv2.LINE_AA)
    
    def _draw_separator(self, canvas: np.ndarray, y: int):
        """Draw a horizontal separator line."""
        cv2.line(canvas, (self.margin, y),
                (self.width - self.margin, y),
                self.border_dark, 1)
    
    def _get_fps_color(self) -> tuple:
        """Get color for FPS display based on performance."""
        if self.fps >= 55:
            return self.accent_primary
        else:
            return self.text_secondary