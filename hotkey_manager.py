#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热键管理器
监听全局热键，实现按住说话功能
"""

import threading
import time
import keyboard as kb
from config import get_config
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class HotkeyManager:
    def __init__(self, recorder, recognizer, typer):
        self.recorder = recorder
        self.recognizer = recognizer
        self.typer = typer
        self.config = get_config()
        
        self.hotkey = self.config["hotkey"]
        self.input_mode = self.config["input_mode"]
        self.is_hotkey_pressed = False
        self.is_processing = False
        self.hotkey_thread = None
        
        logger.info(f"热键管理器初始化，热键: {self.hotkey}，模式: {self.input_mode}")

    def start(self):
        """启动热键监听"""
        logger.info(f"注册热键: {self.hotkey}")
        
        if self.input_mode == "push_to_talk":
            # 按住说话模式
            kb.on_press_key(self._get_primary_key(self.hotkey), self._on_key_down)
            kb.on_release_key(self._get_primary_key(self.hotkey), self._on_key_up)
        else:
            # 开关模式
            kb.add_hotkey(self.hotkey, self._toggle_recording)
        
        logger.info("热键监听启动完成")
        logger.info(f"请按住 '{self.hotkey}' 说话，松开自动识别输入")
        
        # 保持程序运行
        try:
            kb.wait("esc")  # 按 ESC 退出
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self):
        """停止热键监听"""
        print("🛑 停止热键监听...")
        kb.unhook_all()

    def _get_primary_key(self, hotkey: str) -> str:
        """从组合键中提取主按键（如 ctrl+alt+space → space）"""
        keys = hotkey.split("+")
        return keys[-1] if keys else hotkey

    def _on_key_down(self, event):
        """按键按下事件"""
        if event.event_type == kb.KEY_DOWN and not self.is_hotkey_pressed:
            # 检查是否所有的修饰键都按下了
            modifiers = self.hotkey.split("+")[:-1]
            if all(kb.is_pressed(mod) for mod in modifiers):
                self.is_hotkey_pressed = True
                self._start_recording()

    def _on_key_up(self, event):
        """按键释放事件"""
        if event.event_type == kb.KEY_UP and self.is_hotkey_pressed:
            self.is_hotkey_pressed = False
            self._stop_and_process()

    def _start_recording(self):
        """开始录音"""
        if self.is_processing:
            return
        
        print("🎤 开始录音...")
        self.recorder.start_recording()

    def _stop_and_process(self):
        """停止录音并处理识别结果"""
        if self.is_processing:
            return
        
        self.is_processing = True
        print("⏹️ 停止录音，开始识别...")
        
        # 在工作线程中处理，不阻塞UI
        process_thread = threading.Thread(target=self._process_recording)
        process_thread.daemon = True
        process_thread.start()

    def _process_recording(self):
        """处理录音：识别并输入文字"""
        try:
            # 1. 停止录音并保存文件
            audio_file = self.recorder.stop_recording()
            if not audio_file:
                self.is_processing = False
                return
            
            # 2. 识别语音
            text = self.recognizer.recognize_from_file(audio_file)
            
            # 3. 输入文字到当前光标位置
            if text and not text.startswith("❌"):
                self.typer.type_text(text)
            else:
                print(f"⚠️ 识别结果为空或有误: {text}")
            
        except Exception as e:
            print(f"❌ 处理录音时出错: {e}")
        finally:
            self.is_processing = False

    def _toggle_recording(self):
        """开关模式：按一次开始，再按一次停止"""
        if not self.is_hotkey_pressed:
            # 开始录音
            self.is_hotkey_pressed = True
            print("🎤 开始录音...")
            self.recorder.start_recording()
            # 提示用户再次按键停止
            print("💡 再次按下热键停止录音")
        else:
            # 停止并处理
            self.is_hotkey_pressed = False
            print("⏹️ 停止录音，开始识别...")
            self._stop_and_process()

    def test_hotkey(self):
        """测试热键功能"""
        print(f"🧪 测试热键 '{self.hotkey}'...")
        print("请按住热键说话，然后松开")
        print("按 ESC 退出测试")
        
        old_hotkey = self.hotkey
        test_hotkey = "f10"  # 使用 F10 测试
        
        print(f"临时改用 '{test_hotkey}' 测试")
        self.hotkey = test_hotkey
        
        try:
            self.start()
        finally:
            self.hotkey = old_hotkey

    def change_hotkey(self, new_hotkey: str):
        """修改热键"""
        try:
            # 验证热键格式
            self._validate_hotkey(new_hotkey)
            
            print(f"🔄 修改热键: {self.hotkey} → {new_hotkey}")
            self.stop()  # 停止当前监听
            
            self.hotkey = new_hotkey
            self.config["hotkey"] = new_hotkey
            from config import save_config
            save_config(self.config)
            
            # 重新启动监听
            self.start()
            return True
        except Exception as e:
            print(f"❌ 热键修改失败: {e}")
            return False

    def _validate_hotkey(self, hotkey: str):
        """验证热键格式"""
        if not hotkey:
            raise ValueError("热键不能为空")
        
        keys = hotkey.split("+")
        if len(keys) > 3:
            raise ValueError("热键最多包含3个键")
        
        # 检查主键是否有效
        primary_key = keys[-1].lower()
        valid_primary = ["space", "tab", "enter", "esc", "f1", "f2", "f3", "f4", 
                        "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
                        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", 
                        "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", 
                        "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", 
                        "7", "8", "9"]
        
        if primary_key not in valid_primary and not primary_key.startswith("f"):
            raise ValueError(f"无效的主键: {primary_key}")
        
        # 检查修饰键是否有效
        modifiers = keys[:-1]
        valid_modifiers = ["ctrl", "alt", "shift", "win"]
        for mod in modifiers:
            if mod.lower() not in valid_modifiers:
                raise ValueError(f"无效的修饰键: {mod}")

    def list_current_hotkeys(self):
        """列出当前注册的热键"""
        print("📋 当前热键配置:")
        print(f"    主热键: {self.hotkey} - {self.input_mode}")
        print("    退出键: ESC")
        
    def pause_hotkey(self, paused: bool = True):
        """暂停/恢复热键监听"""
        if paused:
            print("⏸️ 暂停热键监听")
            kb.unhook_all()
        else:
            print("▶️ 恢复热键监听")
            self.start()