"""Configuration optimized for relative mouse movement."""

class Config:
    # Camera settings
    CAMERA_INDEX = 0
    CAMERA_WIDTH = 480
    CAMERA_HEIGHT = 360
    CAMERA_FPS = 60
    
    # MediaPipe settings
    MODEL_COMPLEXITY = 0 
    MIN_DETECTION_CONF = 0.5
    MIN_TRACKING_CONF = 0.5
    
    # Mouse control 
    DEFAULT_SENSITIVITY = 3.0  
    SMOOTHING = 0.20 
    DEADZONE_X = 0.00  
    DEADZONE_Y = 0.00
    
    # Gesture thresholds
    CLICK_THRESHOLD = 0.05  
    TOGGLE_THRESHOLD = 0.20
    TOGGLE_DURATION = 2.0
    
    # GUI settings
    GUI_WIDTH = 600
    GUI_HEIGHT = 750