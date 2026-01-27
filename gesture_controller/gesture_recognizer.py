# -*- coding: utf-8 -*-
"""
手势识别模块
"""

import numpy as np
import time
import sys
import os
from collections import deque

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GESTURES, GESTURE_ACTIONS, MOUSE_GESTURE_ACTIONS, BROWSER_GESTURE_ACTIONS, MUSIC_GESTURE_ACTIONS, FINGER_STATE_THRESHOLD, GESTURE_COOLDOWN, BROWSER_GESTURE_COOLDOWN, MUSIC_GESTURE_COOLDOWN


class GestureRecognizer:
    """手势识别器"""
    
    def __init__(self):
        """初始化手势识别器"""
        self.gestures = GESTURES
        self.gesture_actions = GESTURE_ACTIONS
        self.mouse_gesture_actions = MOUSE_GESTURE_ACTIONS
        self.browser_gesture_actions = BROWSER_GESTURE_ACTIONS
        self.music_gesture_actions = MUSIC_GESTURE_ACTIONS
        self.last_gesture_time = 0
        self.cooldown = GESTURE_COOLDOWN
        self.browser_cooldown = BROWSER_GESTURE_COOLDOWN
        self.music_cooldown = MUSIC_GESTURE_COOLDOWN
        
        # 模式管理
        self.mode = "MAIN"  # MAIN: 主模式, MOUSE: 鼠标模式, BROWSER: 浏览器模式, MUSIC: 音乐模式
        
        # 用于平滑识别的队列
        self.gesture_history = deque(maxlen=5)
        self.current_gesture = None
        self.previous_gesture = None  # 记录上一次的确认手势
        
    def recognize_gesture(self, finger_states):
        """
        识别手势
        
        Args:
            finger_states: 手指状态列表 [拇指, 食指, 中指, 无名指, 小指]
            
        Returns:
            tuple: (识别到的手势名称, 是否是新手势变化)
        """
        if not finger_states:
            return None, False
        
        # 匹配手势
        recognized_gesture = None
        min_distance = float('inf')
        
        for gesture_name, gesture_states in self.gestures.items():
            distance = self._calculate_state_distance(finger_states, gesture_states)
            
            if distance < min_distance and distance < FINGER_STATE_THRESHOLD * 5:
                min_distance = distance
                recognized_gesture = gesture_name
        
        # 添加到历史记录
        if recognized_gesture:
            self.gesture_history.append(recognized_gesture)
            
            # 如果连续多次识别到相同手势，才确认
            if len(self.gesture_history) >= 3 and len(set(list(self.gesture_history)[-3:])) == 1:
                # 检查是否是新手势（与之前不同）
                is_new_gesture = (self.current_gesture != recognized_gesture)
                
                self.current_gesture = recognized_gesture
                
                current_time = time.time()
                
                # 鼠标模式下的ONE和PALM手势：持续返回，不受冷却限制（用于鼠标移动和退出）
                if self.mode == "MOUSE" and recognized_gesture in ["ONE", "PALM"]:
                    return recognized_gesture, is_new_gesture
                
                # 音量/亮度调节（1-4指）可以连续触发（冷却时间0.3秒）
                if self.mode == "MAIN" and recognized_gesture in ["ONE", "TWO", "THREE", "FOUR"]:
                    if current_time - self.last_gesture_time >= 0.3:  # 0.3秒冷却
                        self.last_gesture_time = current_time
                        return recognized_gesture, True
                
                # 浏览器模式手势：需要新手势才能触发（冷却时间0.5秒）
                elif self.mode == "BROWSER":
                    if is_new_gesture or (current_time - self.last_gesture_time >= self.cooldown):
                        self.last_gesture_time = current_time
                        return recognized_gesture, is_new_gesture
                
                # 音乐模式：只在新手势时触发（冷却时间0.3秒）
                elif self.mode == "MUSIC":
                    if is_new_gesture or (current_time - self.last_gesture_time >= self.music_cooldown):
                        self.last_gesture_time = current_time
                        return recognized_gesture, is_new_gesture
                
                # 其他手势（截图、切换模式）需要新手势才能触发
                elif is_new_gesture or (current_time - self.last_gesture_time >= self.cooldown):
                    self.last_gesture_time = current_time
                    return recognized_gesture, is_new_gesture
        else:
            self.gesture_history.clear()
            self.current_gesture = None
        
        return self.current_gesture, False
    
    def _calculate_state_distance(self, states1, states2):
        """
        计算两个手势状态的欧氏距离
        
        Args:
            states1: 手势状态1
            states2: 手势状态2
            
        Returns:
            float: 距离
        """
        if len(states1) != len(states2):
            return float('inf')
        
        return np.sqrt(sum((s1 - s2)**2 for s1, s2 in zip(states1, states2)))
    
    def get_gesture_action(self, gesture_name):
        """
        获取手势对应的动作（根据当前模式）
        
        Args:
            gesture_name: 手势名称
            
        Returns:
            str: 动作名称，如果没有映射返回None
        """
        if self.mode == "MUSIC":
            return self.music_gesture_actions.get(gesture_name)
        elif self.mode == "MOUSE":
            return self.mouse_gesture_actions.get(gesture_name)
        elif self.mode == "BROWSER":
            return self.browser_gesture_actions.get(gesture_name)
        else:
            return self.gesture_actions.get(gesture_name)
    
    def toggle_mode(self, current_gesture_name=None, target_mode=None):
        """切换模式"""
        if target_mode:
            # 直接切换到指定模式（用于浏览器自动切换）
            self.mode = target_mode
        elif self.mode == "MAIN":
            self.mode = "MOUSE"
        elif self.mode == "MOUSE":
            self.mode = "MAIN"
        elif self.mode == "BROWSER":
            self.mode = "MAIN"
        elif self.mode == "MUSIC":
            self.mode = "MAIN"
        
        # 打印模式切换信息
        self._print_mode_info()
        
        # 重置手势状态，但保留历史记录以便快速识别新手势
        # 设置当前手势为刚识别的手势，这样is_new_gesture在下次会是False
        self.current_gesture = current_gesture_name
        self.previous_gesture = None
        # 设置较长的冷却时间（1秒），确保用户有时间改变手势
        self.last_gesture_time = time.time() + 1.0
        return self.mode
    
    def _print_mode_info(self):
        """打印当前模式的信息"""
        print("\n" + "=" * 60)
        if self.mode == "MOUSE":
            print("Switched to MOUSE MODE")
            print("=" * 60)
            print("  ONE finger: Move mouse")
            print("  TWO fingers: Left click")
            print("  THREE fingers: Right click")
            print("  FOUR fingers: Double click")
            print("  FIST/PALM: Exit mouse mode")
            print("=" * 60)
        elif self.mode == "BROWSER":
            print("Switched to BROWSER MODE (Auto)")
            print("=" * 60)
            print("  ONE finger: Refresh (F5)")
            print("  TWO fingers: Back (Alt+Left)")
            print("  THREE fingers: Forward (Alt+Right)")
            print("  FOUR fingers: Reopen Tab (Ctrl+Shift+T)")
            print("  ROCK: Switch Tab (Ctrl+Tab)")
            print("  Thumbs Up👍: Scroll Up (Hold for continuous)")
            print("  Fist✊: Scroll Down (Hold for continuous)")
            print("  Auto-exit when browser loses focus")
            print("=" * 60)
        elif self.mode == "MUSIC":
            print("Switched to MUSIC MODE (Auto)")
            print("=" * 60)
            print("  ONE finger: Play/Pause (Alt+Ctrl+P)")
            print("  TWO fingers: Next track (Alt+Ctrl+Right)")
            print("  THREE fingers: Previous track (Alt+Ctrl+Left)")
            print("  FOUR fingers: Volume Up")
            print("  Fist: Volume Down")
            print("  Thumbs Up👍: Like song (Ctrl+Shift+L)")
            print("  PALM: Exit to main mode")
            print("  Auto-activate when music is playing")
            print("=" * 60)
        else:  # MAIN mode
            print("Switched to MAIN MODE")
            print("=" * 60)
            print("  ONE: Volume Up")
            print("  TWO: Volume Down")
            print("  THREE: Brightness Up")
            print("  FOUR: Brightness Down")
            print("  ROCK: Screenshot")
            print("  PALM: Switch to mouse mode")
            print("=" * 60)
    
    def get_gesture_info(self):
        """
        获取手势说明信息（根据当前模式）
        
        Returns:
            list: 手势说明列表
        """
        if self.mode == "MOUSE":
            info = [
                "MOUSE MODE:",
                "1 finger: Move cursor",
                "2 fingers: Left click",
                "3 fingers: Right click",
                "4 fingers: Double click",
                "",
                "EXIT: Make Fist (0 fingers) OR Palm (5 fingers)",
                "",
                "Press 'q' to quit",
                "Press 'r' to reset"
            ]
        elif self.mode == "BROWSER":
            info = [
                "BROWSER MODE (Auto):",
                "1 finger: Refresh (F5)",
                "2 fingers: Back (Alt+←)",
                "3 fingers: Forward (Alt+→)",
                "4 fingers: Reopen Tab (Ctrl+Shift+T)",
                "Rock: Switch Tab (Ctrl+Tab)",
                "Thumbs Up👍: Scroll Up (Hold)",
                "Fist✊: Scroll Down (Hold)",
                "",
                "Auto-exit when browser loses focus",
                "",
                "Press 'q' to quit",
                "Press 'r' to reset"
            ]
        elif self.mode == "MUSIC":
            info = [
                "MUSIC MODE (Auto):",
                "1 finger: Play/Pause",
                "2 fingers: Next track",
                "3 fingers: Previous track",
                "4 fingers: Volume Up",
                "Fist: Volume Down",
                "Thumbs Up👍: Like song",
                "Palm: Exit to main mode",
                "",
                "Auto-activate when music plays",
                "",
                "Press 'q' to quit",
                "Press 'r' to reset"
            ]
        else:
            info = [
                "MAIN MODE:",
                "1 finger: Volume Up",
                "2 fingers: Volume Down",
                "3 fingers: Brightness Up",
                "4 fingers: Brightness Down",
                "Fist (0 fingers): Screenshot",
                "",
                "MOUSE MODE: Open Palm (5 fingers)",
                "",
                "Press 'q' to quit",
                "Press 'r' to reset"
            ]
        return info
    
    def reset(self):
        """重置识别器状态"""
        self.gesture_history.clear()
        self.current_gesture = None
        self.previous_gesture = None
        self.last_gesture_time = 0
        
        # 新增：清空轨迹历史
        if hasattr(self, 'trajectory_history'):
            self.trajectory_history.clear()
        if hasattr(self, 'last_hand_position'):
            self.last_hand_position = None
    
    def record_hand_position(self, landmarks):
        """
        记录手部位置，用于轨迹追踪
        
        Args:
            landmarks: 手部关键点坐标列表
        """
        if not landmarks or len(landmarks) < 9:  # 需要至少有关键点9（食指指尖）
            self.last_hand_position = None
            return
        
        # 使用食指指尖（landmark 8）作为手部位置的参考点
        index_finger_tip = landmarks[8]
        x, y = index_finger_tip[0], index_finger_tip[1]
        timestamp = time.time()
        
        # 记录位置和时间戳
        if not hasattr(self, 'trajectory_history'):
            self.trajectory_history = deque(maxlen=10)
        
        self.trajectory_history.append({
            'x': x,
            'y': y,
            'time': timestamp
        })
        
        self.last_hand_position = (x, y, timestamp)
    
    def analyze_trajectory(self):
        """
        分析手部运动轨迹，识别动态手势
        
        Returns:
            dict: 轨迹分析结果，包含方向和距离等信息
        """
        if not hasattr(self, 'trajectory_history') or len(self.trajectory_history) < 5:
            return None
        
        # 计算总位移
        start_pos = self.trajectory_history[0]
        end_pos = self.trajectory_history[-1]
        
        delta_x = end_pos['x'] - start_pos['x']
        delta_y = end_pos['y'] - start_pos['y']
        delta_time = end_pos['time'] - start_pos['time']
        
        # 计算距离
        distance = np.sqrt(delta_x**2 + delta_y**2)
        
        # 判断方向
        direction = None
        if abs(delta_x) > abs(delta_y):
            # 水平移动为主
            if delta_x > 30:  # 向右移动超过30像素
                direction = "RIGHT"
            elif delta_x < -30:  # 向左移动超过30像素
                direction = "LEFT"
        else:
            # 垂直移动为主
            if delta_y > 30:  # 向下移动超过30像素
                direction = "DOWN"
            elif delta_y < -30:  # 向上移动超过30像素
                direction = "UP"
        
        return {
            'direction': direction,
            'distance': distance,
            'delta_x': delta_x,
            'delta_y': delta_y,
            'duration': delta_time
        }
    
    def recognize_dynamic_gesture(self, landmarks):
        """
        识别动态手势（基于运动轨迹）
        
        Args:
            landmarks: 手部关键点坐标列表
            
        Returns:
            str: 识别到的动态手势名称，如果没有返回None
        """
        # 记录当前位置
        self.record_hand_position(landmarks)
        
        # 分析轨迹
        trajectory_info = self.analyze_trajectory()
        
        if not trajectory_info:
            return None
        
        # 判断是否为滑动手势
        if trajectory_info['distance'] > 50:  # 移动距离超过50像素
            direction = trajectory_info['direction']
            
            if direction == "UP":
                return "SWIPE_UP"
            elif direction == "DOWN":
                return "SWIPE_DOWN"
            elif direction == "LEFT":
                return "SWIPE_LEFT"
            elif direction == "RIGHT":
                return "SWIPE_RIGHT"
        
        return None
    
    def clear_trajectory(self):
        """清空轨迹历史"""
        if hasattr(self, 'trajectory_history'):
            self.trajectory_history.clear()
        self.last_hand_position = None