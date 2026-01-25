import cv2
import time
import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import *
from gesture_controller import HandTracker, GestureRecognizer, ActionExecutor, FPSCounter, draw_gesture_info, draw_instructions

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", type=int, default=CAMERA_INDEX)
    parser.add_argument("--width", type=int, default=CAMERA_WIDTH)
    parser.add_argument("--height", type=int, default=CAMERA_HEIGHT)
    parser.add_argument("--no-viz", action="store_true")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Gesture Control System")
    print("=" * 60)
    print("Initializing components...")
    
    try:
        hand_tracker = HandTracker(
            max_num_hands=MAX_NUM_HANDS,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE
        )
        
        gesture_recognizer = GestureRecognizer()
        action_executor = ActionExecutor()
        fps_counter = FPSCounter()
        
        print("✓ Components initialized successfully")
        print(f"  Volume control: {'Available' if action_executor.volume_interface else 'Not available'}")
        
    except Exception as e:
        print(f"✗ Failed to initialize components: {e}")
        return
    
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"✗ Failed to open camera {args.camera}")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print(f"✓ Camera opened: {args.camera}")
    print(f"  Resolution: {args.width}x{args.height}")
    
    print("\n" + "=" * 60)
    print("Control Instructions:")
    print("=" * 60)
    instructions = gesture_recognizer.get_gesture_info()
    for instruction in instructions:
        if instruction:
            print(f"  {instruction}")
    print("=" * 60)
    
    print("\nStarting main loop...")
    print("(Press 'q' to quit, 'r' to reset)")
    
    try:
        while True:
            success, frame = cap.read()
            if not success:
                print("Failed to read frame from camera")
                break
            
            frame = cv2.flip(frame, 1)
            hand_landmarks_list, annotated_frame = hand_tracker.process_frame(frame)
            
            current_gesture = None
            current_action = None
            
            if hand_landmarks_list:
                landmarks = hand_landmarks_list[0]
                finger_states = hand_tracker.get_finger_states(landmarks)
                
                if finger_states:
                    current_gesture, is_new_gesture = gesture_recognizer.recognize_gesture(finger_states)
                    
                    if current_gesture:
                        current_action = gesture_recognizer.get_gesture_action(current_gesture)
                        
                        if current_action:
                            # 检测是否需要冻结鼠标（手势切换时）
                            if gesture_recognizer.mode == "MOUSE" and is_new_gesture and current_action != "mouse_move":
                                # 从移动切换到其他手势（点击、双击等）时，冻结鼠标0.5秒
                                action_executor.mouse_freeze_until = time.time() + 0.5
                            
                            # 鼠标模式特殊处理
                            if gesture_recognizer.mode == "MOUSE":
                                if current_action == "mouse_move":
                                    # 鼠标移动持续执行（不需要新手势）
                                    action_executor.execute_action(current_action, landmarks=landmarks)
                                elif current_action == "mouse_drag":
                                    # 拖拽持续执行
                                    action_executor.execute_action(current_action, landmarks=landmarks)
                                elif is_new_gesture:
                                    # 其他鼠标动作只在新手势时执行
                                    action_executor.execute_action(current_action)
                                    
                                    # 如果是切换模式（在鼠标模式下也需要切换）
                                    if current_action == "toggle_mode":
                                        gesture_recognizer.toggle_mode(current_gesture)
                            elif is_new_gesture:
                                # 主模式：只在新手势时执行
                                action_executor.execute_action(current_action)
                                
                                # 如果是切换模式
                                if current_action == "toggle_mode":
                                    gesture_recognizer.toggle_mode(current_gesture)
            else:
                # 没有检测到手，停止拖拽
                if gesture_recognizer.mode == "MOUSE" and action_executor.mouse_last_action == "mouse_drag":
                    action_executor.stop_drag()
            
            fps = fps_counter.update()
            
            if not args.no_viz:
                fps_counter.draw(annotated_frame, position=(10, 30))
                
                if current_gesture and current_action:
                    draw_gesture_info(
                        annotated_frame, 
                        current_gesture, 
                        current_action,
                        position=(10, 60),
                        font_scale=FONT_SCALE,
                        color=FONT_COLOR,
                        thickness=FONT_THICKNESS
                    )
                
                instructions = gesture_recognizer.get_gesture_info()
                draw_instructions(
                    annotated_frame,
                    instructions,
                    start_position=(10, 450),
                    font_scale=0.6,
                    color=(200, 200, 200),
                    thickness=1
                )
                
                if DEBUG_MODE:
                    status = action_executor.get_status()
                    y_offset = 0
                    for key, value in status.items():
                        if key in ['current_volume', 'current_brightness']:
                            text = f"{key}: {value}"
                            cv2.putText(
                                annotated_frame, text,
                                (annotated_frame.shape[1] - 200, 30 + y_offset),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 100), 1
                            )
                            y_offset += 20
                
                cv2.imshow("Gesture Control System", annotated_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("Quit requested by user")
                break
            elif key == ord('r'):
                print("Resetting recognizer...")
                gesture_recognizer.reset()
            elif key == ord('s'):
                print("Manual screenshot...")
                action_executor.execute_action("screenshot")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user (Ctrl+C)")
    
    except Exception as e:
        print(f"\nError in main loop: {e}")
        if DEBUG_MODE:
            import traceback
            traceback.print_exc()
    
    finally:
        print("\nCleaning up...")
        
        if 'cap' in locals():
            cap.release()
            print("✓ Camera released")
        
        if 'hand_tracker' in locals():
            hand_tracker.release()
            print("✓ Hand tracker released")
        
        cv2.destroyAllWindows()
        print("✓ Windows closed")
        
        if 'action_executor' in locals():
            print("\nFinal Status:")
            print("-" * 30)
            status = action_executor.get_status()
            for key, value in status.items():
                print(f"  {key}: {value}")
        
        print("\nProgram terminated successfully")


if __name__ == "__main__":
    import sys
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required")
        sys.exit(1)
    
    main()