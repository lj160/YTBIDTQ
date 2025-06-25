#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import extract_channel_id_from_url, check_channel_exists, save_channel

def test_channel_id_extraction():
    """测试频道ID提取功能"""
    print("=" * 50)
    print("频道ID提取功能测试")
    print("=" * 50)
    
    # 测试用例
    test_urls = [
        "https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw",
        "https://www.youtube.com/c/GoogleDevelopers",
        "https://www.youtube.com/user/GoogleDevelopers",
        "https://www.youtube.com/@GoogleDevelopers",
        "https://youtube.com/@PewDiePie",
        "youtube.com/@MrBeast"
    ]
    
    for url in test_urls:
        print(f"\n测试URL: {url}")
        channel_id = extract_channel_id_from_url(url)
        if channel_id:
            print(f"✓ 提取成功: {channel_id}")
        else:
            print("✗ 提取失败")
    
    print("\n" + "=" * 50)

def test_database_operations():
    """测试数据库操作"""
    print("数据库操作测试")
    print("=" * 50)
    
    # 测试保存频道
    test_channel_id = "UC_TEST_123"
    test_url = "https://www.youtube.com/channel/UC_TEST_123"
    
    print(f"测试保存频道: {test_channel_id}")
    if save_channel(test_channel_id, test_url):
        print("✓ 保存成功")
    else:
        print("✗ 保存失败")
    
    # 测试检查频道是否存在
    print(f"测试检查频道是否存在: {test_channel_id}")
    exists = check_channel_exists(test_channel_id)
    if exists:
        print("✓ 频道已存在")
    else:
        print("✗ 频道不存在")
    
    print("\n" + "=" * 50)

def main():
    print("YouTube频道ID提取工具 - 功能测试")
    print("=" * 50)
    
    # 测试频道ID提取
    test_channel_id_extraction()
    
    # 测试数据库操作
    test_database_operations()
    
    print("测试完成！")

if __name__ == '__main__':
    main() 