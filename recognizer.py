#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音识别模块
使用 OpenAI Whisper 进行本地识别
"""

import time
import subprocess
import warnings
from pathlib import Path
from config import MODEL_DIR, get_config
import os


class VoiceRecognizer:

    def __init__(self):
        self.config = get_config()
        self.model = None
        self.model_loaded = False
        self.model_size = self.config["model_name"]
        self.language = self.config["language"]

        # Whisper模型文件路径
        model_name_map = {
            "tiny": "tiny" if self.language == "zh" else "tiny.en",
            "base": "base" if self.language == "zh" else "base.en",
            "small": "small" if self.language == "zh" else "small.en",
            "medium": "medium",
            "large": "large",
        }
        self.model_file = model_name_map.get(self.model_size, "tiny")

        print(f"🧠 语音识别器初始化，模型: {self.model_file}，语言: {self.language}")

    def load_model(self):
        """加载 Whisper 模型"""
        if self.model_loaded:
            return True

        print("⏳ 加载 Whisper 模型...")
        start_time = time.time()

        try:
            # 尝试加载 whisper (openai-whisper)
            import whisper
            print(f"✅ Whisper库版本: {whisper.__version__}")
        except ImportError:
            print("❌ 未安装 Whisper 库")
            print("   请运行: pip install -U openai-whisper")
            print(
                "   或: pip install git+https://github.com/openai/whisper.git")
            return False

        try:
            # 加载模型
            # 使用 fp16=False 确保在 CPU 上也能快速运行
            self.model = whisper.load_model(self.model_file,
                                            download_root=str(MODEL_DIR),
                                            device="cpu")
            self.model_loaded = True
            load_time = time.time() - start_time
            print(f"✅ 模型加载完成，耗时: {load_time:.1f}秒")
            return True
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            print("   可能原因:")
            print("   1. 网络问题，无法下载模型")
            print("   2. 磁盘空间不足（模型需要几百MB到几GB）")
            print("   3. torch/cuda 版本不兼容")
            return False

    def recognize_from_file(self, audio_path: str) -> str:
        """从音频文件识别文字"""
        if not os.path.exists(audio_path):
            return f"❌ 音频文件不存在: {audio_path}"

        if not self.load_model():
            return "❌ Whisper 模型未加载"

        print(f"🔍 开始识别: {os.path.basename(audio_path)}")
        start_time = time.time()

        try:
            # 使用 scipy 加载音频，避免依赖 ffmpeg
            from scipy.io import wavfile
            import numpy as np

            sample_rate, audio_data = wavfile.read(audio_path)

            # 转换为 float32 并归一化
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32768.0
            elif audio_data.dtype == np.int32:
                audio_data = audio_data.astype(np.float32) / 2147483648.0

            # 如果是立体声，转为单声道
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)

            # 自动增益：如果音量太小，放大到合适水平
            max_val = np.max(np.abs(audio_data))
            target_level = 0.5  # 目标50%音量
            if max_val < target_level and max_val > 0:
                gain = target_level / max_val
                gain = min(gain, 15)  # 最多放大15倍
                audio_data = audio_data * gain
                print(f"🔊 已应用增益: {gain:.1f}x")

            # 重采样到 16000Hz（如果需要）
            if sample_rate != 16000:
                import scipy.signal
                num_samples = int(len(audio_data) * 16000 / sample_rate)
                audio_data = scipy.signal.resample(audio_data, num_samples)
                sample_rate = 16000

            # 使用 whisper 转录
            result = self.model.transcribe(
                audio_data,
                language=self.language if self.language != "auto" else None,
                task="transcribe",
                fp16=False,
            )

            text = result["text"].strip()
            duration = time.time() - start_time

            # 简单标点修正
            if self.config["auto_punctuation"]:
                text = self._auto_punctuation(text)

            # 繁体转简体
            if self.language == "zh":
                text = self.convert_to_simplified(text)

            print(f"✅ 识别完成: {text[:60]}{'...' if len(text) > 60 else ''}")
            print(
                f"   ⏱️ 耗时: {duration:.1f}秒，置信度: {result.get('confidence', 0):.2%}"
            )

            return text

        except Exception as e:
            print(f"❌ 识别过程出错: {e}")
            import traceback
            traceback.print_exc()
            return f"❌ 识别失败: {str(e)}"

    def recognize_from_bytes(self,
                             audio_data: bytes,
                             sample_rate: int = 16000) -> str:
        """从音频字节数据直接识别（无需保存文件）"""
        if not self.load_model():
            return "❌ Whisper 模型未加载"

        try:
            import whisper
            import numpy as np
            import io

            # 将字节数据转换为 numpy 数组
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(
                np.float32) / 32768.0

            result = self.model.transcribe(
                audio_array,
                language=self.language if self.language != "auto" else None,
                task="transcribe",
                fp16=False,
            )

            text = result["text"].strip()
            if self.config["auto_punctuation"]:
                text = self._auto_punctuation(text)

            return text

        except Exception as e:
            print(f"❌ 字节数据识别失败: {e}")
            return f"❌ 识别失败: {str(e)}"

    def _auto_punctuation(self, text: str) -> str:
        """简单的中文标点自动修正"""
        if not text:
            return text

        # 移除首尾空格
        text = text.strip()

        # 确保以句号或问号结束
        if text and text[-1] not in "。！？.!?":
            # 根据内容判断是陈述句还是疑问句
            if any(q in text for q in ["吗", "呢", "吧", "？", "?"]):
                text += "？"
            else:
                text += "。"

        # 自动添加书名号（如果检测到可能是书名）
        if "《" not in text and "》" not in text:
            # 简单的书名检测（包含前后文的书名，如"我看了平凡的世界"）
            pass  # TODO: 实现更智能的标点

        return text

    def convert_to_simplified(self, text: str) -> str:
        """繁体中文转简体中文"""
        if not text or self.language != "zh":
            return text

        try:
            import opencc
            converter = opencc.OpenCC('t2s')
            return converter.convert(text)
        except Exception:
            return text

    def select_model_size(self, size_name: str) -> bool:
        """切换模型大小"""
        valid_sizes = ["tiny", "base", "small", "medium", "large"]
        if size_name not in valid_sizes:
            print(f"❌ 无效的模型大小，可选: {', '.join(valid_sizes)}")
            return False

        if size_name == self.model_size:
            return True

        print(f"🔄 切换模型: {self.model_size} → {size_name}")
        self.model_size = size_name
        self.model_loaded = False
        self.model = None

        # 更新配置
        self.config["model_name"] = size_name
        from config import save_config
        save_config(self.config)

        return True

    def list_available_models(self):
        """列出本地已下载的模型"""
        try:
            files = list(MODEL_DIR.glob("*.pt"))
            models = [f.stem for f in files]
            if models:
                print(f"📦 本地已有模型: {', '.join(models)}")
            else:
                print("📦 本地无模型文件，第一次使用时会自动下载")
            return models
        except Exception as e:
            print(f"❌ 检查模型文件失败: {e}")
            return []

    def cleanup_cache(self):
        """清理临时文件"""
        try:
            temp_dir = MODEL_DIR / ".cache"
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                print("✅ 已清理模型缓存")
        except Exception as e:
            pass

    def __del__(self):
        """释放资源"""
        if hasattr(self, "model") and self.model:
            try:
                import gc
                self.model = None
                gc.collect()
            except:
                pass
