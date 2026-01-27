# -*- coding: utf-8 -*-
"""
工具函数模块
"""

import cv2
import numpy as np
import time
from datetime import datetime
import os
import sys
import os as os_import

# 添加父目录到路径
sys.path.append(os_import.path.dirname(os_import.path.dirname(os_import.path.abspath(__file__))))

try:
    from config import FONT_NAME, FONT_SCALE, FONT_COLOR, FONT_THICKNESS, DEBUG_MODE
except Exception:
    try:
        from config import FONT_NAME, FONT_SCALE, FONT_COLOR, FONT_THICKNESS
    except Exception:
        FONT_NAME = cv2.FONT_HERSHEY_SIMPLEX
        FONT_SCALE = 0.7
        FONT_COLOR = (0, 255, 0)
        FONT_THICKNESS = 2
    DEBUG_MODE = False

def draw_landmarks(frame, landmarks, color=(0, 255, 0), thickness=2):
    """
    在图像上绘制手部关键点
    
    Args:
        frame: 图像帧
        landmarks: 关键点坐标列表
        color: 颜色
        thickness: 线条粗细
    """
    if not landmarks:
        return frame
    
    # 绘制关键点
    for i, (x, y, z) in enumerate(landmarks):
        cv2.circle(frame, (x, y), 5, color, -1)
        cv2.putText(frame, str(i), (x + 5, y - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
    
    # 绘制连接线
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),  # 拇指
        (0, 5), (5, 6), (6, 7), (7, 8),  # 食指
        (0, 9), (9, 10), (10, 11), (11, 12),  # 中指
        (0, 13), (13, 14), (14, 15), (15, 16),  # 无名指
        (0, 17), (17, 18), (18, 19), (19, 20),  # 小指
        (5, 9), (9, 13), (13, 17)  # 手掌
    ]
    
    for start, end in connections:
        if start < len(landmarks) and end < len(landmarks):
            x1, y1, _ = landmarks[start]
            x2, y2, _ = landmarks[end]
            cv2.line(frame, (x1, y1), (x2, y2), color, thickness)
    
    return frame


def calculate_distance(point1, point2):
    """
    计算两点之间的欧氏距离
    
    Args:
        point1: 点1坐标 (x, y)
        point2: 点2坐标 (x, y)
        
    Returns:
        float: 两点距离
    """
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def calculate_angle(point1, point2, point3):
    """
    计算三点之间的夹角（point2为顶点）
    
    Args:
        point1: 点1坐标
        point2: 点2坐标（顶点）
        point3: 点3坐标
        
    Returns:
        float: 夹角度数
    """
    v1 = np.array([point1[0] - point2[0], point1[1] - point2[1]])
    v2 = np.array([point3[0] - point2[0], point3[1] - point2[1]])
    
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    
    if norm_v1 == 0 or norm_v2 == 0:
        return 0
    
    cos_angle = dot_product / (norm_v1 * norm_v2)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    
    angle = np.arccos(cos_angle)
    return np.degrees(angle)


