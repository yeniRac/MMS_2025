"""Configuration optimized for relative mouse movement."""

class Config:
    # Camera settings
    CAMERA_INDEX = 0
    CAMERA_WIDTH = 480
    CAMERA_HEIGHT = 360
    CAMERA_FPS = 60
    
    # MediaPipe settings
    MODEL_COMPLEXITY = 0  # Fastest
    MIN_DETECTION_CONF = 0.5
    MIN_TRACKING_CONF = 0.5
    
    # Mouse control - OPTIMIZED FOR RELATIVE MOVEMENT
    DEFAULT_SENSITIVITY = 3.5  # Higher for relative movement
    SMOOTHING = 0.35  # Moderate smoothing for relative deltas
    DEADZONE_X = 0.08  # Smaller deadzone for center area
    DEADZONE_Y = 0.08
    
    # Gesture thresholds
    CLICK_THRESHOLD = 0.045  # Slightly higher for more stable hold
    TOGGLE_THRESHOLD = 0.20
    TOGGLE_DURATION = 2.0
    
    # GUI settings
    GUI_WIDTH = 600
    GUI_HEIGHT = 750