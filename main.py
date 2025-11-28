"""Main application entry point with camera feed display."""

import cv2
import mediapipe as mp
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
    print("  Spread fingers moderately for 2 seconds = Toggle (gesture)")
    print("  Q = Quit")
    print("  Click and drag sliders in GUI to adjust settings")
    print("  Double-click sliders to reset to defaults")
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
                
                # Draw only thumb and index landmarks for clarity
                if hand:
                    thumb_pos = hand.landmark[4]
                    index_pos = hand.landmark[8]
                    
                    h, w = camera_frame.shape[:2]
                    thumb_px = (int(thumb_pos.x * w), int(thumb_pos.y * h))
                    index_px = (int(index_pos.x * w), int(index_pos.y * h))
                    
                    # Draw smaller circles for thumb and index
                    circle_color = (0, 255, 0) if mouse._is_clicking else (66, 133, 244)
                    cv2.circle(camera_frame, thumb_px, 6, circle_color, -1)  # REDUCED from 12 to 6
                    cv2.circle(camera_frame, index_px, 6, circle_color, -1)  # REDUCED from 12 to 6
                    cv2.circle(camera_frame, thumb_px, 6, (255, 255, 255), 1)  # REDUCED border thickness
                    cv2.circle(camera_frame, index_px, 6, (255, 255, 255), 1)  # REDUCED border thickness
                    
                    # Draw thinner line between them
                    line_color = (0, 255, 0) if mouse._is_clicking else (66, 133, 244)
                    cv2.line(camera_frame, thumb_px, index_px, line_color, 2)  # REDUCED from 3 to 2
                    
                    # Draw status info
                    info_y = 30
                    
                    # Click indicator
                    if mouse._is_clicking:
                        cv2.putText(camera_frame, "CLICKING!", (10, info_y),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
                        info_y += 35
                    
                    # Distance indicator
                    distance_text = f"Distance: {pinch_distance:.3f}"
                    cv2.putText(camera_frame, distance_text, (10, info_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                    info_y += 25
                    
                    # Threshold indicator
                    threshold_text = f"Threshold: {config.CLICK_THRESHOLD:.3f}"
                    cv2.putText(camera_frame, threshold_text, (10, info_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1, cv2.LINE_AA)
                    
                    # Velocity indicator (for debugging)
                    if mouse._distance_velocity is not None:
                        velocity_text = f"Velocity: {mouse._distance_velocity:.4f}"
                        velocity_color = (0, 255, 255) if mouse._distance_velocity < -0.01 else (200, 200, 200)
                        cv2.putText(camera_frame, velocity_text, (10, h - 20),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, velocity_color, 1, cv2.LINE_AA)
                
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