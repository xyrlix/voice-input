#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音输入法主程序
"""

import sys
import os
import signal
import traceback
from pathlib import Path

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

import logging
from pathlib import Path

LOG_FILE = Path(__file__).parent / "data" / "voice_input.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# 减少Pillow日志噪音
logging.getLogger('PIL').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

def setup_signal_handlers():
    """设置信号处理器，优雅退出"""
    def signal_handler(sig, frame):
        print(f"\n📢 收到信号 {sig}，正在退出...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def print_banner():
    """打印欢迎信息"""
    logger.info("=" * 60)
    logger.info("语音输入法 v1.0 启动中...")
    logger.info("功能：按住热键说话 → 自动识别 → 输入到光标处")
    logger.info("=" * 60)

def print_usage():
    """打印使用说明"""
    print("\n📋 使用方式:")
    print("  1. python main.py               # 启动语音输入法")
    print("  2. python main.py --config      # 查看当前配置")
    print("  3. python main.py --test        # 测试各模块功能")
    print("  4. python main.py --help        # 显示帮助信息")
    print("\n🎯 操作提示:")
    print("  • 按住 Ctrl+Alt+Space 说话，松开自动识别")
    print("  • 右键系统托盘图标可以修改设置")
    print("  • 按 ESC 键退出程序")

def test_all_modules():
    """测试所有模块"""
    print("🧪 开始测试所有模块...")
    
    try:
        # 导入模块
        from config import get_config, config_to_str
        from recorder import AudioRecorder
        from recognizer import VoiceRecognizer
        from text_typing import get_typer
        
        # 测试配置
        config = get_config()
        print("✅ 配置模块正常")
        print(config_to_str(config))
        
        # 测试录音模块
        recorder = AudioRecorder()
        print("✅ 录音模块初始化正常")
        
        # 测试识别模块
        recognizer = VoiceRecognizer()
        print("✅ 识别模块初始化正常")
        
        # 测试输入模块
        typer = get_typer()
        print("✅ 输入模块初始化正常")
        
        # 列出录音设备
        devices = recorder.get_audio_devices()
        if devices:
            print("🎧 可用的录音设备:")
            for idx, name in devices.items():
                print(f"  [{idx}] {name}")
        else:
            print("⚠️ 未找到录音设备，请检查麦克风")
        
        # 列出 Whisper 模型
        models = recognizer.list_available_models()
        
        print("\n🎉 所有模块测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    # 处理命令行参数
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["-h", "--help", "help"]:
            print_usage()
            return
        elif arg in ["-c", "--config"]:
            from config import config_to_str
            print(config_to_str())
            return
        elif arg in ["-t", "--test"]:
            test_all_modules()
            return
        elif arg in ["-v", "--version"]:
            print("语音输入法 v1.0")
            return
    
    # 正常启动
    print_banner()
    setup_signal_handlers()
    
    # 检查依赖
    logger.info("检查依赖...")
    try:
        import keyboard
        import pyautogui
        import pyperclip
        logger.info("基础依赖已安装")
    except ImportError as e:
        logger.error(f"缺少依赖: {e}")
        logger.info("请运行: pip install -r requirements.txt")
        return
    
    # 测试模块
    if not test_all_modules():
        logger.error("模块测试失败")
        return
    
    logger.info("正在启动语音输入法...")
    
    try:
        # 导入所有模块
        from recorder import AudioRecorder
        from recognizer import VoiceRecognizer
        from text_typing import get_typer
        from hotkey_manager import HotkeyManager
        from tray_icon import TrayIcon
        
        # 初始化模块
        recorder = AudioRecorder()
        recognizer = VoiceRecognizer()
        typer = get_typer()
        
        # 启动热键管理器
        hotkey_manager = HotkeyManager(recorder, recognizer, typer)
        
        # 启动托盘图标（在后台线程）
        tray = TrayIcon(hotkey_manager)
        
        # 在单独的线程中运行托盘
        import threading
        tray_thread = threading.Thread(target=tray.run)
        tray_thread.daemon = True
        tray_thread.start()
        
        # 显示启动成功信息
        from config import get_config
        config = get_config()
        hotkey = config.get("hotkey", "ctrl+alt+space")
        
        print(f"\n✅ 语音输入法启动成功！")
        print(f"🎯 使用方法：按住 {hotkey} 说话，松开自动识别")
        print("📢 程序将在后台运行，右键系统托盘图标可修改设置")
        print("💡 按 ESC 键退出程序\n")
        
        # 启动热键监听（主线程阻塞在这里）
        hotkey_manager.start()
        
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")
        traceback.print_exc()
        print("\n💡 可能的问题：")
        print("1. 检查是否安装了 Whisper: pip install openai-whisper")
        print("2. 检查麦克风是否正常工作")
        print("3. 以管理员权限运行（如果需要全局热键）")
        
        input("\n按 Enter 键退出...")
        sys.exit(1)

def check_dependencies():
    """检查并安装依赖"""
    print("🔧 检查依赖...")
    
    # 检查是否安装了必要的包
    required = ["keyboard", "pyautogui", "pyperclip", "Pillow"]
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ 缺少依赖: {', '.join(missing)}")
        print("正在尝试安装...")
        
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print("✅ 依赖安装成功")
        except Exception as e:
            print(f"❌ 依赖安装失败: {e}")
            print("请手动运行: pip install keyboard pyautogui pyperclip Pillow")
            return False
    
    print("✅ 所有依赖已安装")
    return True

if __name__ == "__main__":
    # 检查工作目录
    if not os.path.exists("requirements.txt"):
        print("⚠️ 请在项目根目录运行此程序")
        print(f"当前目录: {os.getcwd()}")
        print(f"请切换到: {Path(__file__).parent}")
        
        # 尝试自动切换到项目目录
        try:
            os.chdir(Path(__file__).parent)
            print(f"已切换到: {os.getcwd()}")
        except:
            pass
    
    # 如果第一次运行，检查依赖
    if not Path("data").exists():
        print("📁 第一次运行，正在初始化...")
        
    main()