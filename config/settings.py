"""Performance-optimized configuration with snappy click settings."""

class Config:
    # Camera settings
    CAMERA_INDEX = 0
    CAMERA_WIDTH = 480
    CAMERA_HEIGHT = 360
    CAMERA_FPS = 60
    
    # MediaPipe settings
    MODEL_COMPLEXITY = 0  # Fastest
    MIN_DETECTION_CONF = 0.5  # Slightly higher for stability
    MIN_TRACKING_CONF = 0.5
    
    # Mouse control
    DEFAULT_SENSITIVITY = 2.0
    SMOOTHING = 0.25  # Less smoothing for snappier feel
    DEADZONE_X = 0.15
    DEADZONE_Y = 0.15
    
    # Gesture thresholds - OPTIMIZED FOR SNAPPY CLICKS
    CLICK_THRESHOLD = 0.04  # Slightly lower for easier triggering
    CLICK_COOLDOWN = 6  # Reduced cooldown for faster repeat clicks
    TOGGLE_THRESHOLD = 0.20  # REDUCED from 0.25 - less spreading needed
    TOGGLE_DURATION = 2.0
    
    # GUI settings
    GUI_WIDTH = 600
    GUI_HEIGHT = 750