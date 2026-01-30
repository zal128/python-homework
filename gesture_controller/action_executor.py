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
        self.mouse_last_action = None
        self.mouse_action_cooldown = 0.5  # 鼠标动作冷却时间
        self.mouse_sensitivity = MOUSE_SENSITIVITY
        self.mouse_smoothing = MOUSE_SMOOTHING
        self.mouse_dead_zone = MOUSE_DEAD_ZONE
        self.mouse_freeze_until = 0  # 鼠标冻结截止时间
        pyautogui.FAILSAFE = False  # 禁用故障保护
        
        # 浏览器滚动控制
        self.browser_scroll_active = False  # 是否正在滚动
        self.browser_scroll_direction = None  # 滚动方向: 'up' or 'down'
        self.browser_scroll_speed = 3  # 滚动速度
        self.browser_scroll_last_time = 0  # 上次滚动时间
        
        # 音乐控制相关
        self.last_music_action_time = 0  # 上次音乐动作时间
        self.music_action_cooldown = 0.3  # 音乐动作冷却时间
        
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
            elif action_name == "browser_refresh":
                self._browser_refresh()
            elif action_name == "browser_back":
                self._browser_back()
            elif action_name == "browser_forward":
                self._browser_forward()
            elif action_name == "browser_reopen_tab":
                self._browser_reopen_tab()
            elif action_name == "browser_close_tab":
                self._browser_close_tab()
            elif action_name == "browser_switch_tab":
                self._browser_switch_tab()
            elif action_name == "browser_scroll_up":
                self._browser_scroll_up()
            elif action_name == "browser_scroll_down":
                self._browser_scroll_down()
            elif action_name == "music_play_pause":
                self._music_play_pause()
            elif action_name == "music_next":
                self._music_next()
            elif action_name == "music_previous":
                self._music_previous()
            elif action_name == "music_volume_up":
                self._music_volume_up()
            elif action_name == "music_volume_down":
                self._music_volume_down()
            elif action_name == "music_like":
                self._music_like()
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
            print("音量控制不可用")
            return
            
        try:
            # 使用pycaw增加音量（每次增加VOLUME_STEP）
            current_volume = self.volume_interface.GetMasterVolumeLevelScalar()
            new_volume = min(1.0, current_volume + VOLUME_STEP)
            self.volume_interface.SetMasterVolumeLevelScalar(new_volume, None)
            print(f"音量+: {new_volume:.0%}")
        except Exception as e:
            print(f"音量控制错误: {e}")
    
    def _volume_down(self):
        """降低音量"""
        if not self.volume_interface:
            print("音量控制不可用")
            return
            
        try:
            # 使用pycaw降低音量（每次减少VOLUME_STEP）
            current_volume = self.volume_interface.GetMasterVolumeLevelScalar()
            new_volume = max(0.0, current_volume - VOLUME_STEP)
            self.volume_interface.SetMasterVolumeLevelScalar(new_volume, None)
            print(f"音量-: {new_volume:.0%}")
        except Exception as e:
            print(f"音量控制错误: {e}")
    
    def _brightness_up(self):
        """增加亮度"""
        try:
            current_brightness = sbc.get_brightness()[0]
            new_brightness = min(100, current_brightness + BRIGHTNESS_STEP)
            sbc.set_brightness(new_brightness)
            print(f"亮度+: {new_brightness}%")
        except Exception as e:
            print(f"亮度调节失败: {e}")
    
    def _brightness_down(self):
        """降低亮度"""
        try:
            current_brightness = sbc.get_brightness()[0]
            new_brightness = max(0, current_brightness - BRIGHTNESS_STEP)
            sbc.set_brightness(new_brightness)
            print(f"亮度-: {new_brightness}%")
        except Exception as e:
            print(f"亮度调节失败: {e}")
    
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
                    print(f"截图已保存: {filepath}")
                    
                    # 可选：复制到剪贴板
                    # img.show()  # 临时显示
                    
            except Exception as e:
                print(f"截图失败: {e}")
                # 备用方案：使用pyautogui
                try:
                    screenshot = pyautogui.screenshot()
                    filename = f"{SCREENSHOT_PREFIX}_backup_{int(time.time())}.png"
                    filepath = os.path.join(SCREENSHOT_DIR, filename)
                    screenshot.save(filepath)
                    print(f"截图已保存(备用): {filepath}")
                except Exception as e2:
                    print(f"备用截图也失败了: {e2}")
    
    def _toggle_mode(self):
        """切换模式 - 实际切换由GestureRecognizer处理"""
        # 这个方法的实际功能在GestureRecognizer.toggle_mode()中实现
        # 这里只是作为一个占位符，让execute_action的映射正常工作
        pass
    
    def _mouse_move(self, landmarks):
        """
        移动鼠标（缩放映射模式：基于中心点的灵敏度倍增）
        
        工作原理：
        1. 计算手指相对于画面中心的偏移量
        2. 放大这个偏移量（灵敏度倍增）
        3. 将放大后的偏移量加到中心点上
        4. 映射到屏幕
        
        效果：手指只需移动摄像头的1/3区域，就能覆盖整个屏幕
        
        Args:
            landmarks: 手部关键点坐标列表
        """
        if not landmarks:
            # 没有手时停止鼠标
            return
        
        # 检查是否在冻结期（手势切换后的保护时间）
        if time.time() < self.mouse_freeze_until:
            return  # 冻结鼠标，不更新位置
        
        # 获取食指指尖（index 8）作为鼠标位置参考
        index_finger_tip = landmarks[8]
        x, y = index_finger_tip[0], index_finger_tip[1]
        
        # 灵敏度倍增系数
        # 1.0 = 等比例映射（手指移动1cm，光标移动1cm）
        # 3.0 = 高灵敏度（手指移动1cm，光标移动3cm）
        sensitivity_multiplier = 3.0
        
        # 计算相对于画面中心的偏移量
        center_x = CAMERA_WIDTH / 2
        center_y = CAMERA_HEIGHT / 2
        
        offset_x = x - center_x  # 相对于中心的x偏移
        offset_y = y - center_y  # 相对于中心的y偏移
        
        # 放大偏移量（灵敏度倍增）
        offset_x_enhanced = offset_x * sensitivity_multiplier
        offset_y_enhanced = offset_y * sensitivity_multiplier
        
        # 将放大后的偏移量加回到中心点
        x_enhanced = center_x + offset_x_enhanced
        y_enhanced = center_y + offset_y_enhanced
        
        # 限制在摄像头范围内
        x_enhanced = max(0, min(CAMERA_WIDTH, x_enhanced))
        y_enhanced = max(0, min(CAMERA_HEIGHT, y_enhanced))
        
        # 将整个摄像头画面（640x480）直接映射到屏幕
        screen_width, screen_height = pyautogui.size()
        
        # 等比例映射：放大后的摄像头坐标 → 屏幕坐标
        target_x = x_enhanced / CAMERA_WIDTH * screen_width
        target_y = y_enhanced / CAMERA_HEIGHT * screen_height
        
        # 限制在屏幕边界
        target_x = max(0, min(screen_width - 1, target_x))
        target_y = max(0, min(screen_height - 1, target_y))
        
        # 移动鼠标（不使用平滑，确保手停止时鼠标立即停止）
        pyautogui.moveTo(int(target_x), int(target_y), duration=0.0)
    
    def _mouse_click_left(self):
        """鼠标左键单击"""
        pyautogui.click()
        print("左键点击")
    
    def _mouse_click_right(self):
        """鼠标右键单击"""
        pyautogui.rightClick()
        print("右键点击")
    
    def _mouse_double_click(self):
        """鼠标双击"""
        pyautogui.doubleClick()
        print("双击")
    
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
            print("开始拖拽")
        
        # 移动鼠标（拖拽中）
        pyautogui.moveTo(int(target_x), int(target_y), duration=0.0)
        self.mouse_smoothed_position = (target_x, target_y)
        self.mouse_last_position = (x, y)
        self.mouse_last_action = "mouse_drag"
    
    def stop_drag(self):
        """停止拖拽"""
        if self.mouse_last_action == "mouse_drag":
            pyautogui.mouseUp()
            print("结束拖拽")
            self.mouse_last_action = None
            self.mouse_last_position = None
    
    def _browser_refresh(self):
        """刷新页面 (F5)"""
        pyautogui.press('f5')
        print("浏览器: 刷新页面")
    
    def _browser_back(self):
        """返回上一页 (Alt + Left)"""
        pyautogui.hotkey('alt', 'left')
        print("浏览器: 后退")
    
    def _browser_forward(self):
        """前进下一页 (Alt + Right)"""
        pyautogui.hotkey('alt', 'right')
        print("浏览器: 前进")
    
    def _browser_reopen_tab(self):
        """重新打开关闭的标签页 (Ctrl + Shift + T)"""
        pyautogui.hotkey('ctrl', 'shift', 't')
        print("浏览器: 恢复标签")
    
    def _browser_close_tab(self):
        """关闭标签页 (Ctrl + W)"""
        pyautogui.hotkey('ctrl', 'w')
        print("浏览器: 关闭标签")
    
    def _browser_switch_tab(self):
        """切换标签页 (Ctrl + Tab)"""
        pyautogui.hotkey('ctrl', 'tab')
        print("浏览器: 切换标签")
    
    def _browser_scroll_up(self):
        """开始向上滚动页面（持续）"""
        self.browser_scroll_active = True
        self.browser_scroll_direction = 'up'
        self.browser_scroll_last_time = time.time()
        print("浏览器: 开始向上滚动 (连续)")
    
    def _browser_scroll_down(self):
        """开始向下滚动页面（持续）"""
        self.browser_scroll_active = True
        self.browser_scroll_direction = 'down'
        self.browser_scroll_last_time = time.time()
        print("浏览器: 开始向下滚动 (连续)")
    
    def _stop_browser_scroll(self):
        """停止浏览器滚动"""
        if self.browser_scroll_active:
            self.browser_scroll_active = False
            self.browser_scroll_direction = None
            print("浏览器: 停止滚动")
    
    def update_browser_scroll(self):
        """更新浏览器滚动（在主循环中调用）"""
        if not self.browser_scroll_active:
            return
        
        current_time = time.time()
        # 每0.05秒滚动一次（20次/秒），实现平滑滚动
        if current_time - self.browser_scroll_last_time >= 0.05:
            if self.browser_scroll_direction == 'up':
                pyautogui.scroll(20)  # 每次滚动2个单位
            elif self.browser_scroll_direction == 'down':
                pyautogui.scroll(-20)  # 每次滚动-2个单位
            self.browser_scroll_last_time = current_time
    
    def _music_play_pause(self):
        """音乐播放/暂停（Alt + Ctrl + P）"""
        pyautogui.hotkey('alt', 'ctrl', 'p')
        print("音乐: 播放/暂停")
    
    def _music_next(self):
        """下一首（Alt + Ctrl + Right）"""
        pyautogui.hotkey('alt', 'ctrl', 'right')
        print("音乐: 下一首")
    
    def _music_previous(self):
        """上一首（Alt + Ctrl + Left）"""
        pyautogui.hotkey('alt', 'ctrl', 'left')
        print("音乐: 上一首")
    
    def _music_volume_up(self):
        """增加音乐音量"""
        if not self.volume_interface:
            print("音量控制不可用")
            return
            
        try:
            current_volume = self.volume_interface.GetMasterVolumeLevelScalar()
            new_volume = min(1.0, current_volume + VOLUME_STEP * 2)  # 音乐模式音量步长加倍
            self.volume_interface.SetMasterVolumeLevelScalar(new_volume, None)
            print(f"音乐音量+: {new_volume:.0%}")
        except Exception as e:
            print(f"音乐音量控制错误: {e}")
    
    def _music_volume_down(self):
        """降低音乐音量"""
        if not self.volume_interface:
            print("音量控制不可用")
            return
            
        try:
            current_volume = self.volume_interface.GetMasterVolumeLevelScalar()
            new_volume = max(0.0, current_volume - VOLUME_STEP * 2)  # 音乐模式音量步长加倍
            self.volume_interface.SetMasterVolumeLevelScalar(new_volume, None)
            print(f"音乐音量-: {new_volume:.0%}")
        except Exception as e:
            print(f"音乐音量控制错误: {e}")
    
    def _music_like(self):
        """喜欢歌曲（Ctrl + Shift + L）"""
        pyautogui.hotkey('ctrl', 'shift', 'l')
        print("音乐: 喜欢歌曲")
    
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
        
        # 鼠标冻结状态
        if self.mouse_freeze_until > time.time():
            freeze_remaining = self.mouse_freeze_until - time.time()
            status["mouse_frozen"] = f"Yes ({freeze_remaining:.1f}s)"
        else:
            status["mouse_frozen"] = "No"
        
        return status
    
    def set_mouse_sensitivity(self, sensitivity: float):
        """设置鼠标灵敏度"""
        self.mouse_sensitivity = max(1.0, min(20.0, sensitivity))
        print(f"鼠标灵敏度设置为: {self.mouse_sensitivity}")
    
    def set_volume_step(self, step: float):
        """设置音量调节步长"""
        global VOLUME_STEP
        VOLUME_STEP = max(0.01, min(0.2, step))
        print(f"音量调节步长设置为: {VOLUME_STEP}")
    
    def set_brightness_step(self, step: int):
        """设置亮度调节步长"""
        global BRIGHTNESS_STEP
        BRIGHTNESS_STEP = max(1, min(50, step))
        print(f"亮度调节步长设置为: {BRIGHTNESS_STEP}")
    
    def set_scroll_speed(self, speed: int):
        """设置滚动速度"""
        self.browser_scroll_speed = max(1, min(20, speed))
        print(f"浏览器滚动速度设置为: {self.browser_scroll_speed}")