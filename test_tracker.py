"""Complete hand tracking pipeline test."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.hand_tracker import HandTracker, PerformanceMonitor
from utils.coordinate_processor import CoordinateProcessor, PinchDetector
from config import settings
import cv2


class OptimizedHandTrackerDemo:
    """Full hand tracking pipeline demonstration."""
    
    def __init__(self):
        """Initialize all components."""
        print("="*70)
        print("Ultra Low Latency Hand Tracker - Target: 20ms")
        print("="*70)
        
        print(settings.get_config_summary())
        
        print("Initializing components...")
        
        self.tracker = HandTracker(
            model_complexity=settings.MODEL_COMPLEXITY,
            min_detection_confidence=settings.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=settings.MIN_TRACKING_CONFIDENCE,
            downscale_factor=settings.DOWNSCALE_FACTOR
        )
        
        self.coord_processor = CoordinateProcessor(
            screen_width=1920,
            screen_height=1080,
            smoothing_factor=settings.SMOOTHING_FACTOR
        )
        
        self.pinch_detector = PinchDetector(
            click_threshold=settings.CLICK_THRESHOLD,
            release_threshold=settings.RELEASE_THRESHOLD
        )
        
        self.perf = PerformanceMonitor(window_size=30)
        
        print("All components initialized\n")
    
    def run(self):
        """Run the test."""
        print("Controls:")
        print("  q - Quit")
        print("  s - Toggle stats display")
        print("="*70 + "\n")
        
        if not self.tracker.start_camera(
            camera_index=settings.CAMERA_INDEX,
            width=settings.CAMERA_WIDTH,
            height=settings.CAMERA_HEIGHT,
            fps=settings.CAMERA_FPS
        ):
            print("Failed to start camera")
            return
        
        print("Camera running - Move your hand!\n")
        
        frame_count = 0
        show_stats = settings.SHOW_PERFORMANCE_STATS
        
        while self.tracker.running:
            self.perf.tick()
            frame_count += 1
            
            ret, display_frame, process_frame = self.tracker.read_frame()
            if not ret:
                break
            
            results = self.tracker.detect_hands(process_frame)
            
            if results and results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                
                x, y = self.tracker.get_index_finger_position(hand_landmarks)
                
                screen_x, screen_y = self.coord_processor.process(
                    x, y, 
                    sensitivity=settings.DEFAULT_SENSITIVITY
                )
                
                pinch_dist = self.tracker.get_thumb_index_distance(hand_landmarks)
                is_pinching, just_clicked = self.pinch_detector.update(pinch_dist)
                
                scale = 1.0 / settings.DOWNSCALE_FACTOR
                self.tracker.draw_minimal_landmarks(
                    display_frame,
                    hand_landmarks,
                    scale,
                    scale
                )
                
                info_y = 30
                cv2.putText(display_frame, 
                           f"Hand: ({x:.2f}, {y:.2f})", 
                           (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.5, (0, 255, 0), 1)
                
                info_y += 25
                cv2.putText(display_frame, 
                           f"Screen: ({screen_x}, {screen_y})", 
                           (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.5, (0, 255, 0), 1)
                
                info_y += 25
                cv2.putText(display_frame, 
                           f"Pinch: {pinch_dist:.3f}", 
                           (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.5, (0, 255, 0), 1)
                
                if just_clicked:
                    cv2.putText(display_frame, 
                               "CLICK", 
                               (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 
                               1.0, (0, 0, 255), 2)
                elif is_pinching:
                    cv2.putText(display_frame, 
                               "Pinching...", 
                               (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.7, (0, 165, 255), 2)
            else:
                cv2.putText(display_frame, 
                           "No hand detected", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.6, (0, 0, 255), 1)
            
            if show_stats:
                fps = self.perf.get_fps()
                latency = self.perf.get_latency_ms()
                
                h = display_frame.shape[0]
                
                if latency < 20:
                    color = (0, 255, 0)
                elif latency < 30:
                    color = (0, 255, 255)
                else:
                    color = (0, 0, 255)
                
                cv2.putText(display_frame, 
                           f"FPS: {fps:.1f}", 
                           (10, h - 45), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.6, (255, 255, 0), 2)
                cv2.putText(display_frame, 
                           f"Latency: {latency:.1f}ms", 
                           (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.6, color, 2)
            
            cv2.imshow("Hand Tracker", display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\nUser quit")
                break
            elif key == ord('s'):
                show_stats = not show_stats
                print(f"Stats: {'ON' if show_stats else 'OFF'}")
        
        self.tracker.cleanup()
        
        print("\n" + "="*70)
        print("Final Performance Stats")
        print("="*70)
        print(f"Average FPS: {self.perf.get_fps():.1f}")
        print(f"Average Latency: {self.perf.get_latency_ms():.1f}ms")
        print(f"Total frames: {frame_count}")
        
        latency = self.perf.get_latency_ms()
        if latency < 20:
            print("Target achieved: < 20ms latency!")
        elif latency < 25:
            print("Close to target: < 25ms latency")
        else:
            print("Target not achieved. Check camera settings.")
        print("="*70)


def main():
    """Main entry point."""
    demo = OptimizedHandTrackerDemo()
    
    try:
        demo.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()