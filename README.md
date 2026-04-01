# 语音输入法 v1.0

一个基于本地模型的语音输入法，支持中文和英文语音识别，无需网络连接，保护用户隐私。

## 功能特点

- **本地离线识别**：使用 Whisper 或 Qwen3-ASR-0.6B 模型进行本地语音识别，无需网络连接
- **热键控制**：默认使用 Ctrl+Alt+Space 触发录音，松开后自动识别
- **智能处理**：内置 VAD 静音裁剪和 AI 降噪功能，提高识别准确率
- **自动标点**：自动为识别结果添加标点符号
- **剪贴板输入**：识别完成后自动将文字复制到剪贴板并粘贴到光标位置
- **系统托盘**：提供系统托盘图标，方便管理和配置

## 技术栈

- **核心识别**：OpenAI Whisper / Qwen3-ASR-0.6B
- **音频处理**：PyAudio、SciPy
- **热键监听**：keyboard
- **系统集成**：pystray、pyautogui
- **降噪处理**：noisereduce
- **静音检测**：基于能量的 VAD 算法

## 安装步骤

### 1. 安装依赖

```bash
# 基础依赖
pip install -r requirements.txt

# 可选依赖（用于 Qwen3-ASR-0.6B 模型）
pip install transformers torch

# 可选依赖（用于降噪功能）
pip install noisereduce
```

### 2. 运行程序

```bash
# 启动语音输入法
python main.py

# 测试模式（仅测试模块初始化）
python main.py --test

# 查看配置
python main.py --config
```

## 使用方法

1. **启动程序**：运行 `python main.py` 启动语音输入法
2. **开始录音**：按住 `Ctrl+Alt+Space` 热键开始录音
3. **停止录音**：松开热键停止录音，系统会自动识别并输入文字
4. **查看系统托盘**：右键点击系统托盘图标可以修改设置

## 配置选项

配置文件位于 `data/config.json`，可以通过修改此文件调整以下选项：

| 配置项 | 默认值 | 说明 |
|-------|-------|------|
| hotkey | ctrl+alt+space | 触发录音的热键 |
| language | zh | 识别语言：zh中文，en英文 |
| model_name | base | 识别模型：qwen3-asr-0.6b/tiny/base/small/medium/large |
| input_mode | push_to_talk | 录音模式：push_to_talk（按住说话）/ toggle（按一次开始/停止） |
| output_method | clipboard | 文字插入方式：clipboard（复制粘贴） |
| audio_device | null | 音频设备ID，null=自动选择 |
| sample_rate | 16000 | 采样率 |
| channels | 1 | 声道数 |
| enable_beep | true | 开始/结束录音时的提示音 |
| auto_punctuation | true | 自动加标点 |
| debug_mode | false | 调试模式 |
| log_level | INFO | 日志级别 |

## 模型选择

- **qwen3-asr-0.6b**：专为中文优化的轻量级模型，速度快，准确率高
- **tiny**：最小的模型，速度最快，但准确率较低
- **base**：平衡速度和准确率的模型，推荐使用
- **small**：较大的模型，准确率更高，但速度较慢
- **medium**：大型模型，准确率高，速度慢
- **large**：最大的模型，准确率最高，但速度最慢

## 常见问题

### 1. 热键不生效

- 以管理员权限运行程序
- 检查热键是否与其他程序冲突
- 尝试修改热键组合

### 2. 识别速度慢

- 选择较小的模型（如 base 或 tiny）
- 确保系统资源充足
- 减少录音时长

### 3. 识别准确率低

- 选择较大的模型（如 small 或 medium）
- 在安静的环境中录音
- 清晰发音，语速适中
- 检查麦克风是否正常工作

### 4. 程序崩溃

- 检查依赖是否正确安装
- 查看日志文件 `data/voice_input.log` 了解错误原因
- 尝试使用较小的模型

## 项目结构

```
voice-input/
├── main.py              # 主程序入口
├── config.py            # 配置管理
├── recorder.py          # 录音模块
├── recognizer.py        # 语音识别模块
├── text_typing.py       # 文本输入模块
├── hotkey_manager.py    # 热键管理
├── tray_icon.py         # 系统托盘图标
├── vad.py               # VAD 静音裁剪模块
├── denoiser.py          # AI 降噪模块
├── requirements.txt     # 依赖项
└── data/                # 数据目录
    ├── temp/            # 临时录音文件
    ├── config.json      # 配置文件
    └── models/          # 模型文件
```

## 性能优化

1. **模型选择**：根据设备性能选择合适的模型
2. **VAD 裁剪**：自动裁剪静音部分，减少识别时间
3. **AI 降噪**：降低背景噪音，提高识别准确率
4. **批量处理**：对于较长的语音，可以分批次处理

## 未来计划

- [ ] 支持实时语音识别
- [ ] 增加更多语言支持
- [ ] 优化模型推理速度
- [ ] 添加自定义词库功能
- [ ] 提供图形化配置界面

## 许可证

本项目基于 MIT 许可证开源。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！
