#!/usr/bin/env python3
"""Hand gesture mouse control test.

Controls:
    SPACE: Toggle mouse control
    q: Quit
    +/-: Adjust sensitivity
    s/f: Adjust smoothing
"""

import sys
import traceback

import cv2

from src.hand_tracker import HandTracker, PerformanceMonitor
from src.mouse_controller import MouseController


def print_controls():
    """Display control instructions."""
    sep = "=" * 60
    print(f"\n{sep}")
    print("CONTROLS")
    print(sep)
    print("  SPACE  - Toggle mouse control")
    print("  q      - Quit")
    print("  +/-    - Sensitivity")
    print("  s/f    - Smoothing")
    print(f"{sep}\n")


def main():
    """Run hand gesture mouse control."""
    print("=" * 60)
    print("HAND GESTURE MOUSE CONTROL")
    print("=" * 60)
    
    # Initialize with lower resolution for better performance
    tracker = HandTracker(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        downscale_factor=0.5  # Lower resolution
    )
    
    mouse = MouseController(
        sensitivity=2.0,
        smoothing_factor=0.3,
        deadzone_x=0.15,  # Bigger horizontal deadzone
        deadzone_y=0.15   # Bigger vertical deadzone
    )
    perf = PerformanceMonitor()
    
    print_controls()
    
    # Start camera with minimal resolution
    if not tracker.start_camera(camera_index=0, width=320, height=240, fps=30):
        print("Failed to start camera!")
        return
    
    print("Camera started - move your thumb to control mouse\n")
    
    try:
        while tracker.running:
            perf.tick()
            
            ret, display_frame, process_frame = tracker.read_frame()
            if not ret:
                break
            
            results = tracker.detect_hands(process_frame)
            
            # Process detected hand
            if results and results.multi_hand_landmarks:
                hand = results.multi_hand_landmarks[0]
                
                # Get thumb position
                thumb = hand.landmark[4]
                thumb_x, thumb_y = thumb.x, thumb.y
                pinch_dist = tracker.get_thumb_index_distance(hand)
                
                # Control mouse
                clicked = False
                if mouse.enabled:
                    mouse.move_mouse(thumb_x, thumb_y)
                    clicked = mouse.handle_click(pinch_dist)
                
                # Minimal visual feedback
                scale = 1.0 / tracker.downscale_factor
                tracker.draw_minimal_landmarks(display_frame, hand, scale, scale)
                
                # Status overlay - larger text for small window
                cv2.putText(display_frame, f"Thumb: {thumb_x:.2f}, {thumb_y:.2f}", 
                           (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                cv2.putText(display_frame, f"Pinch: {pinch_dist:.3f}", 
                           (5, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                
                if clicked or mouse.is_clicking:
                    cv2.putText(display_frame, "CLICK!", 
                               (5, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            else:
                cv2.putText(display_frame, "No hand", 
                           (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            # Bottom status bar
            h, w = display_frame.shape[:2]
            status = "ON" if mouse.enabled else "OFF"
            color = (0, 255, 0) if mouse.enabled else (0, 0, 255)
            
            cv2.putText(display_frame, f"Mouse: {status}", 
                       (5, h - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            cv2.putText(display_frame, f"Sens: {mouse.sensitivity:.1f} | Smooth: {mouse.smoothing_factor:.2f}", 
                       (5, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
            cv2.putText(display_frame, f"FPS: {perf.get_fps():.0f}", 
                       (5, h - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 0), 1)
            
            cv2.imshow("Hand Control", display_frame)
            
            # Handle keyboard
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord(' '):
                mouse.toggle_enabled()
                print(f"Mouse control: {'ENABLED' if mouse.enabled else 'DISABLED'}")
            elif key in (ord('+'), ord('=')):
                mouse.sensitivity = min(3.0, mouse.sensitivity + 0.1)
                print(f"Sensitivity: {mouse.sensitivity:.1f}")
            elif key == ord('-'):
                mouse.sensitivity = max(0.5, mouse.sensitivity - 0.1)
                print(f"Sensitivity: {mouse.sensitivity:.1f}")
            elif key == ord('s'):
                mouse.smoothing_factor = max(0.1, mouse.smoothing_factor - 0.05)
                print(f"Smoothing: {mouse.smoothing_factor:.2f}")
            elif key == ord('f'):
                mouse.smoothing_factor = min(0.5, mouse.smoothing_factor + 0.05)
                print(f"Smoothing: {mouse.smoothing_factor:.2f}")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        traceback.print_exc()
    finally:
        tracker.cleanup()
        print(f"\nFinal FPS: {perf.get_fps():.1f}")
        print("=" * 60)


if __name__ == "__main__":
    main()