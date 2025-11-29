"""Configuration optimized for relative mouse movement."""

class Config:
    # Camera settings
    CAMERA_INDEX = 0
    CAMERA_WIDTH = 960
    CAMERA_HEIGHT = 720
    CAMERA_FPS = 60
    
    # MediaPipe settings
    MODEL_COMPLEXITY = 0 
    MIN_DETECTION_CONF = 0.5
    MIN_TRACKING_CONF = 0.5
    
    # Mouse control 
    DEFAULT_SENSITIVITY = 3.0
    SMOOTHING = 0.50 
    DEADZONE_X = 0.002  
    DEADZONE_Y = 0.002
    
    # MediaPipe Hand Landmarks:
    STABLE_LANDMARKS = [1, 2, 3, 4, 0, 5, 9, 13, 17]  # Thumb chain + stable anchors
    STABLE_WEIGHTS = [2.0, 2.0, 2.5, 3.0, 1.5, 0.5, 1.0, 1.0, 1.0]  # Thumb tip = 3.0 weight
    
    # Gesture thresholds
    CLICK_THRESHOLD = 0.05  
    TOGGLE_THRESHOLD = 0.30
    TOGGLE_DURATION = 2.0
    
    # GUI settings
    GUI_WIDTH = 600
    GUI_HEIGHT = 750
    
    # Performance settings
    GUI_UPDATE_FPS = 30  
    HAND_DETECTION_SKIP_FRAMES = 0

    # Advanced settings
    ENABLE_PREDICTION = True