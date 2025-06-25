#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os

def check_and_install_dependencies():
    """检查并安装依赖"""
    print("检查Python依赖...")
    
    required_packages = [
        'flask',
        'flask-cors', 
        'requests'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} 已安装")
        except ImportError:
            print(f"✗ {package} 未安装，正在安装...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✓ {package} 安装成功")
            except subprocess.CalledProcessError:
                print(f"✗ {package} 安装失败")
                return False
    
    return True

def main():
    print("=" * 50)
    print("YouTube频道ID提取工具")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 6):
        print("错误: 需要Python 3.6或更高版本")
        sys.exit(1)
    
    print(f"Python版本: {sys.version}")
    
    # 检查并安装依赖
    if not check_and_install_dependencies():
        print("依赖安装失败，请手动运行: pip install -r requirements.txt")
        sys.exit(1)
    
    print("\n启动应用...")
    print("访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止应用")
    print("-" * 50)
    
    # 启动Flask应用
    try:
        from main import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n应用已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 