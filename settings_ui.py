# -*- coding: utf-8 -*-
"""
设置界面模块
提供交互式设置界面，允许用户自定义系统参数
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from typing import Dict, Any


class SettingsWindow:
    """设置窗口类"""
    
    def __init__(self, config_file: str = "user_settings.json"):
        self.config_file = config_file
        self.settings = self._load_settings()
        self.root = None
        
    def _load_settings(self) -> Dict[str, Any]:
        """加载用户设置"""
        default_settings = {
            "camera_index": 0,
            "camera_width": 1024,
            "camera_height": 768,
            "mouse_sensitivity": 8.0,
            "volume_step": 0.05,
            "brightness_step": 10,
            "gesture_cooldown": 0.5,
            "auto_mode_switch": True
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # 合并设置，保留用户自定义的，使用默认值补充缺失的
                    for key, value in default_settings.items():
                        if key not in loaded:
                            loaded[key] = value
                    return loaded
        except Exception as e:
            print(f"加载设置失败: {e}")
        
        return default_settings
    
    def _save_settings(self) -> None:
        """保存用户设置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {e}")
    
    def create_window(self) -> None:
        """创建设置窗口"""
        self.root = tk.Tk()
        self.root.title("手势控制系统设置")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        
        # 设置窗口图标
        try:
            self.root.iconbitmap("gesture_icon.ico")
        except:
            pass
        
        # 创建标签页
        notebook = ttk.Notebook(self.root)
        
        # 摄像头设置标签页
        camera_frame = ttk.Frame(notebook)
        self._create_camera_tab(camera_frame)
        notebook.add(camera_frame, text="摄像头设置")
        
        # 手势设置标签页
        gesture_frame = ttk.Frame(notebook)
        self._create_gesture_tab(gesture_frame)
        notebook.add(gesture_frame, text="手势设置")
        
        notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # 按钮区域
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="保存设置", 
                  command=self._save_and_close).pack(side='right', padx=5)
        ttk.Button(button_frame, text="恢复默认", 
                  command=self._reset_defaults).pack(side='right', padx=5)
        ttk.Button(button_frame, text="取消", 
                  command=self.root.destroy).pack(side='right', padx=5)
        
        # 绑定回车键保存
        self.root.bind('<Return>', lambda e: self._save_and_close())
        
    def _create_camera_tab(self, parent: ttk.Frame) -> None:
        """创建设置摄像头标签页"""
        # 摄像头索引
        ttk.Label(parent, text="摄像头索引:").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.camera_index_var = tk.StringVar(value=str(self.settings['camera_index']))
        ttk.Spinbox(parent, from_=0, to=10, textvariable=self.camera_index_var, 
                   width=10).grid(row=0, column=1, sticky='w', padx=10, pady=5)
        
        # 分辨率设置
        ttk.Label(parent, text="分辨率宽度:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.camera_width_var = tk.StringVar(value=str(self.settings['camera_width']))
        ttk.Combobox(parent, values=["640", "800", "1024", "1280", "1920"], 
                    textvariable=self.camera_width_var, width=10).grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        ttk.Label(parent, text="分辨率高度:").grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.camera_height_var = tk.StringVar(value=str(self.settings['camera_height']))
        ttk.Combobox(parent, values=["480", "600", "768", "720", "1080"], 
                    textvariable=self.camera_height_var, width=10).grid(row=2, column=1, sticky='w', padx=10, pady=5)
        
        # 测试摄像头按钮
        ttk.Button(parent, text="测试摄像头", 
                  command=self._test_camera).grid(row=3, column=0, columnspan=2, pady=10)
        
    def _create_gesture_tab(self, parent: ttk.Frame) -> None:
        """创建设置手势标签页"""
        # 鼠标灵敏度
        ttk.Label(parent, text="鼠标灵敏度:").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.mouse_sensitivity_var = tk.DoubleVar(value=self.settings['mouse_sensitivity'])
        ttk.Scale(parent, from_=1.0, to=20.0, variable=self.mouse_sensitivity_var, 
                 orient='horizontal').grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        ttk.Label(parent, textvariable=self.mouse_sensitivity_var).grid(row=0, column=2, padx=5)
        
        # 音量调节步长
        ttk.Label(parent, text="音量调节步长:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.volume_step_var = tk.DoubleVar(value=self.settings['volume_step'])
        ttk.Scale(parent, from_=0.01, to=0.2, variable=self.volume_step_var, 
                 orient='horizontal').grid(row=1, column=1, sticky='ew', padx=10, pady=5)
        ttk.Label(parent, textvariable=self.volume_step_var).grid(row=1, column=2, padx=5)
        
        # 亮度调节步长
        ttk.Label(parent, text="亮度调节步长:").grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.brightness_step_var = tk.IntVar(value=self.settings['brightness_step'])
        ttk.Scale(parent, from_=1, to=50, variable=self.brightness_step_var, 
                 orient='horizontal').grid(row=2, column=1, sticky='ew', padx=10, pady=5)
        ttk.Label(parent, textvariable=self.brightness_step_var).grid(row=2, column=2, padx=5)
        
        # 手势冷却时间
        ttk.Label(parent, text="手势冷却时间(秒):").grid(row=3, column=0, sticky='w', padx=10, pady=5)
        self.gesture_cooldown_var = tk.DoubleVar(value=self.settings['gesture_cooldown'])
        ttk.Scale(parent, from_=0.1, to=2.0, variable=self.gesture_cooldown_var, 
                 orient='horizontal').grid(row=3, column=1, sticky='ew', padx=10, pady=5)
        ttk.Label(parent, textvariable=self.gesture_cooldown_var).grid(row=3, column=2, padx=5)
        
        # 浏览器滚动速度
        ttk.Label(parent, text="浏览器滚动速度:").grid(row=4, column=0, sticky='w', padx=10, pady=5)
        self.scroll_speed_var = tk.IntVar(value=self.settings.get('scroll_speed', 5))
        ttk.Scale(parent, from_=1, to=20, variable=self.scroll_speed_var, 
                 orient='horizontal').grid(row=4, column=1, sticky='ew', padx=10, pady=5)
        ttk.Label(parent, textvariable=self.scroll_speed_var).grid(row=4, column=2, padx=5)
        
    pass
        
    def _create_advanced_tab(self, parent: ttk.Frame) -> None:
        """创建设置高级标签页"""
        # 说明文本
        info_label = ttk.Label(parent, text="高级设置功能正在开发中，当前版本使用优化后的默认配置。", 
                              font=('Segoe UI', 9), foreground='gray')
        info_label.grid(row=0, column=0, columnspan=3, sticky='w', padx=10, pady=20)
        
        # 重置设置按钮
        ttk.Button(parent, text="重置设置", 
                  command=self._confirm_reset).grid(row=1, column=0, columnspan=2, pady=10)
        
    def _test_camera(self) -> None:
        """测试摄像头"""
        try:
            import cv2
            camera_index = int(self.camera_index_var.get())
            cap = cv2.VideoCapture(camera_index)
            
            if cap.isOpened():
                messagebox.showinfo("测试结果", f"摄像头 {camera_index} 测试成功！")
                cap.release()
            else:
                messagebox.showerror("测试结果", f"无法打开摄像头 {camera_index}")
        except Exception as e:
            messagebox.showerror("错误", f"摄像头测试失败: {e}")
    
    # 移除颜色转换方法
    
    def _save_and_close(self) -> None:
        """保存设置并关闭窗口"""
        try:
            # 收集所有设置
            self.settings.update({
                'camera_index': int(self.camera_index_var.get()),
                'camera_width': int(self.camera_width_var.get()),
                'camera_height': int(self.camera_height_var.get()),
                'mouse_sensitivity': float(self.mouse_sensitivity_var.get()),
                'volume_step': float(self.volume_step_var.get()),
                'brightness_step': int(self.brightness_step_var.get()),
                'gesture_cooldown': float(self.gesture_cooldown_var.get()),
                'scroll_speed': int(self.scroll_speed_var.get())
            })
            
            self._save_settings()
            messagebox.showinfo("成功", "设置保存成功！重启手势控制系统后生效。")
            if self.root:
                self.root.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {e}")
    def _reset_defaults(self) -> None:
        """恢复默认设置"""
        if messagebox.askyesno("确认", "确定要将所有设置恢复为默认值吗？"):
            # 重新加载默认设置
            self.settings = self._load_settings()
            
            # 更新UI控件
            self.camera_index_var.set(str(self.settings['camera_index']))
            self.camera_width_var.set(str(self.settings['camera_width']))
            self.camera_height_var.set(str(self.settings['camera_height']))
            self.mouse_sensitivity_var.set(self.settings['mouse_sensitivity'])
            self.volume_step_var.set(self.settings['volume_step'])
            self.brightness_step_var.set(self.settings['brightness_step'])
            self.gesture_cooldown_var.set(self.settings['gesture_cooldown'])
            
            messagebox.showinfo("成功", "设置已恢复为默认值！")
    
    def _confirm_reset(self) -> None:
        """确认重置所有设置"""
        if messagebox.askyesno("确认", "确定要重置所有设置为默认值吗？此操作不可撤销。"):
            try:
                if os.path.exists(self.config_file):
                    os.remove(self.config_file)
                self.settings = self._load_settings()
                messagebox.showinfo("成功", "所有设置已重置为默认值！")
            except Exception as e:
                messagebox.showerror("错误", f"重置失败: {e}")
    
    def _export_settings(self) -> None:
        """导出设置"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.settings, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("成功", f"设置已导出到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {e}")
    
    def _import_settings(self) -> None:
        """导入设置"""
        from tkinter import filedialog
        
        filename = filedialog.askopenfilename(
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    imported = json.load(f)
                
                # 验证导入的设置
                required_keys = ['camera_index', 'mouse_sensitivity', 'volume_step']
                if all(key in imported for key in required_keys):
                    self.settings.update(imported)
                    self._save_settings()
                    messagebox.showinfo("成功", "设置已导入！")
                else:
                    messagebox.showerror("错误", "导入的文件格式不正确")
            except Exception as e:
                messagebox.showerror("错误", f"导入失败: {e}")
    
    def show(self) -> None:
        """显示设置窗口"""
        self.create_window()
        self.root.mainloop()
    
    def get_settings(self) -> Dict[str, Any]:
        """获取当前设置"""
        return self.settings.copy()


def open_settings() -> None:
    """打开设置窗口"""
    settings_window = SettingsWindow()
    settings_window.show()


if __name__ == "__main__":
    open_settings()