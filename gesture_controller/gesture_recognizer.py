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
from config import GESTURES, GESTURE_ACTIONS, MOUSE_GESTURE_ACTIONS, FINGER_STATE_THRESHOLD, GESTURE_COOLDOWN


class GestureRecognizer:
    """手势识别器"""
    
    def __init__(self):
        """初始化手势识别器"""
        self.gestures = GESTURES
        self.gesture_actions = GESTURE_ACTIONS
        self.mouse_gesture_actions = MOUSE_GESTURE_ACTIONS
        self.last_gesture_time = 0
        self.cooldown = GESTURE_COOLDOWN
        
        # 模式管理
        self.mode = "MAIN"  # MAIN: 主模式, MOUSE: 鼠标模式
        
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
                
                # 音量/亮度调节（1-4指）可以连续触发（冷却时间0.3秒）
                if recognized_gesture in ["ONE", "TWO", "THREE", "FOUR"]:
                    if current_time - self.last_gesture_time >= 0.3:  # 0.3秒冷却
                        self.last_gesture_time = current_time
                        return recognized_gesture, True
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
        if self.mode == "MOUSE":
            return self.mouse_gesture_actions.get(gesture_name)
        else:
            return self.gesture_actions.get(gesture_name)
    
    def toggle_mode(self, current_gesture_name=None):
        """切换模式"""
        if self.mode == "MAIN":
            self.mode = "MOUSE"
            print("\n" + "=" * 60)
            print("Switched to MOUSE MODE")
            print("=" * 60)
            print("  ONE finger: Move mouse")
            print("  TWO fingers: Left click")
            print("  THREE fingers: Right click")
            print("  FOUR fingers: Double click")
            print("  FIST/PALM: Exit mouse mode")
            print("=" * 60)
        else:
            self.mode = "MAIN"
            print("\n" + "=" * 60)
            print("Switched to MAIN MODE")
            print("=" * 60)
            print("  ONE: Volume Up")
            print("  TWO: Volume Down")
            print("  THREE: Brightness Up")
            print("  FOUR: Brightness Down")
            print("  FIST: Screenshot")
            print("  PALM: Switch to mouse mode")
            print("=" * 60)
        
        # 重置手势状态，避免立即再次触发
        self.gesture_history.clear()
        # 设置当前手势为刚识别的手势，这样is_new_gesture在下次会是False
        self.current_gesture = current_gesture_name
        self.previous_gesture = None
        # 设置较长的冷却时间（2秒），确保用户有时间改变手势
        self.last_gesture_time = time.time() + 2.0
        return self.mode
    
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