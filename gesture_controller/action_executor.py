# -*- coding: utf-8 -*-
"""
动作执行器模块
负责执行手势识别的结果动作
"""

import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import pyautogui
import mss
from PIL import Image
import os
import time
import threading
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BRIGHTNESS_STEP, VOLUME_STEP, SCREENSHOT_DIR, SCREENSHOT_PREFIX


class ActionExecutor:
    """动作执行器"""
    
    def __init__(self):
        """初始化动作执行器"""
        self.volume_interface = self._init_volume_control()
        self.screenshot_lock = threading.Lock()
        
        # 创建截图目录
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        
        # 状态信息
        self.last_action = None
        self.action_timestamp = 0
        
    def _init_volume_control(self):
        """
        初始化音量控制接口
        
        Returns:
            IAudioEndpointVolume: 音量控制接口
        """
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            return interface
        except Exception as e:
            print(f"Warning: Failed to initialize volume control: {e}")
            return None
    
    def execute_action(self, action_name):
        """
        执行动作
        
        Args:
            action_name: 动作名称
            
        Returns:
            bool: 是否执行成功
        """
        if not action_name:
            return False
        
        try:
            if action_name == "volume_up":
                self._volume_up()
            elif action_name == "volume_down":
                self._volume_down()
            elif action_name == "brightness_up":
                self._brightness_up()
            elif action_name == "brightness_down":
                self._brightness_down()
            elif action_name == "screenshot":
                self._take_screenshot()
            elif action_name == "toggle_mode":
                self._toggle_mode()
            else:
                print(f"Unknown action: {action_name}")
                return False
            
            self.last_action = action_name
            self.action_timestamp = time.time()
            return True
            
        except Exception as e:
            print(f"Error executing action {action_name}: {e}")
            return False
    
    def _volume_up(self):
        """增加音量"""
        if self.volume_interface:
            current_volume = self.volume_interface.GetMasterVolumeLevelScalar()
            new_volume = min(1.0, current_volume + VOLUME_STEP)
            self.volume_interface.SetMasterVolumeLevelScalar(new_volume, None)
            print(f"Volume up: {new_volume:.0%}")
        else:
            print("Volume control not available")
    
    def _volume_down(self):
        """降低音量"""
        if self.volume_interface:
            current_volume = self.volume_interface.GetMasterVolumeLevelScalar()
            new_volume = max(0.0, current_volume - VOLUME_STEP)
            self.volume_interface.SetMasterVolumeLevelScalar(new_volume, None)
            print(f"Volume down: {new_volume:.0%}")
        else:
            print("Volume control not available")
    
    def _brightness_up(self):
        """增加亮度"""
        try:
            current_brightness = sbc.get_brightness()[0]
            new_brightness = min(100, current_brightness + BRIGHTNESS_STEP)
            sbc.set_brightness(new_brightness)
            print(f"Brightness up: {new_brightness}%")
        except Exception as e:
            print(f"Failed to adjust brightness: {e}")
    
    def _brightness_down(self):
        """降低亮度"""
        try:
            current_brightness = sbc.get_brightness()[0]
            new_brightness = max(0, current_brightness - BRIGHTNESS_STEP)
            sbc.set_brightness(new_brightness)
            print(f"Brightness down: {new_brightness}%")
        except Exception as e:
            print(f"Failed to adjust brightness: {e}")
    
    def _take_screenshot(self):
        """截图"""
        with self.screenshot_lock:
            try:
                # 使用mss进行截图（更高效）
                with mss.mss() as sct:
                    # 获取主显示器
                    monitor = sct.monitors[1]
                    screenshot = sct.grab(monitor)
                    
                    # 转换为PIL Image
                    img = Image.frombytes("RGB", screenshot.size, screenshot.bgr, "raw", "BGRX")
                    
                    # 生成文件名
                    filename = f"{SCREENSHOT_PREFIX}{int(time.time())}.png"
                    filepath = os.path.join(SCREENSHOT_DIR, filename)
                    
                    # 保存图片
                    img.save(filepath, "PNG")
                    print(f"Screenshot saved: {filepath}")
                    
                    # 可选：复制到剪贴板
                    # img.show()  # 临时显示
                    
            except Exception as e:
                print(f"Screenshot failed: {e}")
                # 备用方案：使用pyautogui
                try:
                    screenshot = pyautogui.screenshot()
                    filename = f"{SCREENSHOT_PREFIX}_backup_{int(time.time())}.png"
                    filepath = os.path.join(SCREENSHOT_DIR, filename)
                    screenshot.save(filepath)
                    print(f"Screenshot saved (backup): {filepath}")
                except Exception as e2:
                    print(f"Backup screenshot also failed: {e2}")
    
    def _toggle_mode(self):
        """切换模式（预留功能）"""
        print("Mode toggle triggered (reserved for future extension)")
        # 这里可以添加模式切换逻辑，例如：
        # - 切换到手势鼠标模式
        # - 切换到应用控制模式
        # - 切换到媒体控制模式
    
    def get_status(self):
        """
        获取执行器状态
        
        Returns:
            dict: 状态信息
        """
        status = {
            "last_action": self.last_action,
            "action_timestamp": self.action_timestamp,
            "screenshot_dir": SCREENSHOT_DIR,
            "volume_available": self.volume_interface is not None
        }
        
        # 获取当前音量
        if self.volume_interface:
            try:
                current_volume = self.volume_interface.GetMasterVolumeLevelScalar()
                status["current_volume"] = f"{current_volume:.0%}"
            except:
                status["current_volume"] = "Unknown"
        
        # 获取当前亮度
        try:
            current_brightness = sbc.get_brightness()[0]
            status["current_brightness"] = f"{current_brightness}%"
        except:
            status["current_brightness"] = "Unknown"
        
        return status