@echo off
chcp 65001 >nul
title YouTube频道ID提取工具

echo.
echo ================================================
echo           YouTube频道ID提取工具
echo ================================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.6或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python环境检查通过
echo.

echo 正在启动应用...
echo 访问地址: http://localhost:5000
echo 按 Ctrl+C 停止应用
echo.

python start.py

pause 