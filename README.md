# 🎤 语音输入法

一个 Windows 桌面应用，**按住热键说话 → 自动识别 → 输入到光标处**。

不用再手动打字，动动嘴就能输入文字。

---

## ✨ 特性

- **按住说话**：按住 `Ctrl+Alt+Space` 说话，松开自动识别
- **本地识别**：基于 OpenAI Whisper，**完全离线**，无需网络
- **全局生效**：在任何窗口（记事本、Word、浏览器）都可使用
- **托盘后台**：系统托盘运行，不占桌面
- **中英双语**：支持中文/英文识别
- **两种输入模式**：模拟键盘打字 或 复制粘贴

---

## 📦 安装

### 第一步：确保有 Python（3.8+）

```bash
python --version
```

### 第二步：克隆/下载本项目

```bash
cd F:\claw\voice-input
```

### 第三步：安装依赖

最简方式：双击 `.venv.bat`，它帮你解决 PyAudio 等 Windows 依赖问题。

或者手动：
```bash
# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 额外安装 Whisper
pip install -U openai-whisper
```

---

## 🚀 使用

### 启动程序

```bash
python main.py
```

或双击 `.venv.bat`

启动后 **系统托盘** 会出现一个麦克风图标。

### 基本操作

1. **正常启动**：
   ```bash
   python main.py
   ```

2. **测试功能**（首次运行建议）：
   ```bash
   python main.py --test
   ```

3. **查看配置**：
   ```
   python main.py --config
   ```

### 使用方法

1. 打开任意文本编辑器（记事本、Word、浏览器输入框）
2. 将光标放到你想输入的位置
3. **按住 `Ctrl+Alt+Space`**（默认热键） 说话
4. **松开热键**，语音会自动识别并输入

> 💡 如果热键冲突，右键托盘图标 → 修改热键

---

## ⚙️ 配置

### 热键修改

右键托盘图标 → "修改热键" → 输入新的组合，如 `ctrl+shift+v`

### 其他配置

配置文件位于：`data/config.json`

主要配置项：
```json
{
  "hotkey": "ctrl+alt+space",      // 热键组合
  "language": "zh",                // 识别语言 zh/zh
  "model_name": "tiny",           // 模型大小：tiny/base/small/medium/large
  "output_method": "typing",      // 输入方式：typing（打字）/clipboard（粘贴）
  "typing_speed": 0.01,           // 打字速度（秒/字符）
  "enable_beep": true             // 录音提示音
}
```

**模型大小说明**：
- `tiny` (75MB)：最快，准确度一般
- `base` (142MB)：平衡
- `small` (466MB)：推荐，准确性不错
- `medium` (1.5GB)：准确度高，较慢
- `large` (3.1GB)：最准确，但是很慢

---

## 🛠️ 模块说明

```
F:\claw\voice-input\
├── main.py              # 主程序入口
├── config.py           # 配置管理
├── recorder.py         # 录音模块（按住热键录音）
├── recognizer.py       # Whisper语音识别
├── typing.py           # 文字输入（打字/粘贴）
├── hotkey_manager.py   # 全局热键监听
├── tray_icon.py        # 系统托盘图标
├── requirements.txt    # 依赖列表
├── .venv.bat          # Windows快速启动脚本
└── data/              # 数据目录（配置、临时文件、模型）
```

---

## 🔧 故障排除

### 1. "No module named 'pyaudio'"

Windows 用户需要安装 PyAudio：

```bash
# 尝试这个
pip install pipwin
pipwin install pyaudio

# 或下载预编译包：https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# 然后：pip install PyAudio-0.2.11-cpXX-XX-win_amd64.whl
```

### 2. 无法录音或没声音

- 检查麦克风是否禁用
- 运行 `python main.py --test` 检查设备列表
- 尝试更换音频设备（如果有多麦克风）

### 3. 识别不准

- 减慢语速，清晰发音
- 切换到更大的模型（修改 config.json 中 model_name）
- 确保环境安静

### 4. 热键无效

- 以管理员权限运行程序
- 修改热键避免与现有快捷键冲突
- 检查键盘布局（部分热键可能与输入法冲突）

### 5. Whisper 模型下载慢

第一次运行会自动下载模型（约75MB-3GB），可以：
- 使用国内镜像源：`pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple`
- 手动下载模型到 `data/models/` 目录

---

## 💡 使用技巧

1. **分段输入**：长段落可以分几次录音，每次一句
2. **纠错**：识别错了？直接按 `Ctrl+Z` 撤销，重新说
3. **标点**：程序会自动添加句号，说"问号"也会识别
4. **中英混合**：说中文时夹杂英文单词通常可以识别
5. **离线备用**：确保下载好模型，没有网络也能用

---

## 📄 许可证

MIT License - 详见 LICENSE 文件