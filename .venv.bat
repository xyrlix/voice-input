@echo off
chcp 65001 >nul
echo.
echo 🎤 语音输入法 - 快速启动脚本
echo.

REM 检查是否在虚拟环境中
if "%VIRTUAL_ENV%"=="" (
    echo ⚠️  未检测到虚拟环境
    echo    建议创建虚拟环境运行:
    echo    python -m venv venv
    echo    venv\Scripts\activate
    echo.
    echo 直接使用系统Python继续？
    choice /c YN /n /m "继续 (Y/N)? "
    if errorlevel 2 goto :eof
)

echo 🔧 安装依赖...
pip install -r requirements.txt

REM 检查是否安装了PyAudio，这是Windows上的难点
python -c "import pyaudio" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  未检测到PyAudio
    echo    尝试安装...
    pip install PyAudio
    python -c "import pyaudio" >nul 2>&1
    if errorlevel 1 (
        echo 🚨 PyAudio安装失败
        echo 
        echo Windows用户可能需要:
        echo 1. 下载PyAudio预编译包: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
        echo 2. 根据Python版本下载: PyAudio-0.2.11-cpXX-XX-win_amd64.whl
        echo 3. 运行: pip install 下载的文件.whl
        pause
        goto :eof
    )
)

echo 🚀 启动语音输入法...
python main.py

pause