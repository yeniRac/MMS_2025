"""Main application entry point with camera feed display."""

import cv2
import mediapipe as mp
from config.settings import Config
from src.hand_tracker import HandTracker
from src.mouse_controller import MouseController
from src.gui import StatusGUI

def draw_hand_landmarks(frame, hand_landmarks):
    """Draw hand landmarks and connections on frame."""
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    
    # Draw landmarks and connections
    mp_drawing.draw_landmarks(
        frame,
        hand_landmarks,
        mp_hands.HAND_CONNECTIONS,
        mp_drawing_styles.get_default_hand_landmarks_style(),
        mp_drawing_styles.get_default_hand_connections_style()
    )
    
    return frame

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
    print("  Hold VERY tight pinch 5 seconds = Toggle (gesture)")
    print("  Q = Quit")
    print("  Click and drag sliders in GUI to adjust settings")
    print("  Click 'Show Camera Feed' button to view tracking")
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
                
                # Check for toggle gesture first (before other actions)
                if mouse.check_toggle_gesture(pinch_distance):
                    mouse.toggle()
                    status = "ENABLED" if mouse.enabled else "DISABLED"
                    print(f"\n{'='*50}")
                    print(f"Mouse control TOGGLED by gesture: {status}")
                    print(f"{'='*50}\n")
                    # Small delay to prevent accidental actions after toggle
                    cv2.waitKey(500)
                else:
                    # Only do normal mouse actions if not toggling
                    mouse.move_cursor(hand)
                    mouse.handle_click(pinch_distance)
            else:
                pinch_distance = 0.0
            
            # Display camera feed if enabled
            if gui.show_camera:
                camera_frame = frame.copy()
                
                # Draw hand landmarks if detected
                if hand:
                    camera_frame = draw_hand_landmarks(camera_frame, hand)
                
                # Show camera feed window
                cv2.imshow(gui.camera_window_name, camera_frame)
            
            # Draw GUI (pass config values via gui object)
            gui_img = gui.draw_status(
                mouse.enabled,
                hand is not None,
                pinch_distance,
                mouse._is_clicking,
                mouse.toggle_progress
            )
            cv2.imshow(gui.window_name, gui_img)
            
            # Handle window events (works even when window is not focused)
            key = gui.handle_window_events()
            
            if key == ord('q'):
                break
            elif key == ord('m'):
                mouse.toggle()
                status = "ENABLED" if mouse.enabled else "DISABLED"
                print(f"\nMouse control: {status}\n")
    
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