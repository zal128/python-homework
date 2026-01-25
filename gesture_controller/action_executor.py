# -*- coding: utf-8 -*-
"""
动作执行器模块
负责执行手势识别的结果动作
"""

import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities
import pyautogui
import mss
from PIL import Image
import os
import time
import threading
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BRIGHTNESS_STEP, VOLUME_STEP, SCREENSHOT_DIR, SCREENSHOT_PREFIX, CAMERA_WIDTH, CAMERA_HEIGHT, MOUSE_SENSITIVITY, MOUSE_SMOOTHING, MOUSE_DEAD_ZONE


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
        
        # 鼠标控制相关
        self.mouse_last_position = None
        self.mouse_smoothed_position = None
        self.mouse_last_action = None
        self.mouse_action_cooldown = 0.5  # 鼠标动作冷却时间
        self.mouse_sensitivity = MOUSE_SENSITIVITY
        self.mouse_smoothing = MOUSE_SMOOTHING
        self.mouse_dead_zone = MOUSE_DEAD_ZONE
        self.mouse_freeze_until = 0  # 鼠标冻结截止时间
        pyautogui.FAILSAFE = False  # 禁用故障保护
        
        # 摄像头区域到屏幕区域的映射（只使用中心区域，避免手出镜头）
        self.mouse_capture_area = {
            'x_min': int(CAMERA_WIDTH * 0.1),   # 使用10%-90%区域
            'x_max': int(CAMERA_WIDTH * 0.9),
            'y_min': int(CAMERA_HEIGHT * 0.1),
            'y_max': int(CAMERA_HEIGHT * 0.9)
        }
        
    def _init_volume_control(self):
        """
        初始化音量控制接口（使用pycaw官方方法）
        """
        try:
            print("Initializing volume control...")
            
            # 使用pycaw官方方法获取音量控制
            device = AudioUtilities.GetSpeakers()
            if not device:
                print("✗ No audio devices found")
                return None
            
            print(f"✓ Audio device: {device.FriendlyName}")
            
            # 直接获取音量控制接口
            volume = device.EndpointVolume
            print("✓ Volume control initialized successfully (pycaw)")
            return volume
            
        except Exception as e:
            print(f"✗ Failed to initialize volume control: {e}")
            print("  Please ensure pycaw is installed: pip install pycaw")
            return None
    
    def execute_action(self, action_name, **kwargs):
        """
        执行动作
        
        Args:
            action_name: 动作名称
            **kwargs: 额外的参数（如鼠标位置等）
            
        Returns:
            bool: 是否执行成功
        """
        if not action_name:
            return False
        
        # 检查鼠标动作冷却时间（防止过快执行）
        if action_name.startswith("mouse_"):
            if time.time() - self.action_timestamp < self.mouse_action_cooldown:
                if action_name != "mouse_move":  # 鼠标移动不受冷却限制
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
            elif action_name == "mouse_move":
                self._mouse_move(kwargs.get('landmarks'))
            elif action_name == "mouse_click_left":
                self._mouse_click_left()
            elif action_name == "mouse_click_right":
                self._mouse_click_right()
            elif action_name == "mouse_double_click":
                self._mouse_double_click()
            elif action_name == "mouse_drag":
                self._mouse_drag(kwargs.get('landmarks'))
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
        if not self.volume_interface:
            print("Volume control not available")
            return
            
        try:
            # 使用pycaw增加音量（每次增加VOLUME_STEP）
            current_volume = self.volume_interface.GetMasterVolumeLevelScalar()
            new_volume = min(1.0, current_volume + VOLUME_STEP)
            self.volume_interface.SetMasterVolumeLevelScalar(new_volume, None)
            print(f"Volume up: {new_volume:.0%}")
        except Exception as e:
            print(f"Volume control error: {e}")
    
    def _volume_down(self):
        """降低音量"""
        if not self.volume_interface:
            print("Volume control not available")
            return
            
        try:
            # 使用pycaw降低音量（每次减少VOLUME_STEP）
            current_volume = self.volume_interface.GetMasterVolumeLevelScalar()
            new_volume = max(0.0, current_volume - VOLUME_STEP)
            self.volume_interface.SetMasterVolumeLevelScalar(new_volume, None)
            print(f"Volume down: {new_volume:.0%}")
        except Exception as e:
            print(f"Volume control error: {e}")
    
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
        """切换模式 - 实际切换由GestureRecognizer处理"""
        # 这个方法的实际功能在GestureRecognizer.toggle_mode()中实现
        # 这里只是作为一个占位符，让execute_action的映射正常工作
        pass
    
    def _mouse_move(self, landmarks):
        """
        移动鼠标（带冻结功能，避免手势切换时跳动）
        
        Args:
            landmarks: 手部关键点坐标列表
        """
        if not landmarks:
            return
        
        # 检查是否在冻结期（手势切换后的保护时间）
        if time.time() < self.mouse_freeze_until:
            return  # 冻结鼠标，不更新位置
        
        # 获取食指指尖（index 8）作为鼠标位置参考
        index_finger_tip = landmarks[8]
        x, y = index_finger_tip[0], index_finger_tip[1]
        
        # 限制在捕获区域内（避免手出镜头）
        x = max(self.mouse_capture_area['x_min'], min(self.mouse_capture_area['x_max'], x))
        y = max(self.mouse_capture_area['y_min'], min(self.mouse_capture_area['y_max'], y))
        
        # 直接将摄像头坐标映射到屏幕（不使用相对移动）
        screen_width, screen_height = pyautogui.size()
        
        # 线性映射：摄像头640x480 → 屏幕分辨率
        target_x = (x - self.mouse_capture_area['x_min']) / (self.mouse_capture_area['x_max'] - self.mouse_capture_area['x_min']) * screen_width
        target_y = (y - self.mouse_capture_area['y_min']) / (self.mouse_capture_area['y_max'] - self.mouse_capture_area['y_min']) * screen_height
        
        # 轻微平滑处理（降低平滑系数以提高响应速度）
        if self.mouse_smoothed_position:
            last_x, last_y = self.mouse_smoothed_position
            # 降低平滑系数到0.3，让鼠标更紧跟手
            smooth_factor = 0.3
            target_x = last_x * smooth_factor + target_x * (1 - smooth_factor)
            target_y = last_y * smooth_factor + target_y * (1 - smooth_factor)
        
        # 限制在屏幕边界内
        target_x = max(0, min(screen_width - 1, target_x))
        target_y = max(0, min(screen_height - 1, target_y))
        
        # 移动鼠标
        pyautogui.moveTo(int(target_x), int(target_y), duration=0.0)
        self.mouse_smoothed_position = (target_x, target_y)
        self.mouse_last_position = (x, y)
    
    def _mouse_click_left(self):
        """鼠标左键单击"""
        pyautogui.click()
        print("Left click")
    
    def _mouse_click_right(self):
        """鼠标右键单击"""
        pyautogui.rightClick()
        print("Right click")
    
    def _mouse_double_click(self):
        """鼠标双击"""
        pyautogui.doubleClick()
        print("Double click")
    
    def _mouse_drag(self, landmarks):
        """
        鼠标拖拽（使用与mouse_move相同的逻辑）
        
        Args:
            landmarks: 手部关键点坐标列表
        """
        if not landmarks:
            return
        
        # 使用手掌中心（手腕点0）作为拖拽位置参考
        palm = landmarks[0]
        x, y = palm[0], palm[1]
        
        # 限制在捕获区域内
        x = max(self.mouse_capture_area['x_min'], min(self.mouse_capture_area['x_max'], x))
        y = max(self.mouse_capture_area['y_min'], min(self.mouse_capture_area['y_max'], y))
        
        # 归一化
        norm_x = 2 * (x - self.mouse_capture_area['x_min']) / (self.mouse_capture_area['x_max'] - self.mouse_capture_area['x_min']) - 1
        norm_y = 2 * (y - self.mouse_capture_area['y_min']) / (self.mouse_capture_area['y_max'] - self.mouse_capture_area['y_min']) - 1
        
        # 应用死区
        if abs(norm_x) < self.mouse_dead_zone:
            norm_x = 0
        if abs(norm_y) < self.mouse_dead_zone:
            norm_y = 0
        
        if norm_x == 0 and norm_y == 0 and self.mouse_smoothed_position:
            return
        
        # 计算移动距离
        screen_width, screen_height = pyautogui.size()
        move_x = norm_x * self.mouse_sensitivity * screen_width * 0.03
        move_y = norm_y * self.mouse_sensitivity * screen_height * 0.03
        
        current_x, current_y = pyautogui.position()
        target_x = current_x + move_x
        target_y = current_y + move_y
        
        # 平滑处理
        if self.mouse_smoothed_position:
            last_x, last_y = self.mouse_smoothed_position
            target_x = last_x * self.mouse_smoothing + target_x * (1 - self.mouse_smoothing)
            target_y = last_y * self.mouse_smoothing + target_y * (1 - self.mouse_smoothing)
        
        # 限制在屏幕边界
        target_x = max(0, min(screen_width - 1, target_x))
        target_y = max(0, min(screen_height - 1, target_y))
        
        # 如果还没有拖拽，开始拖拽
        if self.mouse_last_action != "mouse_drag":
            pyautogui.mouseDown()
            print("Drag start")
        
        # 移动鼠标（拖拽中）
        pyautogui.moveTo(int(target_x), int(target_y), duration=0.0)
        self.mouse_smoothed_position = (target_x, target_y)
        self.mouse_last_position = (x, y)
        self.mouse_last_action = "mouse_drag"
    
    def stop_drag(self):
        """停止拖拽"""
        if self.mouse_last_action == "mouse_drag":
            pyautogui.mouseUp()
            print("Drag end")
            self.mouse_last_action = None
            self.mouse_last_position = None
    
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