"""Performance-optimized configuration."""

class Config:
    # Camera settings
    CAMERA_INDEX = 0
    CAMERA_WIDTH = 480
    CAMERA_HEIGHT = 360
    CAMERA_FPS = 60
    
    # MediaPipe settings
    MODEL_COMPLEXITY = 0
    MIN_DETECTION_CONF = 0.4
    MIN_TRACKING_CONF = 0.4
    
    # Mouse control
    DEFAULT_SENSITIVITY = 2.0
    SMOOTHING = 0.3
    DEADZONE_X = 0.15
    DEADZONE_Y = 0.15
    
    # Gesture thresholds
    CLICK_THRESHOLD = 0.05
    CLICK_COOLDOWN = 10
    
    # GUI settings
    GUI_WIDTH = 400
    GUI_HEIGHT = 400