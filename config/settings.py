"""Performance-optimized configuration for hand gesture mouse control."""

# Camera settings - optimized for 20ms latency
CAMERA_INDEX = 0
CAMERA_WIDTH = 480
CAMERA_HEIGHT = 360
CAMERA_FPS = 120

# Hand detection settings - optimized for speed
MODEL_COMPLEXITY = 0
MIN_DETECTION_CONFIDENCE = 0.4
MIN_TRACKING_CONFIDENCE = 0.4
DOWNSCALE_FACTOR = 0.5

# Mouse control settings
DEFAULT_SENSITIVITY = 2.0
SMOOTHING_FACTOR = 0.4
DEAD_ZONE = 0.002

# Gesture settings
CLICK_THRESHOLD = 0.05
RELEASE_THRESHOLD = 0.07
CLICK_COOLDOWN_FRAMES = 8

# UI settings
WINDOW_TITLE = "Hand Gesture Mouse Control"
SHOW_PERFORMANCE_STATS = True


def get_config_summary():
    """Return formatted configuration summary."""
    separator = "=" * 50
    return f"""
Configuration Summary:
{separator}
Camera:
  Resolution: {CAMERA_WIDTH}x{CAMERA_HEIGHT}
  FPS: {CAMERA_FPS}
  Downscale: {DOWNSCALE_FACTOR}x

Detection:
  Model complexity: {MODEL_COMPLEXITY}
  Detection confidence: {MIN_DETECTION_CONFIDENCE}
  Tracking confidence: {MIN_TRACKING_CONFIDENCE}

Mouse Control:
  Sensitivity: {DEFAULT_SENSITIVITY}
  Smoothing: {SMOOTHING_FACTOR}
  Dead zone: {DEAD_ZONE}

Gestures:
  Click threshold: {CLICK_THRESHOLD}
  Release threshold: {RELEASE_THRESHOLD}
  Cooldown: {CLICK_COOLDOWN_FRAMES} frames

UI:
  Show stats: {SHOW_PERFORMANCE_STATS}
{separator}
"""


if __name__ == "__main__":
    print("Configuration Test")
    print("=" * 70)
    print(get_config_summary())