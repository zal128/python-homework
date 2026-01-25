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
FINGER_STATE_THRESHOLD = 0.02  # 手指状态判断阈值
GESTURE_COOLDOWN = 1.0  # 手势识别冷却时间（秒）

# 动作执行配置
BRIGHTNESS_STEP = 10  # 亮度调节步长
VOLUME_STEP = 0.05  # 音量调节步长（0-1之间）

# 截图配置
SCREENSHOT_DIR = os.path.join(os.path.expanduser("~"), "Pictures", "GestureScreenshots")
SCREENSHOT_PREFIX = "gesture_screenshot_"

# 手势定义
GESTURES = {
    # 手势名称: [拇指, 食指, 中指, 无名指, 小指] (1=伸直, 0=弯曲)
    "FIST": [0, 0, 0, 0, 0],  # 拳头
    "PALM": [1, 1, 1, 1, 1],  # 手掌
    "ONE": [0, 1, 0, 0, 0],   # 数字1
    "TWO": [0, 1, 1, 0, 0],   # 数字2
    "THREE": [0, 1, 1, 1, 0], # 数字3
    "FOUR": [0, 1, 1, 1, 1],  # 数字4
    "FIVE": [1, 1, 1, 1, 1],  # 数字5
    "OK": [1, 0, 0, 1, 1],    # OK手势
    "PEACE": [0, 1, 1, 0, 0], # 剪刀手
}

# 手势映射到动作
GESTURE_ACTIONS = {
    "ONE": "volume_up",      # 音量+
    "TWO": "volume_down",    # 音量-
    "THREE": "brightness_up", # 亮度+
    "FOUR": "brightness_down", # 亮度-
    "FIST": "screenshot",    # 截图
    "OK": "toggle_mode",     # 切换模式（预留）
}

# UI 配置
FONT_NAME = "FONT_HERSHEY_SIMPLEX"  # OpenCV字体名称
FONT_SCALE = 0.7
FONT_COLOR = (255, 255, 255)
FONT_THICKNESS = 2

# 调试模式
DEBUG_MODE = True
