
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VAD (Voice Activity Detection) 静音裁剪模块
用于检测并裁剪录音中的静音部分
"""

import numpy as np
from scipy.io import wavfile

class VoiceActivityDetector:
    def __init__(self, threshold=0.05):
        """初始化 VAD 检测器
        
        Args:
            threshold: 语音检测阈值，0-1，值越大检测越严格
        """
        self.threshold = threshold
        self.sample_rate = 16000  # 默认采样率

    def detect_voice_segments(self, audio_data, sample_rate):
        """检测音频中的语音段（基于能量的简单 VAD）
        
        Args:
            audio_data: 音频数据，numpy 数组
            sample_rate: 采样率
        
        Returns:
            list: 语音段的起始和结束索引列表 [(start1, end1), (start2, end2), ...]
        """
        # 确保音频数据是 float32 格式
        if audio_data.dtype != np.float32:
            if audio_data.dtype == np.int16:
                # 转换为 float32
                audio_data = audio_data.astype(np.float32) / 32768.0
            else:
                raise ValueError("音频数据必须是 int16 或 float32 格式")
        
        # 计算帧长（20ms）
        frame_duration_ms = 20
        frame_size = int(sample_rate * frame_duration_ms / 1000)
        hop_size = frame_size // 2  # 50% 重叠
        
        # 计算每帧的能量
        energy = []
        for i in range(0, len(audio_data) - frame_size, hop_size):
            frame = audio_data[i:i+frame_size]
            frame_energy = np.sqrt(np.mean(frame**2))
            energy.append(frame_energy)
        
        # 检测语音段
        voice_segments = []
        current_segment = None
        
        for i, e in enumerate(energy):
            if e > self.threshold and current_segment is None:
                # 开始一个新的语音段
                current_segment = i * hop_size
            elif e <= self.threshold and current_segment is not None:
                # 结束当前语音段
                end = i * hop_size
                voice_segments.append((current_segment, end))
                current_segment = None
        
        # 处理最后一个语音段
        if current_segment is not None:
            voice_segments.append((current_segment, len(audio_data)))
        
        return voice_segments

    def crop_silence(self, audio_data, sample_rate, min_segment_length=1000):
        """裁剪音频中的静音部分
        
        Args:
            audio_data: 音频数据，numpy 数组
            sample_rate: 采样率
            min_segment_length: 最小语音段长度（毫秒）
        
        Returns:
            numpy.ndarray: 裁剪后的音频数据
        """
        # 检测语音段
        segments = self.detect_voice_segments(audio_data, sample_rate)
        
        if not segments:
            return audio_data  # 没有检测到语音，返回原始数据
        
        # 过滤掉太短的语音段
        min_segment_samples = int(sample_rate * min_segment_length / 1000)
        filtered_segments = []
        
        for start, end in segments:
            if end - start >= min_segment_samples:
                filtered_segments.append((start, end))
        
        if not filtered_segments:
            return audio_data  # 没有足够长的语音段，返回原始数据
        
        # 合并相邻的语音段
        merged_segments = []
        current_start, current_end = filtered_segments[0]
        
        for start, end in filtered_segments[1:]:
            # 如果两个段之间的间隔小于 100ms，合并它们
            if start - current_end < int(sample_rate * 0.1):
                current_end = end
            else:
                merged_segments.append((current_start, current_end))
                current_start, current_end = start, end
        
        merged_segments.append((current_start, current_end))
        
        # 提取语音段
        voice_data = []
        for start, end in merged_segments:
            voice_data.append(audio_data[start:end])
        
        # 合并语音段
        if voice_data:
            return np.concatenate(voice_data)
        else:
            return audio_data

    def process_wav_file(self, wav_path, output_path=None):
        """处理 WAV 文件，裁剪静音部分
        
        Args:
            wav_path: 输入 WAV 文件路径
            output_path: 输出 WAV 文件路径，如果为 None 则返回音频数据
        
        Returns:
            numpy.ndarray: 裁剪后的音频数据（如果 output_path 为 None）
        """
        # 读取 WAV 文件
        sample_rate, audio_data = wavfile.read(wav_path)
        
        # 裁剪静音
        cropped_data = self.crop_silence(audio_data, sample_rate)
        
        # 保存到文件
        if output_path:
            wavfile.write(output_path, sample_rate, cropped_data)
            return cropped_data
        else:
            return cropped_data

# 测试 VAD 功能
if __name__ == "__main__":
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="VAD 静音裁剪工具")
    parser.add_argument("input_file", help="输入 WAV 文件路径")
    parser.add_argument("-o", "--output", help="输出 WAV 文件路径")
    parser.add_argument("-a", "--aggressiveness", type=int, default=3, help="VAD 检测激进程度 (0-3)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"错误: 文件 {args.input_file} 不存在")
        exit(1)
    
    # 初始化 VAD
    vad = VoiceActivityDetector(aggressiveness=args.aggressiveness)
    
    # 处理文件
    output_path = args.output if args.output else args.input_file.replace(".wav", "_cropped.wav")
    cropped_data = vad.process_wav_file(args.input_file, output_path)
    
    print(f"✅ 处理完成！")
    print(f"📁 输入文件: {args.input_file}")
    print(f"📁 输出文件: {output_path}")
    print(f"📊 原始长度: {len(wavfile.read(args.input_file)[1])} 样本")
    print(f"📊 裁剪后长度: {len(cropped_data)} 样本")
