# -*- coding: utf-8 -*-
"""
悬浮状态窗口 - 显示手势控制系统的实时状态
"""

import tkinter as tk
from tkinter import ttk
import queue
import threading
import time


class StatusWindow:
    """悬浮状态窗口"""
    
    def __init__(self, update_queue):
        """
        初始化悬浮窗口
        
        Args:
            update_queue: 用于接收状态更新的队列
        """
        self.update_queue = update_queue
        self.root = None
        self.is_running = False
        self.mode_var = None
        self.gesture_var = None
        self.volume_var = None
        self.brightness_var = None
        self.music_var = None
        
    def _create_window(self):
        """创建悬浮窗口"""
        self.root = tk.Tk()
        self.root.title("Gesture Control")
        
        # 设置窗口样式
        self.root.attributes('-topmost', True)  # 始终置顶
        self.root.attributes('-alpha', 0.9)     # 透明度（稍微提高）
        self.root.overrideredirect(True)        # 无边框
        
        # 设置窗口大小和位置（屏幕右上角）
        window_width = 280
        window_height = 140
        screen_width = self.root.winfo_screenwidth()
        x = screen_width - window_width - 20
        y = 20
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 设置背景色
        bg_color = "#2E3440"  # 深色背景（Nord主题）
        
        # 创建主框架
        main_frame = tk.Frame(self.root, bg=bg_color, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题区域（带装饰）
        title_frame = tk.Frame(main_frame, bg=bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 8))
        
        # 标题图标和文字
        title_label = tk.Label(
            title_frame, 
            text="✋ 手势控制", 
            font=('Segoe UI', 11, 'bold'),
            bg=bg_color,
            fg="#88C0D0"  # 蓝色（Nord主题）
        )
        title_label.pack(side=tk.LEFT)
        
        # 状态指示灯（小圆点）
        self.status_light = tk.Canvas(title_frame, width=12, height=12, bg=bg_color, highlightthickness=0)
        self.status_light.pack(side=tk.RIGHT, padx=(0, 5))
        self.status_dot = self.status_light.create_oval(2, 2, 10, 10, fill="#4CAF50", outline="")
        
        # 分隔线（更美观）
        separator = tk.Frame(main_frame, height=2, bg="#3B4252")
        separator.pack(fill=tk.X, pady=(0, 8))
        
        # 状态显示框架（使用网格布局，更整齐）
        status_frame = tk.Frame(main_frame, bg=bg_color)
        status_frame.pack(fill=tk.X)
        
        # 配置网格布局
        status_frame.columnconfigure(1, weight=1)
        
        # 模式（带图标）
        tk.Label(status_frame, text="🎯", font=('Segoe UI', 9), bg=bg_color, fg="#ECEFF4").grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        tk.Label(status_frame, text="模式:", font=('Segoe UI', 9), bg=bg_color, fg="#E5E9F0").grid(row=0, column=1, sticky=tk.W)
        self.mode_var = tk.StringVar(value="主模式")
        self.mode_value_label = tk.Label(status_frame, textvariable=self.mode_var, font=('Segoe UI', 9, 'bold'), bg=bg_color, fg="#88C0D0")
        self.mode_value_label.grid(row=0, column=2, sticky=tk.E)
        
        # 手势（带图标）
        tk.Label(status_frame, text="👋", font=('Segoe UI', 9), bg=bg_color, fg="#ECEFF4").grid(row=1, column=0, sticky=tk.W, padx=(0, 8))
        tk.Label(status_frame, text="手势:", font=('Segoe UI', 9), bg=bg_color, fg="#E5E9F0").grid(row=1, column=1, sticky=tk.W)
        self.gesture_var = tk.StringVar(value="-")
        gesture_value = tk.Label(status_frame, textvariable=self.gesture_var, font=('Segoe UI', 9), bg=bg_color, fg="#EBCB8B")
        gesture_value.grid(row=1, column=2, sticky=tk.E)
        
        # 音量（带图标）
        tk.Label(status_frame, text="🔊", font=('Segoe UI', 9), bg=bg_color, fg="#ECEFF4").grid(row=2, column=0, sticky=tk.W, padx=(0, 8))
        tk.Label(status_frame, text="音量:", font=('Segoe UI', 9), bg=bg_color, fg="#E5E9F0").grid(row=2, column=1, sticky=tk.W)
        self.volume_var = tk.StringVar(value="-")
        volume_value = tk.Label(status_frame, textvariable=self.volume_var, font=('Segoe UI', 9), bg=bg_color, fg="#B48EAD")
        volume_value.grid(row=2, column=2, sticky=tk.E)
        
        # 亮度（带图标）
        tk.Label(status_frame, text="☀️", font=('Segoe UI', 9), bg=bg_color, fg="#ECEFF4").grid(row=3, column=0, sticky=tk.W, padx=(0, 8))
        tk.Label(status_frame, text="亮度:", font=('Segoe UI', 9), bg=bg_color, fg="#E5E9F0").grid(row=3, column=1, sticky=tk.W)
        self.brightness_var = tk.StringVar(value="-")
        brightness_value = tk.Label(status_frame, textvariable=self.brightness_var, font=('Segoe UI', 9), bg=bg_color, fg="#BF616A")
        brightness_value.grid(row=3, column=2, sticky=tk.E)
        
        # 音乐状态（带图标）
        tk.Label(status_frame, text="🎵", font=('Segoe UI', 9), bg=bg_color, fg="#ECEFF4").grid(row=4, column=0, sticky=tk.W, padx=(0, 8))
        tk.Label(status_frame, text="音乐:", font=('Segoe UI', 9), bg=bg_color, fg="#E5E9F0").grid(row=4, column=1, sticky=tk.W)
        self.music_var = tk.StringVar(value="未播放")
        music_value = tk.Label(status_frame, textvariable=self.music_var, font=('Segoe UI', 8), bg=bg_color, fg="#D08770")
        music_value.grid(row=4, column=2, sticky=tk.E)
        
        # 添加一些间距
        for i in range(5):
            status_frame.rowconfigure(i, pad=3)
        
        # 绑定右键关闭事件
        self.root.bind('<Button-3>', lambda e: self.stop())
        
        # 绑定左键拖动
        self.root.bind('<Button-1>', self._start_move)
        self.root.bind('<B1-Motion>', self._on_move)
        
    def _start_move(self, event):
        """开始拖动窗口"""
        self.x = event.x
        self.y = event.y
        
    def _on_move(self, event):
        """拖动窗口"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
        
    def start(self):
        """启动悬浮窗口"""
        if self.is_running:
            return
            
        self.is_running = True
        self._create_window()
        
        # 启动更新线程
        update_thread = threading.Thread(target=self._update_loop, daemon=True)
        update_thread.start()
        
        # 启动Tkinter主循环
        self.root.mainloop()
        
    def stop(self):
        """停止悬浮窗口"""
        if not self.is_running:
            return
            
        self.is_running = False
        if self.root:
            self.root.quit()
            
    def _update_loop(self):
        """后台更新循环"""
        while self.is_running:
            try:
                # 从队列获取更新（超时1秒）
                try:
                    status = self.update_queue.get(timeout=1)
                    self._update_display(status)
                except queue.Empty:
                    pass
                    
            except Exception as e:
                print(f"Status window update error: {e}")
                
    def _update_display(self, status):
        """
        更新显示内容
        
        Args:
            status: 状态字典
        """
        if not self.root:
            return
            
        # 更新模式（带颜色编码）
        mode = status.get('mode', 'MAIN')
        mode_text = mode
        mode_color = "#88C0D0"  # 默认蓝色
        
        if mode == 'BROWSER':
            mode_text = "浏览器"
            mode_color = "#A3BE8C"  # 绿色
        elif mode == 'MUSIC':
            mode_text = "音乐"
            mode_color = "#B48EAD"  # 紫色
        elif mode == 'MOUSE':
            mode_text = "鼠标"
            mode_color = "#D08770"  # 橙色
        elif mode == 'MAIN':
            mode_text = "主模式"
            mode_color = "#88C0D0"  # 蓝色
            
        self.mode_var.set(mode_text)
        # 更新模式颜色
        self.mode_value_label.config(fg=mode_color)
        
        # 更新手势
        gesture = status.get('gesture', '-')
        if gesture and gesture != '-':
            # 将手势名称转换为中文显示
            gesture_map = {
                'ONE': '1指',
                'TWO': '2指', 
                'THREE': '3指',
                'FOUR': '4指',
                'FIST': '拳头',
                'PALM': '手掌',
                'ROCK': '🤘',
                'THUMBS_UP': '👍'
            }
            display_gesture = gesture_map.get(gesture, gesture)
            self.gesture_var.set(display_gesture)
        else:
            self.gesture_var.set('-')
            
        # 更新音量
        volume = status.get('volume', '-')
        if volume and volume != '-':
            self.volume_var.set(f"{volume}")
        else:
            self.volume_var.set('-')
            
        # 更新亮度
        brightness = status.get('brightness', '-')
        if brightness and brightness != '-':
            self.brightness_var.set(f"{brightness}")
        else:
            self.brightness_var.set('-')
            
        # 更新音乐状态
        music_app = status.get('music_app', None)
        if music_app:
            # 简化应用名称
            app_short = music_app
            if 'NetEase' in music_app:
                app_short = "网易云"
            elif 'Spotify' in music_app:
                app_short = "Spotify"
            elif 'QQ' in music_app:
                app_short = "QQ音乐"
            else:
                app_short = music_app[:8]  # 截取前8个字符
            self.music_var.set(f"{app_short}")
        else:
            self.music_var.set("未播放")


def start_status_window(update_queue):
    """
    启动状态窗口（在独立线程中）
    
    Args:
        update_queue: 用于接收状态更新的队列
    """
    window = StatusWindow(update_queue)
    window.start()
