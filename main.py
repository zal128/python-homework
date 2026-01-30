import cv2
import time
import argparse
import sys
import os
import queue
import threading
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import *
from gesture_controller import HandTracker, GestureRecognizer, ActionExecutor, FPSCounter
from gesture_controller.utils import is_browser_active, get_browser_name, is_music_playing, get_music_app_name
from gesture_controller.status_window import start_status_window

def load_user_settings():
    """加载用户设置"""
    settings_file = "user_settings.json"
    default_settings = {
        "mouse_sensitivity": 8.0,
        "volume_step": 0.05,
        "brightness_step": 10,
        "gesture_cooldown": 0.5,
        "scroll_speed": 5,
        "ui_primary_color": (0, 150, 255),
        "ui_background_color": (30, 30, 40)
    }
    
    try:
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                user_settings = json.load(f)
                # 合并设置，保留用户自定义的，使用默认值补充缺失的
                for key, value in default_settings.items():
                    if key not in user_settings:
                        user_settings[key] = value
                return user_settings
    except Exception as e:
        print(f"加载用户设置失败: {e}")
    
    return default_settings

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", type=int, default=CAMERA_INDEX)
    parser.add_argument("--width", type=int, default=CAMERA_WIDTH)
    parser.add_argument("--height", type=int, default=CAMERA_HEIGHT)
    parser.add_argument("--no-viz", action="store_true")
    args = parser.parse_args()
    
    # 加载用户设置
    user_settings = load_user_settings()
    
    print("=" * 60)
    print("手势控制系统")
    print("=" * 60)
    print("初始化组件...")
    print(f"  鼠标灵敏度: {user_settings['mouse_sensitivity']}")
    print(f"  音量调节步长: {user_settings['volume_step']}")
    print(f"  亮度调节步长: {user_settings['brightness_step']}")
    print(f"  手势冷却时间: {user_settings['gesture_cooldown']}秒")
    
    try:
        hand_tracker = HandTracker(
            max_num_hands=MAX_NUM_HANDS,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE
        )
        
        gesture_recognizer = GestureRecognizer()
        action_executor = ActionExecutor()
        fps_counter = FPSCounter()
        
        # 应用用户设置
        action_executor.set_mouse_sensitivity(user_settings['mouse_sensitivity'])
        action_executor.set_volume_step(user_settings['volume_step'])
        action_executor.set_brightness_step(user_settings['brightness_step'])
        action_executor.set_scroll_speed(user_settings['scroll_speed'])
        gesture_recognizer.set_cooldown(user_settings['gesture_cooldown'])
        
        print("✓ 组件初始化成功")
        print(f"  音量控制: {'可用' if action_executor.volume_interface else '不可用'}")
        
        # 启动状态悬浮窗
        print("\n启动状态窗口...")
        status_queue = queue.Queue()
        status_thread = threading.Thread(target=start_status_window, args=(status_queue,), daemon=True)
        status_thread.start()
        print("✓ 状态窗口已启动 (右键关闭)")
        
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
    
    print(f"✓ 摄像头已打开: {args.camera}")
    print(f"  分辨率: {args.width}x{args.height}")
    
    print("\n" + "=" * 60)
    print("Control Instructions:")
    print("=" * 60)
    instructions = gesture_recognizer.get_gesture_info()
    for instruction in instructions:
        if instruction:
            print(f"  {instruction}")
    print("=" * 60)
    
    print("\n启动主循环...")
    print("(按 'q' 退出, 'r' 重置)")
    print("浏览器自动检测: 已启用")
    print("状态窗口: 右键关闭, 拖动移动")
    
    # 初始化状态更新相关变量
    main.last_status_update = 0
    
    # 浏览器检测相关变量
    last_browser_check = 0
    browser_check_interval = 2.0  # 每2秒检查一次浏览器
    last_known_mode = "MAIN"  # 记录上一次的非自动切换的模式
    
    # 音乐检测相关变量
    last_music_check = 0
    music_check_interval = 1.0  # 每1秒检查一次音乐播放状态
    music_mode_override = False  # 音乐模式是否覆盖其他模式
    
    try:
        while True:
            current_time = time.time()
            music_playing = False
            music_app_name = None
            
            # 定期检测音乐播放状态（优先级最高）
            if current_time - last_music_check >= music_check_interval:
                last_music_check = current_time
                
                music_playing, music_app_name = is_music_playing()
                current_mode = gesture_recognizer.mode
                
                if music_playing and current_mode != "MUSIC":
                    # 检测到音乐播放且当前不在音乐模式，自动切换到音乐模式
                    if not music_mode_override:  # 如果当前不是被音乐模式覆盖的状态
                        last_known_mode = current_mode  # 保存当前模式
                        music_mode_override = True
                    gesture_recognizer.toggle_mode(target_mode="MUSIC")
                    print(f"\n[自动] 检测到音乐: {music_app_name}")
                    print("[自动] 切换到 音乐模式 (覆盖)")
                    
            elif not music_playing and current_mode == "MUSIC":
                # 音乐停止播放且当前在音乐模式，恢复之前模式
                music_mode_override = False
                gesture_recognizer.toggle_mode(target_mode=last_known_mode)
                print(f"\n[自动] 音乐已停止")
                print(f"[自动] 恢复到 {last_known_mode} 模式")
                last_known_mode = "MAIN"  # 重置
            
            # 只有在非音乐模式时才检测浏览器（音乐模式优先级最高）
            if not music_mode_override:
                # 定期检测浏览器活动状态
                if current_time - last_browser_check >= browser_check_interval:
                    last_browser_check = current_time
                    
                    browser_active = is_browser_active()
                    current_mode = gesture_recognizer.mode
                    
                    if browser_active and current_mode != "BROWSER":
                        # 检测到浏览器且当前不在浏览器模式，自动切换
                        last_known_mode = current_mode  # 保存当前模式
                        gesture_recognizer.toggle_mode(target_mode="BROWSER")
                        browser_name = get_browser_name()
                        print(f"\n[自动] 检测到浏览器: {browser_name}")
                        print("[自动] 切换到 浏览器模式")
                        
                    elif not browser_active and current_mode == "BROWSER":
                        # 浏览器失去焦点且当前在浏览器模式，停止滚动并恢复之前模式
                        action_executor._stop_browser_scroll()
                        gesture_recognizer.toggle_mode(target_mode=last_known_mode)
                        print(f"\n[自动] 浏览器失去焦点")
                        print(f"[自动] 恢复到 {last_known_mode} 模式")
                        last_known_mode = "MAIN"  # 重置
            success, frame = cap.read()
            if not success:
                print("Failed to read frame from camera")
                break
            
            frame = cv2.flip(frame, 1)
            hand_landmarks_list, annotated_frame = hand_tracker.process_frame(frame)
            
            current_gesture = None
            current_action = None
            
            # 更新浏览器滚动（在浏览器模式下持续调用）
            if gesture_recognizer.mode == "BROWSER":
                action_executor.update_browser_scroll()
            else:
                # 不在浏览器模式时停止滚动
                action_executor._stop_browser_scroll()
            
            if hand_landmarks_list:
                landmarks = hand_landmarks_list[0]
                finger_states = hand_tracker.get_finger_states(landmarks)
                
                # 记录手部位置用于轨迹追踪（调试用）
                gesture_recognizer.record_hand_position(landmarks)
                
                # 识别动态手势（调试用，不用于控制）
                dynamic_gesture = gesture_recognizer.recognize_dynamic_gesture(landmarks)
                if dynamic_gesture and DEBUG_MODE:
                    print(f"Dynamic gesture detected: {dynamic_gesture}")
                
                if finger_states:
                    current_gesture, is_new_gesture = gesture_recognizer.recognize_gesture(finger_states)
                    
                    if current_gesture:
                        current_action = gesture_recognizer.get_gesture_action(current_gesture)
                        
                        if current_action:
                            # 检测是否需要冻结鼠标（手势切换时）- 排除mouse_move和mouse_drag
                            if (gesture_recognizer.mode == "MOUSE" and 
                                is_new_gesture and 
                                current_action not in ["mouse_move", "mouse_drag"]):
                                # 切换到点击/双击等手势时冻结鼠标1秒，避免切换姿势时鼠标移动
                                action_executor.mouse_freeze_until = time.time() + 1.0
                            
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
                            elif gesture_recognizer.mode == "BROWSER":
                                # 浏览器模式：只在新手势时执行（除了滚动）
                                if is_new_gesture:
                                    # 停止之前的滚动
                                    action_executor._stop_browser_scroll()
                                    action_executor.execute_action(current_action)
                            elif is_new_gesture:
                                # 主模式：只在新手势时执行
                                action_executor.execute_action(current_action)
                                
                                # 如果是切换模式
                                if current_action == "toggle_mode":
                                    gesture_recognizer.toggle_mode(current_gesture)
            else:
                # 没有检测到手，停止拖拽并清空轨迹
                if gesture_recognizer.mode == "MOUSE" and action_executor.mouse_last_action == "mouse_drag":
                    action_executor.stop_drag()
                
                # 在浏览器模式下，没有检测到手时停止滚动
                if gesture_recognizer.mode == "BROWSER":
                    action_executor._stop_browser_scroll()
                
                # 清空手部运动轨迹
                gesture_recognizer.clear_trajectory()
            
            fps_counter.update()
            
            # 更新悬浮窗状态（每0.5秒更新一次）
            if current_time - getattr(main, 'last_status_update', 0) >= 0.5:
                main.last_status_update = current_time
                
                # 获取当前状态
                status = action_executor.get_status()
                
                # 构建状态信息
                status_info = {
                    'mode': gesture_recognizer.mode,
                    'gesture': current_gesture if current_gesture else '-',
                    'volume': status.get('current_volume', '-'),
                    'brightness': status.get('current_brightness', '-'),
                    'music_app': music_app_name if music_playing else None
                }
                
                # 发送到悬浮窗（非阻塞）
                try:
                    status_queue.put_nowait(status_info)
                except queue.Full:
                    pass  # 如果队列满了，跳过这次更新
            
            if not args.no_viz:
                # 只显示原始的摄像头画面，不添加任何UI元素
                cv2.imshow("Gesture Control System", annotated_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("用户请求退出")
                break
            elif key == ord('r'):
                print("重置识别器...")
                gesture_recognizer.reset()
            elif key == ord('s'):
                print("手动截图...")
                action_executor.execute_action("screenshot")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user (Ctrl+C)")
    
    except Exception as e:
        print(f"\nError in main loop: {e}")
        if DEBUG_MODE:
            import traceback
            traceback.print_exc()
    
    finally:
        print("\n清理资源...")
        
        if 'cap' in locals():
            cap.release()
            print("✓ 摄像头已释放")
        
        if 'hand_tracker' in locals():
            hand_tracker.release()
            print("✓ 手部追踪器已释放")
        
        cv2.destroyAllWindows()
        print("✓ 窗口已关闭")
        
        if 'action_executor' in locals():
            print("\n最终状态:")
            print("-" * 30)
            status = action_executor.get_status()
            for key, value in status.items():
                print(f"  {key}: {value}")
        
        print("\n程序已成功终止")


if __name__ == "__main__":
    import sys
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required")
        sys.exit(1)
    
    main()