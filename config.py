#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局配置
"""

import json
import os
from pathlib import Path

# 项目路径
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
CONFIG_FILE = DATA_DIR / "config.json"
MODEL_DIR = DATA_DIR / "models"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

# 默认配置
DEFAULT_CONFIG = {
    "hotkey": "ctrl+alt+space",  # 按住说话的热键
    "language": "zh",  # 识别语言：zh中文，en英文
    "model_name": "base",  # 模型名称: qwen3-asr-0.6b/tiny/base/small/medium/large
    "input_mode": "push_to_talk",  # 按一次启动录音模式: push_to_talk / toggle
    "output_method": "clipboard",  # 文字插入方式: clipboard（复制粘贴）
    "audio_device": None,  # 音频设备ID，None=自动选择
    "sample_rate": 16000,  # 采样率
    "channels": 1,  # 声道数
    "enable_beep": True,  # 开始/结束录音时的提示音
    "auto_punctuation": True,  # 自动加标点
    "debug_mode": False,  # 调试模式
    "log_level": "INFO",  # 日志级别
}

# 模型名称对应的大小（MB）
MODEL_SIZES = {
    "qwen3-asr-0.6b": 300,  # Qwen3-ASR-0.6B
    "tiny": 75,  # tiny.en / tiny
    "base": 142,  # base.en / base
    "small": 466,  # small.en / small
    "medium": 1.5,  # GB
    "large": 3.1,  # GB
}


def load_config() -> dict:
    """加载配置文件，不存在则创建默认"""
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        # 合并默认配置（确保新字段存在）
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
        return config
    except Exception as e:
        print(f"读取配置文件失败: {e}，使用默认配置")
        return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    """保存配置文件"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存配置文件失败: {e}")
        return False


def config_to_str(config: dict = None) -> str:
    """将配置转换为可读字符串"""
    if config is None:
        config = load_config()

    lines = ["📱 语音输入法配置 📱", "=" * 40]
    for key, value in sorted(config.items()):
        if key == "hotkey":
            lines.append(f"🔘 热键: {value}")
        elif key == "language":
            lang_name = {
                "zh": "中文",
                "en": "英文",
                "auto": "自动识别"
            }.get(value, value)
            lines.append(f"🌐 识别语言: {lang_name}")
        elif key == "model_name":
            size_mb = MODEL_SIZES.get(value, "?")
            if value == "qwen3-asr-0.6b":
                lines.append(f"🧠 识别模型: Qwen3-ASR-0.6B (~{size_mb}MB)")
            else:
                lines.append(f"🧠 识别模型: {value} (~{size_mb}MB)")
        elif key == "input_mode":
            mode_name = {
                "push_to_talk": "按住说话",
                "toggle": "开关模式"
            }.get(value, value)
            lines.append(f"🎤 录音模式: {mode_name}")
        elif key == "output_method":
            method_name = {
                "typing": "模拟打字",
                "clipboard": "复制粘贴"
            }.get(value, value)
            lines.append(f"⌨️ 文字插入: {method_name}")
    lines.append("=" * 40)
    return "\n".join(lines)


# 全局配置实例
_config = None


def get_config():
    """获取全局配置（单例模式）"""
    global _config
    if _config is None:
        _config = load_config()
    return _config
