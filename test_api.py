#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import (
    add_api_key, test_api_key, get_available_api_key, 
    check_api_keys_validity, reset_daily_quotas,
    encrypt_api_key, decrypt_api_key, hash_api_key
)

def test_encryption():
    """测试加密解密功能"""
    print("=" * 50)
    print("加密解密功能测试")
    print("=" * 50)
    
    test_key = "AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    
    # 测试加密
    encrypted = encrypt_api_key(test_key)
    print(f"原始密钥: {test_key}")
    print(f"加密后: {encrypted}")
    
    # 测试解密
    decrypted = decrypt_api_key(encrypted)
    print(f"解密后: {decrypted}")
    print(f"加密解密测试: {'✓ 成功' if test_key == decrypted else '✗ 失败'}")
    
    # 测试哈希
    key_hash = hash_api_key(test_key)
    print(f"密钥哈希: {key_hash}")
    
    print("\n" + "=" * 50)

def test_api_key_validation():
    """测试API密钥验证功能"""
    print("API密钥验证功能测试")
    print("=" * 50)
    
    # 测试无效密钥
    invalid_key = "invalid_key_123"
    is_valid = test_api_key(invalid_key)
    print(f"无效密钥测试: {'✗ 正确识别为无效' if not is_valid else '✗ 错误识别为有效'}")
    
    # 测试有效密钥（需要真实的API密钥）
    print("\n注意: 如需测试有效密钥，请在下方输入真实的YouTube API密钥:")
    real_key = input("请输入API密钥（直接回车跳过）: ").strip()
    
    if real_key:
        is_valid = test_api_key(real_key)
        print(f"有效密钥测试: {'✓ 正确识别为有效' if is_valid else '✗ 错误识别为无效'}")
        
        if is_valid:
            # 测试添加密钥
            success, message = add_api_key(real_key)
            print(f"添加密钥测试: {message}")
    
    print("\n" + "=" * 50)

def test_key_management():
    """测试密钥管理功能"""
    print("密钥管理功能测试")
    print("=" * 50)
    
    # 测试获取可用密钥
    available_key = get_available_api_key()
    if available_key:
        print(f"✓ 找到可用密钥: {available_key[:20]}...")
    else:
        print("✗ 未找到可用密钥")
    
    # 测试添加重复密钥
    test_key = "test_key_123"
    success1, message1 = add_api_key(test_key)
    print(f"添加测试密钥: {message1}")
    
    success2, message2 = add_api_key(test_key)
    print(f"重复添加测试: {message2}")
    
    print("\n" + "=" * 50)

def test_background_functions():
    """测试后台功能"""
    print("后台功能测试")
    print("=" * 50)
    
    print("测试配额重置功能...")
    try:
        reset_daily_quotas()
        print("✓ 配额重置功能正常")
    except Exception as e:
        print(f"✗ 配额重置失败: {e}")
    
    print("测试密钥有效性检查...")
    try:
        check_api_keys_validity()
        print("✓ 密钥有效性检查功能正常")
    except Exception as e:
        print(f"✗ 密钥有效性检查失败: {e}")
    
    print("\n" + "=" * 50)

def test_channel_extraction():
    """测试频道ID提取功能"""
    print("频道ID提取功能测试")
    print("=" * 50)
    
    from main import extract_channel_id_from_url
    
    test_urls = [
        "https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw",
        "https://www.youtube.com/c/GoogleDevelopers",
        "https://www.youtube.com/@GoogleDevelopers",
        "youtube.com/@PewDiePie"
    ]
    
    for url in test_urls:
        print(f"\n测试URL: {url}")
        channel_id = extract_channel_id_from_url(url)
        if channel_id:
            print(f"✓ 提取成功: {channel_id}")
        else:
            print("✗ 提取失败")
    
    print("\n" + "=" * 50)

def main():
    print("YouTube频道ID提取工具 - API密钥管理功能测试")
    print("=" * 50)
    print(f"测试时间: {datetime.now()}")
    print("=" * 50)
    
    # 测试加密解密
    test_encryption()
    
    # 测试API密钥验证
    test_api_key_validation()
    
    # 测试密钥管理
    test_key_management()
    
    # 测试后台功能
    test_background_functions()
    
    # 测试频道提取
    test_channel_extraction()
    
    print("所有测试完成！")
    print("\n注意事项:")
    print("1. 某些测试需要真实的API密钥才能完全验证")
    print("2. 后台任务会在实际运行时自动启动")
    print("3. 时区设置为香港时间，确保系统时间正确")

if __name__ == '__main__':
    main() 