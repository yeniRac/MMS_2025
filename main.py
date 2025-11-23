"""Main application entry point."""

import cv2
from config.settings import Config
from src.hand_tracker import HandTracker
from src.mouse_controller import MouseController
from src.gui import StatusGUI

def main():
    """Run hand gesture mouse control."""
    config = Config()
    
    # Initialize components
    tracker = HandTracker(config)
    mouse = MouseController(config)
    gui = StatusGUI(config)
    
    # Start camera
    if not tracker.start():
        print("ERROR: Failed to start camera!")
        return
    
    # Create GUI
    gui.create_window()
    
    print("=" * 50)
    print("HAND GESTURE MOUSE CONTROL")
    print("=" * 50)
    print("\nControls:")
    print("  M = Toggle mouse control (keyboard)")
    print("  Hold tight pinch 5 seconds = Toggle mouse control (gesture)")
    print("  Q = Quit")
    print("  +/- = Adjust sensitivity")
    print("\nStarting...\n")
    
    # Track pinch state
    pinch_distance = 0.0
    
    try:
        while True:
            # Update FPS
            gui.update_fps()
            
            # Read frame
            ret, frame = tracker.read_frame()
            if not ret:
                break
            
            # Detect hand
            hand = tracker.detect_hand(frame)
            
            # Process hand
            if hand:
                pinch_distance = tracker.get_pinch_distance(hand)
                
                # Check for toggle gesture first
                if mouse.check_toggle_gesture(pinch_distance):
                    mouse.toggle()
                    status = "ENABLED" if mouse.enabled else "DISABLED"
                    print(f"\n{'='*50}")
                    print(f"Mouse control TOGGLED by gesture: {status}")
                    print(f"{'='*50}\n")
                
                # Then handle normal cursor and click
                mouse.move_cursor(hand)
                mouse.handle_click(pinch_distance)
            else:
                pinch_distance = 0.0
            
            # Draw GUI
            gui_img = gui.draw_status(
                mouse.enabled,
                hand is not None,
                config.DEFAULT_SENSITIVITY,
                config.SMOOTHING,
                pinch_distance,
                mouse._is_clicking,
                mouse.toggle_progress
            )
            cv2.imshow(gui.window_name, gui_img)
            
            # Handle keyboard
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('m'):
                mouse.toggle()
                status = "ENABLED" if mouse.enabled else "DISABLED"
                print(f"\nMouse control: {status}\n")
            elif key in (ord('+'), ord('=')):
                config.DEFAULT_SENSITIVITY = min(3.0, config.DEFAULT_SENSITIVITY + 0.1)
                print(f"\nSensitivity: {config.DEFAULT_SENSITIVITY:.1f}\n")
            elif key == ord('-'):
                config.DEFAULT_SENSITIVITY = max(0.5, config.DEFAULT_SENSITIVITY - 0.1)
                print(f"\nSensitivity: {config.DEFAULT_SENSITIVITY:.1f}\n")
    
    except KeyboardInterrupt:
        print("\nInterrupted")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tracker.cleanup()
        cv2.destroyAllWindows()
        print(f"\nFinal FPS: {gui.fps:.1f}")
        print("=" * 50)


if __name__ == "__main__":
    main()