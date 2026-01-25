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
from config import GESTURES, GESTURE_ACTIONS, FINGER_STATE_THRESHOLD, GESTURE_COOLDOWN


class GestureRecognizer:
    """手势识别器"""
    
    def __init__(self):
        """初始化手势识别器"""
        self.gestures = GESTURES
        self.gesture_actions = GESTURE_ACTIONS
        self.last_gesture_time = 0
        self.cooldown = GESTURE_COOLDOWN
        
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
                
                # 只在手势变化或冷却时间过后才更新
                current_time = time.time()
                if is_new_gesture or (current_time - self.last_gesture_time >= self.cooldown):
                    self.last_gesture_time = current_time
                    self.previous_gesture = self.current_gesture
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
        获取手势对应的动作
        
        Args:
            gesture_name: 手势名称
            
        Returns:
            str: 动作名称，如果没有映射返回None
        """
        return self.gesture_actions.get(gesture_name)
    
    def get_gesture_info(self):
        """
        获取手势说明信息
        
        Returns:
            list: 手势说明列表
        """
        info = [
            "Gesture Controls:",
            "1 finger up: Volume Up",
            "2 fingers up: Volume Down", 
            "3 fingers up: Brightness Up",
            "4 fingers up: Brightness Down",
            "Fist: Screenshot",
            "OK: Toggle Mode",
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