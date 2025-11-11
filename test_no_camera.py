#!/usr/bin/env python3
"""Hand gesture mouse control - NO DISPLAY VERSION for maximum performance.

Controls:
    Press 'm' to toggle mouse control
    Press 'q' to quit
    Press '+' or '-' to adjust sensitivity
    Press 's' or 'f' to adjust smoothing
"""

import sys
import time
# import msvcrt if sys.platform == 'win32' else None

import cv2

from src.hand_tracker import HandTracker, PerformanceMonitor
from src.mouse_controller import MouseController


def get_key_non_blocking():
    """Get keyboard input without blocking (cross-platform)."""
    if sys.platform == 'win32':
        # Windows
        if msvcrt.kbhit():
            return msvcrt.getch().decode('utf-8', errors='ignore')
    else:
        # Unix/Linux/Mac
        import select
        import sys
        import tty
        import termios
        
        # Check if input is available
        if select.select([sys.stdin], [], [], 0)[0]:
            old_settings = termios.tcgetattr(sys.stdin)
            try:
                tty.setcbreak(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                return ch
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    return None


def print_status_line(mouse, perf, hand_detected, thumb_pos, pinch_dist, click_status):
    """Print live status line that updates in place."""
    status = "ON " if mouse.enabled else "OFF"
    hand = "✓" if hand_detected else "✗"
    click = "CLICK!" if click_status else "     "
    
    # Single line status with carriage return
    line = (f"\r[Mouse:{status}] Hand:{hand} | "
            f"({thumb_pos[0]:.2f},{thumb_pos[1]:.2f}) "
            f"Pinch:{pinch_dist:.3f} {click} | "
            f"{perf.get_fps():.0f}fps {perf.get_latency_ms():.0f}ms | "
            f"m=Toggle q=Quit +/-=Sens")
    
    # Write and flush
    sys.stdout.write(line)
    sys.stdout.flush()


def print_header():
    """Display header and instructions."""
    print("\n" + "=" * 70)
    print("HAND GESTURE MOUSE CONTROL - HIGH PERFORMANCE")
    print("=" * 70)
    print("\nKEYBOARD CONTROLS:")
    print("  m  = Toggle mouse control ON/OFF")
    print("  q  = Quit")
    print("  +  = Increase sensitivity")
    print("  -  = Decrease sensitivity")
    print("  s  = Less smoothing (more responsive)")
    print("  f  = More smoothing (more stable)")
    print("\n" + "=" * 70)
    print("Starting... Press 'm' to enable\n")


def main():
    """Run optimized hand gesture mouse control."""
    print_header()
    
    # Initialize
    tracker = HandTracker(
        model_complexity=0,
        min_detection_confidence=0.4,
        min_tracking_confidence=0.4,
        downscale_factor=0.5
    )
    
    mouse = MouseController(
        sensitivity=2.0,
        smoothing_factor=0.3,
        deadzone_x=0.15,
        deadzone_y=0.15
    )
    
    perf = PerformanceMonitor()
    
    # Start camera
    if not tracker.start_camera(camera_index=0, width=320, height=240, fps=60):
        print("ERROR: Failed to start camera!")
        return
    
    # Create minimal window for cv2.waitKey to work
    cv2.namedWindow('control', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('control', 1, 1)
    cv2.moveWindow('control', -100, -100)  # Move offscreen
    
    # State
    last_thumb_pos = (0.0, 0.0)
    last_pinch = 0.0
    hand_detected = False
    click_status = False
    
    try:
        while tracker.running:
            perf.tick()
            
            # Read frame
            ret, _, process_frame = tracker.read_frame()
            if not ret:
                break
            
            # Detect hands
            results = tracker.detect_hands(process_frame)
            
            # Process
            if results and results.multi_hand_landmarks:
                hand = results.multi_hand_landmarks[0]
                hand_detected = True
                
                thumb = hand.landmark[4]
                thumb_x, thumb_y = thumb.x, thumb.y
                pinch_dist = tracker.get_thumb_index_distance(hand)
                
                last_thumb_pos = (thumb_x, thumb_y)
                last_pinch = pinch_dist
                
                if mouse.enabled:
                    mouse.move_mouse(thumb_x, thumb_y)
                    mouse.handle_click(pinch_dist)
                    click_status = mouse.is_clicking
                else:
                    click_status = False
            else:
                hand_detected = False
                click_status = False
            
            # Update status line
            print_status_line(mouse, perf, hand_detected, last_thumb_pos, 
                            last_pinch, click_status)
            
            # Handle keyboard
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('m'):
                mouse.toggle_enabled()
                print(f"\n{'='*50}")
                print(f"Mouse control: {'ENABLED ✓' if mouse.enabled else 'DISABLED'}")
                print(f"{'='*50}\n")
            elif key in (ord('+'), ord('=')):
                mouse.sensitivity = min(3.0, mouse.sensitivity + 0.1)
                print(f"\nSensitivity: {mouse.sensitivity:.1f}\n")
            elif key == ord('-'):
                mouse.sensitivity = max(0.5, mouse.sensitivity - 0.1)
                print(f"\nSensitivity: {mouse.sensitivity:.1f}\n")
            elif key == ord('s'):
                mouse.smoothing_factor = max(0.1, mouse.smoothing_factor - 0.05)
                print(f"\nSmoothing: {mouse.smoothing_factor:.2f}\n")
            elif key == ord('f'):
                mouse.smoothing_factor = min(0.5, mouse.smoothing_factor + 0.05)
                print(f"\nSmoothing: {mouse.smoothing_factor:.2f}\n")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tracker.cleanup()
        print(f"\n{'='*70}")
        print(f"Final FPS: {perf.get_fps():.1f} | Latency: {perf.get_latency_ms():.1f}ms")
        print("="*70)


if __name__ == "__main__":
    main()