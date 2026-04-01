#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
录音模块
按住热键时录音，松开时保存到临时文件
"""

import threading
import time
import wave
import pyaudio
import numpy as np
from pathlib import Path
from config import DATA_DIR, get_config
import os

class AudioRecorder:
    def __init__(self):
        self.is_recording = False
        self.audio_frames = []
        self.recorder_thread = None
        self.config = get_config()
        
        # 音频参数
        self.sample_rate = self.config["sample_rate"]
        self.channels = self.config["channels"]
        self.chunk = 1024
        self.audio_format = pyaudio.paInt16
        
        # 初始化 PyAudio
        self.p = pyaudio.PyAudio()
        
        # 临时文件目录
        self.temp_dir = DATA_DIR / "temp"
        self.temp_dir.mkdir(exist_ok=True)
        
        print(f"✅ 录音模块初始化完成，采样率: {self.sample_rate}Hz")

    def get_audio_devices(self):
        """获取可用的音频输入设备"""
        devices = {}
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            if info["maxInputChannels"] > 0:
                devices[info["index"]] = f"{info['name']} (in: {info['maxInputChannels']})"
        return devices

    def start_recording(self):
        """开始录音"""
        if self.is_recording:
            print("⚠️ 已经在录音中")
            return False

        self.audio_frames = []
        self.is_recording = True
        
        # 创建录音线程
        self.recorder_thread = threading.Thread(target=self._recording_thread)
        self.recorder_thread.daemon = True
        self.recorder_thread.start()
        
        if self.config["enable_beep"]:
            self._play_start_sound()
        
        print("🎤 开始录音...")
        return True

    def stop_recording(self, save_to_temp: bool = True) -> str:
        """停止录音并保存到临时文件，返回文件路径或空字符串"""
        if not self.is_recording:
            return ""

        self.is_recording = False
        if self.recorder_thread:
            self.recorder_thread.join(timeout=1.0)
            self.recorder_thread = None

        if self.config["enable_beep"]:
            self._play_stop_sound()

        if not self.audio_frames:
            print("⚠️ 没有录音数据")
            return ""

        # 保存到临时文件
        if save_to_temp:
            temp_file = self._save_temp_file()
            duration = len(self.audio_frames) * self.chunk / self.sample_rate
            print(f"💾 录音已保存: {temp_file} ({duration:.1f}秒)")
            return temp_file
        else:
            return ""

    def _recording_thread(self):
        """录音线程主循环"""
        try:
            # 打开音频流
            stream = self.p.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk,
                input_device_index=self.config.get("audio_device")
            )

            # 直接录音，不做任何过滤
            self.audio_frames = []
            
            # 录制循环
            while self.is_recording:
                try:
                    data = stream.read(self.chunk, exception_on_overflow=False)
                    self.audio_frames.append(data)
                except Exception as e:
                    print(f"⚠️ 录音数据读取失败: {e}")
                    time.sleep(0.01)

            # 停止并关闭流
            stream.stop_stream()
            stream.close()

        except Exception as e:
            print(f"❌ 录音线程异常: {e}")
            self.is_recording = False

    def _save_temp_file(self) -> str:
        """保存录音数据为临时 WAV 文件"""
        import uuid
        filename = f"temp_{int(time.time())}_{uuid.uuid4().hex[:8]}.wav"
        temp_path = self.temp_dir / filename

        with wave.open(str(temp_path), 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.audio_format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(self.audio_frames))

        return str(temp_path)

    def _play_start_sound(self):
        """播放开始录音提示音（440Hz, 0.1秒）"""
        try:
            duration = 0.1
            frequency = 440  # A4音
            fs = 44100
            t = np.linspace(0, duration, int(fs * duration), False)
            wave_data = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)

            stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=fs,
                output=True
            )
            stream.write(wave_data.tobytes())
            stream.stop_stream()
            stream.close()
        except Exception as e:
            pass  # 无声提示不影响主要功能

    def _play_stop_sound(self):
        """播放停止录音提示音（880Hz, 0.1秒）"""
        try:
            duration = 0.1
            frequency = 880  # A5音
            fs = 44100
            t = np.linspace(0, duration, int(fs * duration), False)
            wave_data = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)

            stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=fs,
                output=True
            )
            stream.write(wave_data.tobytes())
            stream.stop_stream()
            stream.close()
        except Exception as e:
            pass

    def cleanup_old_temp_files(self, max_age_hours: int = 24):
        """清理旧的临时文件"""
        try:
            current_time = time.time()
            for file in self.temp_dir.glob("temp_*.wav"):
                if current_time - file.stat().st_mtime > max_age_hours * 3600:
                    file.unlink()
        except Exception as e:
            pass

    def __del__(self):
        """释放资源"""
        try:
            self.p.terminate()
        except:
            pass