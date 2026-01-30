# -*- coding: utf-8 -*-
"""
手势控制系统启动器
提供图形化启动界面和功能选择
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import threading
from typing import Optional


class GestureControlLauncher:
    """手势控制启动器"""
    
    def __init__(self):
        self.root = None
        self.main_process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.camera_preview_var = None
        
    def create_main_window(self) -> None:
        """创建主窗口"""
        self.root = tk.Tk()
        self.root.title("手势控制系统启动器")
        self.root.geometry("400x550")
        self.root.resizable(False, False)
        self.root.configure(bg='white')
        
        # 设置窗口图标
        try:
            self.root.iconbitmap("gesture_icon.ico")
        except:
            pass
        
        # 设置主题样式
        self._setup_styles()
        
        # 创建界面
        self._create_ui()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _setup_styles(self) -> None:
        """设置样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 自定义样式
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), background='white')
        style.configure('Subtitle.TLabel', font=('Segoe UI', 12), background='white')
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('Secondary.TButton', font=('Segoe UI', 9))
        style.configure('TFrame', background='white')
        style.configure('TCheckbutton', background='white')
        
        # 方形框容器样式
        style.configure('Container.TLabelframe', background='white', bordercolor='#e0e0e0')
        style.configure('Container.TLabelframe.Label', background='white', font=('Segoe UI', 9, 'bold'))
        
    def _create_ui(self) -> None:
        """创建UI界面"""
        # 初始化摄像头预览变量（默认不显示预览）
        self.camera_preview_var = tk.BooleanVar(value=False)
        
        # 标题区域
        title_frame = ttk.Frame(self.root, style='TFrame')
        title_frame.pack(fill='x', padx=20, pady=20)
        
        # 应用图标和标题
        icon_label = ttk.Label(title_frame, text="✋", font=('Segoe UI', 32), background='white')
        icon_label.pack()
        
        title_label = ttk.Label(title_frame, text="手势控制系统", style='Title.TLabel')
        title_label.pack(pady=(10, 5))
        
        subtitle_label = ttk.Label(title_frame, text="基于MediaPipe的手势识别与控制", 
                                  style='Subtitle.TLabel')
        subtitle_label.pack()
        
        # 功能按钮区域（直接显示4个按钮）
        button_frame = ttk.Frame(self.root, style='TFrame')
        button_frame.pack(fill='both', expand=True, padx=25, pady=20)
        
        # 主功能按钮 - 启动手势控制
        start_button = ttk.Button(button_frame, text="启动手势控制", 
                                style='Primary.TButton',
                                command=self._start_gesture_control)
        start_button.pack(fill='x', padx=15, pady=10)
        
        # 系统设置按钮
        settings_button = ttk.Button(button_frame, text="系统设置", 
                                    style='Secondary.TButton',
                                    command=self._open_settings)
        settings_button.pack(fill='x', padx=15, pady=8)
        
        # 使用教程按钮
        tutorial_button = ttk.Button(button_frame, text="使用教程", 
                                    style='Secondary.TButton',
                                    command=self._show_tutorial)
        tutorial_button.pack(fill='x', padx=15, pady=8)
        
        # 手势教学按钮
        gesture_tutorial_button = ttk.Button(button_frame, text="手势教学", 
                                           style='Secondary.TButton',
                                           command=self._open_gesture_tutorial)
        gesture_tutorial_button.pack(fill='x', padx=15, pady=8)
        
        # 摄像头预览选项（复选框）
        preview_frame = ttk.Frame(button_frame, style='TFrame')
        preview_frame.pack(fill='x', padx=15, pady=10)
        
        preview_checkbutton = ttk.Checkbutton(
            preview_frame, 
            text="显示摄像头预览窗口", 
            variable=self.camera_preview_var,
            style='TCheckbutton'
        )
        preview_checkbutton.pack(anchor='w')
        
        # 添加提示文字
        preview_tip = ttk.Label(
            preview_frame, 
            text="取消勾选可隐藏摄像头画面，减少资源占用",
            font=('Segoe UI', 8), 
            foreground='gray',
            background='white'
        )
        preview_tip.pack(anchor='w', padx=20, pady=(2, 0))
        
        # 状态显示区域
        status_frame = ttk.Frame(self.root, style='TFrame')
        status_frame.pack(fill='x', padx=20, pady=15)
        
        self.status_label = ttk.Label(status_frame, text="就绪", 
                                     font=('Segoe UI', 9), foreground='green')
        self.status_label.pack()
        
        # 版本信息
        version_label = ttk.Label(self.root, text="v1.0.0", 
                                 font=('Segoe UI', 8), foreground='gray', background='white')
        version_label.pack(side='bottom', pady=5)
        
    def _start_gesture_control(self) -> None:
        """启动手势控制系统"""
        if self.is_running:
            messagebox.showwarning("警告", "手势控制系统已经在运行中！")
            return
            
        def run_main():
            try:
                # 构建启动参数
                args = [sys.executable, 'main.py']
                if not self.camera_preview_var.get():
                    args.append('--no-viz')
                
                # 启动主程序
                self.main_process = subprocess.Popen(args)
                
                self.is_running = True
                self.root.after(0, self._update_status_running)
                
                # 等待进程结束
                self.main_process.wait()
                
                self.is_running = False
                self.root.after(0, self._update_status_stopped)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"启动失败: {e}"))
                self.is_running = False
                self.root.after(0, self._update_status_stopped)
        
        # 在新线程中运行
        thread = threading.Thread(target=run_main, daemon=True)
        thread.start()
        
        self._update_status_starting()
        
    def _stop_gesture_control(self) -> None:
        """停止手势控制系统"""
        if self.main_process and self.is_running:
            try:
                self.main_process.terminate()
                self.main_process.wait(timeout=3)
            except:
                try:
                    self.main_process.kill()
                except:
                    pass
            
            self.is_running = False
            self.main_process = None
            self._update_status_stopped()
            messagebox.showinfo("成功", "手势控制系统已停止")
        else:
            messagebox.showinfo("提示", "手势控制系统未运行")
        
    def _open_settings(self) -> None:
        """打开设置界面"""
        try:
            subprocess.Popen([sys.executable, 'settings_ui.py'])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开设置界面: {e}")
    
    def _show_tutorial(self) -> None:
        """显示使用教程"""
        tutorial_text = """手势控制系统使用指南

📖 基本操作:
1. 确保摄像头正常工作
2. 在摄像头前做出标准手势
3. 系统将自动识别并执行相应操作

✋ 支持的手势:
• 1根手指: 音量+ / 播放暂停
• 2根手指: 音量- / 下一曲
• 3根手指: 亮度+ / 上一曲
• 4根手指: 亮度- / 音量+
• 握拳: 停止滚动 / 音量-
• 手掌: 切换模式
• 摇滚手势: 截屏 / 切换标签页
• 点赞: 向上滚动 / 喜欢歌曲

🎯 模式说明:
• 主模式: 基础系统控制
• 鼠标模式: 鼠标指针控制
• 浏览器模式: 网页浏览控制
• 音乐模式: 音乐播放控制

💡 提示:
• 系统自动检测浏览器和音乐状态
• 可在设置界面自定义参数
• 手势校准可提高识别准确率"""
        
        tutorial_window = tk.Toplevel(self.root)
        tutorial_window.title("使用教程")
        tutorial_window.geometry("500x600")
        
        text_widget = tk.Text(tutorial_window, wrap='word', font=('Segoe UI', 10))
        text_widget.insert('1.0', tutorial_text)
        text_widget.config(state='disabled')
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        close_button = ttk.Button(tutorial_window, text="关闭", 
                                 command=tutorial_window.destroy)
        close_button.pack(pady=10)
    
    def _open_gesture_tutorial(self) -> None:
        """打开手势教学"""
        tutorial_window = tk.Toplevel(self.root)
        tutorial_window.title("手势教学")
        tutorial_window.geometry("600x700")
        tutorial_window.configure(bg='white')
        tutorial_window.resizable(False, False)
        
        # 标题
        title_label = ttk.Label(tutorial_window, text="手势操作教学", 
                               font=('Segoe UI', 18, 'bold'), background='white')
        title_label.pack(pady=(20, 10))
        
        # 说明文字
        desc_label = ttk.Label(tutorial_window, 
                              text="学习基本手势，快速上手手势控制系统",
                              font=('Segoe UI', 10), background='white', 
                              foreground='gray')
        desc_label.pack(pady=(0, 20))
        
        # 创建画布区域
        canvas_frame = ttk.Frame(tutorial_window, style='TFrame')
        canvas_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 创建Canvas和Scrollbar
        canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 手势教学内容
        gestures = [
            {
                "icon": "1️⃣",
                "name": "单指操作",
                "description": "伸出食指，其余手指弯曲",
                "functions": [
                    "主模式：音量增加",
                    "音乐模式：播放/暂停",
                    "鼠标模式：移动光标"
                ]
            },
            {
                "icon": "2️⃣", 
                "name": "双指操作",
                "description": "伸出食指和中指，其余手指弯曲",
                "functions": [
                    "主模式：音量减少",
                    "音乐模式：下一首",
                    "鼠标模式：左键点击"
                ]
            },
            {
                "icon": "3️⃣",
                "name": "三指操作", 
                "description": "伸出食指、中指和无名指，其余手指弯曲",
                "functions": [
                    "主模式：亮度增加",
                    "音乐模式：上一首",
                    "鼠标模式：右键点击"
                ]
            },
            {
                "icon": "4️⃣",
                "name": "四指操作",
                "description": "伸出除拇指外的四根手指",
                "functions": [
                    "主模式：亮度减少",
                    "音乐模式：音量增加",
                    "鼠标模式：双击"
                ]
            },
            {
                "icon": "✊",
                "name": "握拳",
                "description": "五指全部弯曲成拳",
                "functions": [
                    "主模式：截图",
                    "音乐模式：音量减少",
                    "浏览器模式：向下滚动"
                ]
            },
            {
                "icon": "✋",
                "name": "手掌",
                "description": "五指全部伸直张开",
                "functions": [
                    "主模式：切换到鼠标模式",
                    "音乐模式：退出到主模式"
                ]
            },
            {
                "icon": "🤘",
                "name": "摇滚手势",
                "description": "伸出食指和小指，其余手指弯曲",
                "functions": [
                    "主模式：截图",
                    "浏览器模式：切换标签页"
                ]
            },
            {
                "icon": "👍",
                "name": "点赞手势",
                "description": "拇指伸直向上，其余手指弯曲",
                "functions": [
                    "浏览器模式：向上滚动",
                    "音乐模式：喜欢歌曲"
                ]
            }
        ]
        
        # 添加每个手势的教学内容
        for i, gesture in enumerate(gestures):
            # 创建手势容器
            gesture_frame = ttk.LabelFrame(scrollable_frame, text=f"  {gesture['name']}  ",
                                         style='Container.TLabelframe')
            gesture_frame.pack(fill='x', padx=10, pady=10)
            
            # 手势图标
            icon_label = ttk.Label(gesture_frame, text=gesture['icon'], 
                                 font=('Segoe UI', 24), background='white')
            icon_label.pack(pady=(10, 5))
            
            # 手势描述
            desc_label = ttk.Label(gesture_frame, text=gesture['description'],
                                 font=('Segoe UI', 9), background='white',
                                 foreground='gray')
            desc_label.pack(pady=(0, 10))
            
            # 功能列表
            for func in gesture['functions']:
                func_label = ttk.Label(gesture_frame, text=f"• {func}",
                                     font=('Segoe UI', 9), background='white')
                func_label.pack(anchor='w', padx=20, pady=2)
        
        # 底部说明
        bottom_frame = ttk.Frame(tutorial_window, style='TFrame')
        bottom_frame.pack(fill='x', padx=20, pady=20)
        
        tip_label = ttk.Label(bottom_frame,
                            text="💡 提示：保持手势稳定，摄像头清晰识别效果更佳",
                            font=('Segoe UI', 9, 'italic'),
                            background='white',
                            foreground='#666666')
        tip_label.pack()
        
        # 按钮区域
        button_frame = ttk.Frame(tutorial_window, style='TFrame')
        button_frame.pack(fill='x', padx=20, pady=10)
        
        close_button = ttk.Button(button_frame, text="关闭", 
                                 command=tutorial_window.destroy)
        close_button.pack(pady=10)
    
    def _open_calibration(self) -> None:
        """打开手势校准"""
        messagebox.showinfo("信息", "手势校准功能正在开发中...")
    
    def _update_status_starting(self) -> None:
        """更新状态为启动中"""
        self.status_label.config(text="启动中...", foreground='orange')
    
    def _update_status_running(self) -> None:
        """更新状态为运行中"""
        self.status_label.config(text="运行中", foreground='green')
    
    def _update_status_stopped(self) -> None:
        """更新状态为已停止"""
        self.status_label.config(text="已停止", foreground='red')
    
    def _on_closing(self) -> None:
        """窗口关闭事件处理器"""
        if self.is_running:
            if messagebox.askokcancel("确认", "手势控制系统仍在运行，确定要退出吗？"):
                self._stop_gesture_control()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self) -> None:
        """运行启动器"""
        self.create_main_window()
        self.root.mainloop()


def main():
    """主函数"""
    launcher = GestureControlLauncher()
    launcher.run()


if __name__ == "__main__":
    main()