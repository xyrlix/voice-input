
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 降噪模块
用于降低音频中的背景噪音，提高语音识别质量
"""

import numpy as np
from scipy.io import wavfile

class AudioDenoiser:
    def __init__(self, reduction_strength=0.8):
        """初始化降噪器
        
        Args:
            reduction_strength: 降噪强度，0-1，值越大降噪效果越强
        """
        self.reduction_strength = reduction_strength

    def denoise(self, audio_data, sample_rate):
        """对音频数据进行降噪处理
        
        Args:
            audio_data: 音频数据，numpy 数组
            sample_rate: 采样率
        
        Returns:
            numpy.ndarray: 降噪后的音频数据
        """
        try:
            import noisereduce as nr
            print("🔇 开始降噪处理...")
            
            # 确保音频数据是 float32 格式
            if audio_data.dtype != np.float32:
                if audio_data.dtype == np.int16:
                    # 转换为 float32
                    audio_data = audio_data.astype(np.float32) / 32768.0
                else:
                    raise ValueError("音频数据必须是 int16 或 float32 格式")
            
            # 执行降噪
            denoised_data = nr.reduce_noise(
                y=audio_data,
                sr=sample_rate,
                prop_decrease=self.reduction_strength,
                time_mask_smooth_ms=120,
                freq_mask_smooth_hz=100
            )
            
            print("✅ 降噪完成")
            return denoised_data
            
        except ImportError:
            print("⚠️ noisereduce 库未安装，跳过降噪")
            return audio_data
        except Exception as e:
            print(f"❌ 降噪过程出错: {e}")
            return audio_data

    def process_wav_file(self, wav_path, output_path=None):
        """处理 WAV 文件，进行降噪
        
        Args:
            wav_path: 输入 WAV 文件路径
            output_path: 输出 WAV 文件路径，如果为 None 则返回音频数据
        
        Returns:
            numpy.ndarray: 降噪后的音频数据（如果 output_path 为 None）
        """
        # 读取 WAV 文件
        sample_rate, audio_data = wavfile.read(wav_path)
        
        # 降噪
        denoised_data = self.denoise(audio_data, sample_rate)
        
        # 转换回 int16 格式
        denoised_data_int16 = (denoised_data * 32768).astype(np.int16)
        
        # 保存到文件
        if output_path:
            wavfile.write(output_path, sample_rate, denoised_data_int16)
            return denoised_data
        else:
            return denoised_data

# 测试降噪功能
if __name__ == "__main__":
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="AI 降噪工具")
    parser.add_argument("input_file", help="输入 WAV 文件路径")
    parser.add_argument("-o", "--output", help="输出 WAV 文件路径")
    parser.add_argument("-s", "--strength", type=float, default=0.8, help="降噪强度 (0-1)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"错误: 文件 {args.input_file} 不存在")
        exit(1)
    
    # 初始化降噪器
    denoiser = AudioDenoiser(reduction_strength=args.strength)
    
    # 处理文件
    output_path = args.output if args.output else args.input_file.replace(".wav", "_denoised.wav")
    denoised_data = denoiser.process_wav_file(args.input_file, output_path)
    
    print(f"✅ 处理完成！")
    print(f"📁 输入文件: {args.input_file}")
    print(f"📁 输出文件: {output_path}")
    print(f"📊 音频长度: {len(denoised_data)} 样本")
