"""Low-latency hand tracking module optimized for real-time control."""

import cv2
import mediapipe as mp
import numpy as np
from collections import deque


class HandTracker:
    """Real-time hand tracker optimized for minimal latency."""
    
    def __init__(self, model_complexity=0, min_detection_confidence=0.5, 
                 min_tracking_confidence=0.5, downscale_factor=1.0):
        """Initialize hand tracker with performance settings."""
        print("Initializing Hand Tracker...")
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        self.downscale_factor = downscale_factor
        self.process_width = None
        self.process_height = None
        
        self.cap = None
        self.running = False
        self.last_hand_landmarks = None
        
        self._process_frame = None
        
        print(f"Model complexity: {model_complexity}")
        print(f"Downscale factor: {downscale_factor}x")
        print(f"Detection confidence: {min_detection_confidence}")
    
    def start_camera(self, camera_index=0, width=640, height=480, fps=60):
        """Initialize camera with specified parameters."""
        print(f"Starting camera {camera_index}...")
        
        self.cap = cv2.VideoCapture(camera_index)
        
        if not self.cap.isOpened():
            print("Failed to open camera")
            return False
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        
        self.process_width = int(width * self.downscale_factor)
        self.process_height = int(height * self.downscale_factor)
        
        if self.downscale_factor != 1.0:
            self._process_frame = np.zeros((self.process_height, self.process_width, 3), dtype=np.uint8)
        
        self.running = True
        
        actual_w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        print(f"Camera: {actual_w}x{actual_h} @ {actual_fps}fps")
        print(f"Processing: {self.process_width}x{self.process_height}")
        
        return True
    
    def read_frame(self, flip=True):
        """Read and optionally flip camera frame."""
        if not self.cap:
            return False, None, None
        
        ret, frame = self.cap.read()
        if not ret:
            return False, None, None
        
        if flip:
            cv2.flip(frame, 1, frame)
        
        if self.downscale_factor != 1.0:
            cv2.resize(frame, (self.process_width, self.process_height), 
                      dst=self._process_frame, interpolation=cv2.INTER_NEAREST)
            process_frame = self._process_frame
        else:
            process_frame = frame
        
        return ret, frame, process_frame
    
    def detect_hands(self, frame):
        """Detect hands in frame and return results."""
        if frame is None:
            return None
        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        
        if results and results.multi_hand_landmarks:
            self.last_hand_landmarks = results.multi_hand_landmarks[0]
        
        return results
    
    def get_index_finger_position(self, hand_landmarks):
        """Extract index finger tip position."""
        idx = hand_landmarks.landmark[8]
        return idx.x, idx.y
    
    def get_thumb_index_distance(self, hand_landmarks):
        """Calculate 2D distance between thumb and index finger."""
        thumb = hand_landmarks.landmark[4]
        index = hand_landmarks.landmark[8]
        
        dx = index.x - thumb.x
        dy = index.y - thumb.y
        
        return np.sqrt(dx*dx + dy*dy)
    
    def draw_minimal_landmarks(self, frame, hand_landmarks, scale_x=1.0, scale_y=1.0):
        """Draw minimal landmarks for performance."""
        h, w = frame.shape[:2]
        
        thumb = hand_landmarks.landmark[4]
        index = hand_landmarks.landmark[8]
        
        # MediaPipe returns normalized coordinates (0-1), multiply by frame dimensions
        # No scaling needed - normalized coords work on any frame size
        tx = int(thumb.x * w)
        ty = int(thumb.y * h)
        ix = int(index.x * w)
        iy = int(index.y * h)
        
        cv2.circle(frame, (tx, ty), 6, (255, 0, 0), -1)
        cv2.circle(frame, (ix, iy), 6, (0, 255, 0), -1)
        cv2.line(frame, (tx, ty), (ix, iy), (255, 255, 0), 2)
    
    def cleanup(self):
        """Release resources."""
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
    
    def __del__(self):
        self.cleanup()


class PerformanceMonitor:
    """FPS and latency monitoring."""
    
    def __init__(self, window_size=30):
        self.frame_times = deque(maxlen=window_size)
        self.last_time = None
    
    def tick(self):
        """Record frame time."""
        import time
        current = time.perf_counter()
        
        if self.last_time is not None:
            self.frame_times.append(current - self.last_time)
        
        self.last_time = current
    
    def get_fps(self):
        """Calculate average FPS."""
        if len(self.frame_times) == 0:
            return 0
        avg_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_time if avg_time > 0 else 0
    
    def get_latency_ms(self):
        """Calculate average latency in milliseconds."""
        if len(self.frame_times) == 0:
            return 0
        return (sum(self.frame_times) / len(self.frame_times)) * 1000