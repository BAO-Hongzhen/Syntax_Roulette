@echo off
chcp 65001 >nul
echo ========================================
echo   🎨 Syntax Roulette - AI文本生图
echo ========================================
echo.
echo 正在检查依赖...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python
    echo 请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python已安装
echo.

REM 检查是否需要安装依赖
python -c "import gradio" >nul 2>&1
if errorlevel 1 (
    echo 📦 首次运行，正在安装依赖...
    echo 这可能需要几分钟，请耐心等待...
    echo.
    pip install gradio pillow numpy
    echo.
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        echo 请手动运行: pip install gradio pillow numpy
        pause
        exit /b 1
    )
    echo ✅ 依赖安装完成
    echo.
) else (
    echo ✅ 依赖已就绪
    echo.
)

echo ========================================
echo   正在启动应用...
echo   启动后会自动打开浏览器
echo   如未自动打开，请访问: http://localhost:7860
echo ========================================
echo.

REM 启动应用
python main.py

pause