class FPSCounter:
    """FPS计数器"""
    
    def __init__(self):
        self.start_time = time.time()
        self.frame_count = 0
        self.fps = 0
    
    def update(self):
        """更新FPS"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.start_time >= 1.0:
            self.fps = self.frame_count / (current_time - self.start_time)
            self.frame_count = 0
            self.start_time = current_time
        
        return self.fps
    
    def draw(self, frame, position=(10, 30), color=(0, 255, 0), thickness=2):
        """
        在帧上绘制FPS
        
        Args:
            frame: 图像帧
            position: 位置
            color: 颜色
            thickness: 线条粗细
        """
        fps_text = f"FPS: {int(self.fps)}"
        cv2.putText(frame, fps_text, position, 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, thickness)
        return frame


def create_screenshot_directory(path):
    """
    创建截图保存目录
    
    Args:
        path: 目录路径
    """
    os.makedirs(path, exist_ok=True)


def get_timestamp_filename(prefix="screenshot", extension="png"):
    """
    生成带时间戳的文件名
    
    Args:
        prefix: 文件名前缀
        extension: 文件扩展名
        
    Returns:
        str: 文件名
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def draw_gesture_info(frame, gesture_name, action_name, position=(10, 60), 
                     font_scale=0.7, color=(0, 255, 0), thickness=2):
    """
    在帧上绘制手势信息
    
    Args:
        frame: 图像帧
        gesture_name: 手势名称
        action_name: 动作名称
        position: 位置
        font_scale: 字体大小
        color: 颜色
        thickness: 线条粗细
    """
    if gesture_name and action_name:
        info_text = f"Gesture: {gesture_name} | Action: {action_name}"
        cv2.putText(frame, info_text, position,
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
    return frame


def draw_instructions(frame, instructions, start_position=(10, 450), 
                     font_scale=None, color=None, thickness=None):
    """
    在帧上绘制操作说明
    
    Args:
        frame: 图像帧
        instructions: 说明文本列表
        start_position: 起始位置
        font_scale: 字体大小
        color: 颜色
        thickness: 线条粗细
    """
    font_scale = font_scale or (FONT_SCALE - 0.1)
    color = color or FONT_COLOR
    thickness = thickness or (FONT_THICKNESS - 1)
    """
    在帧上绘制操作说明
    
    Args:
        frame: 图像帧
        instructions: 说明文本列表
        start_position: 起始位置
        font_scale: 字体大小
        color: 颜色
        thickness: 线条粗细
    """
    y_offset = 0
    for i, instruction in enumerate(instructions):
        y = start_position[1] + y_offset
        cv2.putText(frame, instruction, 
                   (start_position[0], y),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
        y_offset += 20
    return frame


def is_browser_active():
    """
    检测当前活动窗口是否是浏览器
    
    Returns:
        bool: 如果是浏览器返回True，否则返回False
    """
    try:
        import win32gui
        import win32process
        import psutil
        
        # 获取当前活动窗口句柄
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return False
        
        # 获取窗口标题
        window_title = win32gui.GetWindowText(hwnd)
        if not window_title:
            return False
        
        # 获取进程ID
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if not pid:
            return False
        
        try:
            # 获取进程名称
            process = psutil.Process(pid)
            process_name = process.name().lower()
            
            # 检查是否是浏览器进程
            browser_processes = [
                'chrome.exe',      # Google Chrome
                'firefox.exe',     # Mozilla Firefox
                'msedge.exe',      # Microsoft Edge
                'safari.exe',      # Safari
                'opera.exe',       # Opera
                'brave.exe',       # Brave
                'vivaldi.exe'      # Vivaldi
            ]
            
            return process_name in browser_processes
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
            
    except Exception as e:
        if DEBUG_MODE:
            print(f"Browser detection error: {e}")
        return False


def get_browser_name():
    """
    获取当前浏览器的名称
    
    Returns:
        str: 浏览器名称，如果不是浏览器返回None
    """
    try:
        import win32gui
        import win32process
        import psutil
        
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return None
        
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if not pid:
            return None
        
        try:
            process = psutil.Process(pid)
            process_name = process.name().lower()
            
            browser_names = {
                'chrome.exe': 'Chrome',
                'firefox.exe': 'Firefox',
                'msedge.exe': 'Edge',
                'safari.exe': 'Safari',
                'opera.exe': 'Opera',
                'brave.exe': 'Brave',
                'vivaldi.exe': 'Vivaldi'
            }
            
            return browser_names.get(process_name)
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
            
    except Exception:
        return None


def is_music_playing():
    """
    检测是否有音乐正在播放（支持网易云音乐等）
    
    Returns:
        tuple: (bool:是否正在播放, str:音乐软件名称)
    """
    try:
        import win32gui
        import win32process
        import psutil
        
        # 检查音频会话状态（Windows Core Audio API）
        try:
            from pycaw.pycaw import AudioUtilities
            sessions = AudioUtilities.GetAllSessions()
            
            for session in sessions:
                if session.State and session.State == 1:  # 1 = Active
                    if session.Process:
                        process_name = session.Process.name().lower()
                        # 检查是否是音乐软件
                        music_apps = {
                            'cloudmusic.exe': 'NetEase Cloud Music',
                            'spotify.exe': 'Spotify',
                            'qqmusic.exe': 'QQ Music',
                            'foobar2000.exe': 'Foobar2000',
                            'vlc.exe': 'VLC Media Player',
                            'winamp.exe': 'Winamp'
                        }
                        
                        if process_name in music_apps:
                            return True, music_apps[process_name]
        except:
            pass
        
        # 备选方案：检查活跃窗口标题是否包含播放指示
        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            window_title = win32gui.GetWindowText(hwnd).lower()
            
            # 网易云音乐的播放状态通常会在标题中显示
            if '网易云音乐' in window_title or 'netease' in window_title:
                # 检查是否有播放相关的标题变化（这只是一个启发式检测）
                return True, 'NetEase Cloud Music'
        
        return False, None
        
    except Exception as e:
        if DEBUG_MODE:
            print(f"Music detection error: {e}")
        return False, None


def get_music_app_name():
    """
    获取当前正在播放音乐的应用名称
    
    Returns:
        str: 音乐软件名称，如果没有返回None
    """
    is_playing, app_name = is_music_playing()
    return app_name if is_playing else None