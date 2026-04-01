#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统托盘图标
提供后台运行和快捷设置
"""

import threading
import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageDraw
from pathlib import Path
import pystray
import sys
import os

from config import get_config, config_to_str, save_config

class TrayIcon:
    def __init__(self, hotkey_manager=None):
        self.hotkey_manager = hotkey_manager
        self.config = get_config()
        self.icon = None
        self.running = True
        
        # 创建托盘图标
        self.create_icon()
        
    def create_icon(self):
        """创建托盘图标"""
        # 创建一个简单的圆形图标（麦克风）
        image = Image.new('RGBA', (64, 64), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        
        # 绘制麦克风图标
        center = (32, 32)
        radius = 24
        
        # 麦克风主体
        draw.ellipse([center[0]-radius, center[1]-radius, 
                     center[0]+radius, center[1]+radius], 
                    fill=(0, 120, 212, 255), outline=(0, 90, 158, 255))
        
        # 麦克风网头
        inner_radius = radius - 8
        draw.ellipse([center[0]-inner_radius, center[1]-inner_radius,
                     center[0]+inner_radius, center[1]+inner_radius],
                    fill=(255, 255, 255, 180), outline=(200, 200, 200, 200))
        
        # 中央点
        draw.ellipse([center[0]-4, center[1]-4, center[0]+4, center[1]+4],
                    fill=(0, 90, 158, 255))
        
        # 创建菜单
        menu = (
            pystray.MenuItem("🔄 重新加载配置", self.reload_config),
            pystray.MenuItem("🎤 测试录音", self.test_recording),
            pystray.MenuItem("⌨️ 测试输入", self.test_typing),
            pystray.MenuItem("⚙️ 修改热键", self.change_hotkey),
            pystray.MenuItem("📊 查看配置", self.show_config),
            pystray.MenuItem("📝 编辑配置", self.edit_config),
            pystray.MenuItem("---", None),
            pystray.MenuItem("❓ 帮助", self.show_help),
            pystray.MenuItem("🚪 退出", self.exit_app)
        )
        
        self.icon = pystray.Icon("voice_input", image, "语音输入法", menu)
    
    def run(self):
        """运行托盘图标（阻塞）"""
        print("📢 语音输入法已启动，在系统托盘查看")
        print("💡 右键点击托盘图标可以打开设置菜单")
        
        # 在后台线程中运行托盘图标
        tray_thread = threading.Thread(target=self._run_tray)
        tray_thread.daemon = True
        tray_thread.start()
        
    def _run_tray(self):
        """运行托盘图标的内部方法"""
        try:
            self.icon.run()
        except Exception as e:
            print(f"❌ 托盘图标运行失败: {e}")
    
    def reload_config(self, icon=None, item=None):
        """重新加载配置"""
        from config import load_config
        self.config = load_config()
        if self.hotkey_manager:
            self.hotkey_manager.config = self.config
        print("✅ 配置已重新加载")
        messagebox.showinfo("语音输入法", "配置已重新加载")
    
    def test_recording(self, icon=None, item=None):
        """测试录音功能"""
        # 这里应该导入并测试录音模块
        print("🎤 测试录音功能...")
        messagebox.showinfo("测试", "测试录音功能 - 请检查控制台输出")
    
    def test_typing(self, icon=None, item=None):
        """测试输入功能"""
        # 这里应该导入并测试打字模块
        print("⌨️ 测试输入功能...")
        messagebox.showinfo("测试", "测试输入功能 - 请检查控制台输出")
    
    def change_hotkey(self, icon=None, item=None):
        """修改热键"""
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        current_hotkey = self.config.get("hotkey", "ctrl+alt+space")
        new_hotkey = simpledialog.askstring(
            "修改热键",
            f"当前热键: {current_hotkey}\n\n请输入新的热键组合 (如: ctrl+alt+space):",
            initialvalue=current_hotkey
        )
        
        if new_hotkey and new_hotkey != current_hotkey:
            try:
                # 验证热键格式
                from hotkey_manager import HotkeyManager
                mgr = HotkeyManager(None, None, None)
                mgr._validate_hotkey(new_hotkey)
                
                self.config["hotkey"] = new_hotkey
                save_config(self.config)
                
                # 如果hotkey_manager存在，更新它
                if self.hotkey_manager:
                    self.hotkey_manager.change_hotkey(new_hotkey)
                
                messagebox.showinfo("成功", f"热键已修改为: {new_hotkey}")
                print(f"✅ 热键已修改: {new_hotkey}")
            except Exception as e:
                messagebox.showerror("错误", f"热键修改失败: {str(e)}")
    
    def show_config(self, icon=None, item=None):
        """显示当前配置"""
        config_text = config_to_str(self.config)
        messagebox.showinfo("当前配置", config_text)
        print("📋 显示配置信息:")
        print(config_text)
    
    def edit_config(self, icon=None, item=None):
        """编辑配置文件"""
        config_file = Path(__file__).parent / "data" / "config.json"
        try:
            os.startfile(str(config_file))
            print(f"📝 打开配置文件: {config_file}")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开配置文件: {str(e)}")
    
    def show_help(self, icon=None, item=None):
        """显示帮助信息"""
        help_text = """🎤 语音输入法使用说明

📌 主要功能：
• 按住热键说话，松开自动识别并输入文字
• 支持中文/英文识别
• 支持本地离线识别（无需网络）

🎯 使用方法：
1. 程序启动后会在系统托盘显示图标
2. 默认热键：Ctrl+Alt+Space
3. 按住热键说话，松开键自动识别

⚙️ 配置方式：
• 右键托盘图标打开菜单
• 可以修改热键、查看配置
• 配置文件在 data/config.json

📋 常见问题：
• 识别不准：尝试减慢语速，清晰发音
• 没有声音：检查麦克风是否正常工作
• 无法识别：Whisper模型需要下载，第一次会较慢

💡 提示：
• 识别模型越大越准，但速度越慢
• 可切换打字模式或剪贴板模式
"""
        messagebox.showinfo("语音输入法帮助", help_text)
    
    def exit_app(self, icon=None, item=None):
        """退出应用程序"""
        self.running = False
        if self.hotkey_manager:
            try:
                self.hotkey_manager.stop()
            except:
                pass
        
        print("👋 正在退出语音输入法...")
        self.icon.stop()
        
        # 如果是主线程，退出程序
        if threading.current_thread() is threading.main_thread():
            sys.exit(0)
        else:
            # 在托盘线程中退出
            import os
            os._exit(0)
    
    def update_status(self, status_text: str):
        """更新托盘图标状态提示"""
        if self.icon:
            self.icon.title = f"语音输入法 - {status_text}"
            print(f"📢 状态更新: {status_text}")
    
    def show_notification(self, title: str, message: str):
        """显示系统通知"""
        try:
            if self.icon:
                self.icon.notify(message, title)
        except Exception as e:
            print(f"❌ 通知发送失败: {e}")
    
    def get_menu_items(self):
        """获取当前菜单项"""
        return self.icon.menu.items if self.icon else []

def create_default_tray():
    """创建默认的托盘图标（无功能引用）"""
    icon = TrayIcon()
    return icon

if __name__ == "__main__":
    # 独立运行测试托盘
    icon = TrayIcon()
    icon.run()