#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文字输入模块
将识别到的文字插入到当前光标位置
支持两种模式：模拟键盘打字 或 复制粘贴
"""

import time
import pyautogui
import pyperclip
import keyboard as kb
from config import get_config
import threading

class TextTyper:
    def __init__(self):
        self.config = get_config()
        self.typing_speed = self.config["typing_speed"]
        self.output_method = self.config["output_method"]
        
        # 安全设置
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = self.typing_speed
        
        print(f"⌨️ 文字输入模块初始化，模式: {self.output_method}")

    def type_text(self, text: str):
        """根据配置的方式输入文字"""
        if not text:
            return False

        # 移除错误信息
        if text.startswith("❌"):
            print(f"⚠️ 识别失败，不输入: {text}")
            return False

        print(f"💬 准备输入: {text}")
        
        if self.output_method == "typing":
            return self._type_by_keyboard(text)
        elif self.output_method == "clipboard":
            return self._type_by_clipboard(text)
        else:
            print(f"❌ 未知的输出方式: {self.output_method}")
            return False

    def _type_by_keyboard(self, text: str) -> bool:
        """模拟键盘打字（逐字符输入）"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # 记录原始位置
            original_pos = pyautogui.position()
            logger.info(f"当前鼠标位置: {original_pos}")
            
            # 等待确保用户释放了热键，并且目标窗口准备好接收输入
            time.sleep(0.3)
            
            logger.info(f"开始逐字符输入: {text}")
            
            # 逐个字符输入
            for i, char in enumerate(text):
                try:
                    # 处理特殊字符
                    if char == "\n":
                        pyautogui.press("enter")
                    elif char == "\t":
                        pyautogui.press("tab")
                    else:
                        pyautogui.write(char, interval=self.typing_speed)
                    
                    # 每输入3个字符后短暂休息，防止丢失
                    if i > 0 and i % 3 == 0:
                        time.sleep(0.02)
                        
                except pyautogui.FailSafeException:
                    logger.warning("触发了安全保护，输入中断")
                    return False
                except Exception as e:
                    logger.warning(f"输入字符失败: {char}, 错误: {e}")
                    continue
            
            logger.info(f"打字完成: {len(text)} 字符")
            return True
            
        except Exception as e:
            logger.error(f"键盘输入失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _type_by_clipboard(self, text: str) -> bool:
        """使用剪贴板复制粘贴"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # 先保存当前剪贴板内容
            try:
                old_clipboard = pyperclip.paste()
            except:
                old_clipboard = ""
            
            logger.info(f"复制到剪贴板: {text}")
            
            # 复制识别文本到剪贴板
            pyperclip.copy(text)
            
            # 等待剪贴板同步
            time.sleep(0.1)
            
            # 检查剪贴板内容是否正确
            current = pyperclip.paste()
            if current != text:
                logger.warning("剪贴板复制失败，回退到键盘输入")
                return self._type_by_keyboard(text)
            
            # 记录原始位置
            original_pos = pyautogui.position()
            logger.info(f"当前鼠标位置: {original_pos}")
            
            # 等待一小段时间
            time.sleep(0.2)
            
            # 粘贴 (Ctrl+V)
            logger.info("执行 Ctrl+V 粘贴")
            pyautogui.hotkey("ctrl", "v")
            
            # 可选：恢复原剪贴板内容
            time.sleep(0.15)
            if old_clipboard:
                try:
                    pyperclip.copy(old_clipboard)
                except:
                    pass
            
            logger.info(f"粘贴完成: {len(text)} 字符")
            return True
            
        except Exception as e:
            logger.error(f"剪贴板粘贴失败: {e}")
            import traceback
            traceback.print_exc()
            # 尝试用键盘输入作为备选
            return self._type_by_keyboard(text)

    def insert_with_timing(self, text: str, delay: float = None):
        """带延迟的输入（可选的）"""
        if delay:
            time.sleep(delay)
        return self.type_text(text)

    def test_typing(self):
        """测试输入功能"""
        print("🧪 测试文字输入...")
        test_text = "语音输入法测试 Hello 123"
        return self.type_text(test_text)

    def set_output_method(self, method: str):
        """设置输出方式"""
        valid_methods = ["typing", "clipboard"]
        if method in valid_methods:
            if method != self.output_method:
                print(f"🔄 切换输出方式: {self.output_method} → {method}")
                self.output_method = method
                self.config["output_method"] = method
                from config import save_config
                save_config(self.config)
            return True
        else:
            print(f"❌ 无效的输出方式，可选: {', '.join(valid_methods)}")
            return False

    def set_typing_speed(self, speed: float):
        """设置打字速度（秒/字符）"""
        if 0.001 <= speed <= 1.0:
            self.typing_speed = speed
            pyautogui.PAUSE = speed
            self.config["typing_speed"] = speed
            from config import save_config
            save_config(self.config)
            print(f"⚙️ 打字速度设置为: {speed}秒/字符")
            return True
        else:
            print("❌ 打字速度需要在 0.001-1.0 秒之间")
            return False

    def pause_for_user_input(self, seconds: float = 0.5):
        """暂停，等待用户交互"""
        time.sleep(seconds)

    def type_with_cursor_follow(self, text: str):
        """输入后保持光标在文字末尾"""
        if not self.type_text(text):
            return False
        
        # 对于键盘输入模式，可以尝试移动光标到末尾
        if self.output_method == "typing":
            # 假设用户不会移动光标，所以不需要额外处理
            pass
        
        return True

# 全局实例
_typer = None

def get_typer():
    """获取全局 TextTyper 实例"""
    global _typer
    if _typer is None:
        _typer = TextTyper()
    return _typer