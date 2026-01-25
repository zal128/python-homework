# -*- coding: utf-8 -*-
"""
MediaPipe手部追踪模块（基于Tasks API）
"""

import cv2
import numpy as np
import urllib.request
import os
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import Image as MpImage, ImageFormat

class HandTracker:
    """MediaPipe手部追踪器（Tasks API版本）"""
    
    def __init__(self, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5):
        """
        初始化手部追踪器
        
        Args:
            max_num_hands: 最大检测手数
            min_detection_confidence: 最小检测置信度
            min_tracking_confidence: 最小跟踪置信度
        """
        self.max_num_hands = max_num_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.frame_timestamp_ms = 0
        
        # 下载模型文件（如果不存在）
        self.model_path = self._download_model()
        
        # 初始化MediaPipe HandLandmarker
        self.landmarker = self._initialize_landmarker()
        
        # 关键点索引
        self.TIP_IDS = [4, 8, 12, 16, 20]  # 指尖索引（拇指、食指、中指、无名指、小指）
        self.FINGER_IDS = {
            'thumb': [1, 2, 3, 4],
            'index': [5, 6, 7, 8],
            'middle': [9, 10, 11, 12],
            'ring': [13, 14, 15, 16],
            'pinky': [17, 18, 19, 20]
        }
    
    def _download_model(self):
        """下载MediaPipe HandLandmarker模型文件"""
        model_url = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'
        model_path = os.path.join(os.path.dirname(__file__), 'hand_landmarker.task')
        
        if not os.path.exists(model_path):
            print("正在下载MediaPipe HandLandmarker模型文件...")
            try:
                urllib.request.urlretrieve(model_url, model_path)
                print("模型下载完成！")
            except Exception as e:
                print(f"模型下载失败: {e}")
                raise
        
        return model_path
    
    def _initialize_landmarker(self):
        """初始化HandLandmarker"""
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            min_hand_detection_confidence=self.min_detection_confidence,
            min_hand_presence_confidence=self.min_tracking_confidence,
            num_hands=self.max_num_hands,
            running_mode=vision.RunningMode.VIDEO
        )
        return vision.HandLandmarker.create_from_options(options)
    
    def process_frame(self, frame):
        """
        处理单帧图像并检测手部
        
        Args:
            frame: BGR格式的图像帧
            
        Returns:
            tuple: (处理结果, 标注后的图像)
        """
        # 转换为RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 创建MediaPipe Image对象
        mp_image = MpImage(image_format=ImageFormat.SRGB, data=image_rgb)
        
        # 增加时间戳
        self.frame_timestamp_ms += 33  # 假设30fps，每帧约33ms
        
        # 检测手部
        detection_result = self.landmarker.detect_for_video(mp_image, self.frame_timestamp_ms)
        
        # 绘制标注
        annotated_frame = frame.copy()
        hand_landmarks_list = []
        
        if detection_result.hand_landmarks:
            for hand_landmarks in detection_result.hand_landmarks:
                # 提取关键点坐标
                landmarks = []
                for landmark in hand_landmarks:
                    h, w, _ = frame.shape
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    z = landmark.z
                    landmarks.append((x, y, z))
                
                hand_landmarks_list.append(landmarks)
                
                # 绘制关键点和连接线
                self._draw_landmarks(annotated_frame, hand_landmarks)
        
        return hand_landmarks_list, annotated_frame
    
    def _draw_landmarks(self, frame, hand_landmarks):
        """
        在图像上绘制手部关键点（手动实现）
        
        Args:
            frame: 图像帧
            hand_landmarks: MediaPipe手部关键点列表
        """
        h, w, _ = frame.shape
        
        # 绘制关键点
        for landmark in hand_landmarks:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        
        # 绘制连接线（基于MediaPipe手部连接关系）
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # 拇指
            (0, 5), (5, 6), (6, 7), (7, 8),  # 食指
            (0, 9), (9, 10), (10, 11), (11, 12),  # 中指
            (0, 13), (13, 14), (14, 15), (15, 16),  # 无名指
            (0, 17), (17, 18), (18, 19), (19, 20),  # 小指
            (5, 9), (9, 13), (13, 17)  # 手掌
        ]
        
        for connection in connections:
            idx1, idx2 = connection
            if idx1 < len(hand_landmarks) and idx2 < len(hand_landmarks):
                x1 = int(hand_landmarks[idx1].x * w)
                y1 = int(hand_landmarks[idx1].y * h)
                x2 = int(hand_landmarks[idx2].x * w)
                y2 = int(hand_landmarks[idx2].y * h)
                cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
    
    def get_finger_states(self, landmarks):
        """
        获取手指状态（伸直或弯曲）
        
        Args:
            landmarks: 关键点坐标列表
            
        Returns:
            list: 手指状态列表 [拇指, 食指, 中指, 无名指, 小指]
        """
        if not landmarks:
            return None
        
        finger_states = []
        
        # 拇指特殊处理（比较x坐标）
        thumb_tip = landmarks[4][:2]
        thumb_base = landmarks[2][:2]
        
        if thumb_tip[0] > thumb_base[0]:
            finger_states.append(1)  # 伸直
        else:
            finger_states.append(0)  # 弯曲
        
        # 其他四指（比较y坐标）
        for tip_id in self.TIP_IDS[1:]:
            tip = landmarks[tip_id][:2]
            pip = landmarks[tip_id - 2][:2]  # 中间关节
            
            if tip[1] < pip[1]:
                finger_states.append(1)  # 伸直
            else:
                finger_states.append(0)  # 弯曲
        
        return finger_states
    
    def release(self):
        """释放资源"""
        if hasattr(self, 'landmarker'):
            self.landmarker.close()
