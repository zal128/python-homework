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
