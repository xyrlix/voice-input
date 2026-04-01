
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载 Qwen3-ASR-0.6B 模型
"""

import os
import sys
import time
from pathlib import Path

# 解决 urllib3 的 DEFAULT_CIPHERS 问题
import urllib3
if not hasattr(urllib3.util.ssl_, 'DEFAULT_CIPHERS'):
    urllib3.util.ssl_.DEFAULT_CIPHERS = 'DEFAULT'
print("✅ 已修复 urllib3 的 DEFAULT_CIPHERS 问题")

print(f"📦 开始下载 Qwen3-ASR-0.6B 模型...")
print(f"Python 版本: {sys.version}")
print(f"当前目录: {os.getcwd()}")

# 模型保存路径
MODEL_DIR = Path(__file__).parent / "data" / "models" / "qwen3-asr-0.6b"
print(f"💾 模型将保存到: {MODEL_DIR}")

# 创建目录
print(f"⏳ 创建目录: {MODEL_DIR}")
MODEL_DIR.mkdir(parents=True, exist_ok=True)
print(f"✅ 目录创建成功")

# 检查目录是否创建成功
if not MODEL_DIR.exists():
    print(f"❌ 目录创建失败: {MODEL_DIR}")
    sys.exit(1)

print(f"✅ 目录创建成功: {MODEL_DIR}")

# 尝试导入 transformers
print("⏳ 检查 transformers 库...")
try:
    print("  尝试导入 transformers...")
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
    print("  尝试导入 torch...")
    import torch
    print("✅ transformers 库导入成功")
    print(f"  transformers 版本: {__import__('transformers').__version__}")
    print(f"  torch 版本: {torch.__version__}")
except ImportError as e:
    print(f"❌ 导入 transformers 失败: {e}")
    print("请运行: pip install transformers torch")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 模型名称
MODEL_NAME = "Qwen/Qwen3-ASR-0.6B"

# 下载模型和处理器
try:
    # 检查模型是否已存在
    config_file = MODEL_DIR / "config.json"
    print(f"⏳ 检查模型文件: {config_file}")
    
    if not config_file.exists():
        print("⏳ 正在下载模型...")
        print(f"模型名称: {MODEL_NAME}")
        # 下载并保存模型
        print("⏳ 加载模型...")
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True
        )
        print("✅ 模型加载成功")
        
        print("⏳ 加载处理器...")
        processor = AutoProcessor.from_pretrained(MODEL_NAME)
        print("✅ 处理器加载成功")
        
        # 保存模型
        print("⏳ 保存模型...")
        model.save_pretrained(MODEL_DIR)
        print("✅ 模型保存成功")
        
        print("⏳ 保存处理器...")
        processor.save_pretrained(MODEL_DIR)
        print("✅ 处理器保存成功")
        
        print("✅ 模型下载完成！")
    else:
        print("✅ 模型已存在，跳过下载")
    
    # 测试加载模型
    print("⏳ 测试加载模型...")
    model = AutoModelForSpeechSeq2Seq.from_pretrained(MODEL_DIR)
    processor = AutoProcessor.from_pretrained(MODEL_DIR)
    print("✅ 模型加载成功！")
    print(f"📊 模型类型: {type(model)}")
    
    # 打印目录内容
    print("⏳ 模型目录内容:")
    for file in MODEL_DIR.iterdir():
        if file.is_file():
            size = file.stat().st_size / 1024 / 1024  # MB
            print(f"  - {file.name}: {size:.2f} MB")
    
    print("✅ 所有文件已创建成功")
    
except Exception as e:
    print(f"❌ 下载或加载模型失败: {e}")
    import traceback
    traceback.print_exc()

print("\n🎉 任务完成！")
