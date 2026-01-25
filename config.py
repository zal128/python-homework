# -*- coding: utf-8 -*-
"""
手势控制系统配置文件
"""

import os

# 摄像头配置
CAMERA_INDEX = 0  # 默认摄像头索引
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# MediaPipe 配置
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.5
MAX_NUM_HANDS = 1  # 只检测一只手

# 手势识别配置
FINGER_STATE_THRESHOLD = 0.015  # 手指状态判断阈值（降低提高准确度）
GESTURE_COOLDOWN = 0.5  # 手势识别冷却时间（缩短到0.5秒，提高响应）

# 动作执行配置
BRIGHTNESS_STEP = 10  # 亮度调节步长
VOLUME_STEP = 0.05  # 音量调节步长（0-1之间）

# 鼠标控制配置
MOUSE_SENSITIVITY = 5.0  # 鼠标灵敏度（1.0-5.0，越大越灵敏）
MOUSE_SMOOTHING = 0.3 # 鼠标平滑系数（0.0-1.0，越大越平滑）
MOUSE_DEAD_ZONE = 0.01  # 鼠标死区（防止微小抖动）

# 截图配置
SCREENSHOT_DIR = os.path.join(os.path.expanduser("~"), "Pictures", "GestureScreenshots")
SCREENSHOT_PREFIX = "gesture_screenshot_"

# 手势定义（优化识别准确度）
GESTURES = {
    # 手势名称: [拇指, 食指, 中指, 无名指, 小指] (1=伸直, 0=弯曲)
    "FIST": [0, 0, 0, 0, 0],      # 拳头 - 最容易做
    "PALM": [1, 1, 1, 1, 1],      # 手掌（5指） - 最容易做
    "ONE": [0, 1, 0, 0, 0],       # 数字1
    "TWO": [0, 1, 1, 0, 0],       # 数字2
    "THREE": [0, 1, 1, 1, 0],     # 数字3
    "FOUR": [0, 1, 1, 1, 1],      # 数字4
    "ROCK": [0, 1, 0, 0, 1],      # 摇滚手势（食指+小指伸直）🤘 - 用于截图
}

# 主模式手势映射（优化：摇滚手势=截图，与PALM差异极大）
GESTURE_ACTIONS = {
    "ONE": "volume_up",          # 音量+
    "TWO": "volume_down",        # 音量-
    "THREE": "brightness_up",    # 亮度+
    "FOUR": "brightness_down",   # 亮度-
    "ROCK": "screenshot",        # 摇滚手势=截图🤘（食指+小指伸直，极易识别）
    "PALM": "toggle_mode",       # 手掌=切换模式（5指伸直，与ROCK完全不同）
}

# 鼠标模式手势映射（优化后）
MOUSE_GESTURE_ACTIONS = {
    "ONE": "mouse_move",         # 1指：鼠标移动
    "TWO": "mouse_click_left",   # 2指：左键点击
    "THREE": "mouse_click_right", # 3指：右键点击
    "FOUR": "mouse_double_click", # 4指：双击
    "FIST": "toggle_mode",       # 拳头：退出鼠标模式
    "PALM": "toggle_mode",       # 手掌：也用于退出鼠标模式（更容易做）
}

# UI 配置
FONT_NAME = "FONT_HERSHEY_SIMPLEX"  # OpenCV字体名称
FONT_SCALE = 0.7
FONT_COLOR = (255, 255, 255)
FONT_THICKNESS = 2

# 调试模式
DEBUG_MODE = True
