"""Hand tracking with MediaPipe - OPTIMIZED."""

import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, Tuple
from config.settings import Config


class HandTracker:
    def __init__(self, config: Config):
        self.config = config
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=config.MODEL_COMPLEXITY,
            min_detection_confidence=config.MIN_DETECTION_CONF,
            min_tracking_confidence=config.MIN_TRACKING_CONF
        )
        self.cap: Optional[cv2.VideoCapture] = None
        
        # Frame skipping for performance
        self.frame_skip = config.HAND_DETECTION_SKIP_FRAMES
        self.frame_counter = 0
        self._last_result = None
    
    def start(self) -> bool:
        """Initialize camera."""
        self.cap = cv2.VideoCapture(self.config.CAMERA_INDEX)
        if not self.cap.isOpened():
            return False
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, self.config.CAMERA_FPS)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        return True
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read and flip frame."""
        if not self.cap:
            return False, None
        ret, frame = self.cap.read()
        return (ret, cv2.flip(frame, 1)) if ret else (False, None)
    
    def detect_hand(self, frame: np.ndarray):
        """Detect hand landmarks with optional frame skipping."""
        self.frame_counter += 1
        
        # Skip frames if enabled (return last result for smooth tracking)
        if self.frame_skip > 0 and self.frame_counter % (self.frame_skip + 1) != 0:
            return self._last_result
        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        self._last_result = results.multi_hand_landmarks[0] if results.multi_hand_landmarks else None
        return self._last_result
    
    @staticmethod
    def get_pinch_distance(hand_landmarks) -> float:
        """Get thumb-index distance."""
        thumb, index = hand_landmarks.landmark[4], hand_landmarks.landmark[8]
        dx, dy = index.x - thumb.x, index.y - thumb.y
        return np.sqrt(dx * dx + dy * dy)
    
    def cleanup(self):
        """Release resources."""
        if self.cap:
            self.cap.release()
        self.hands.close()