#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from main import extract_channel_id_from_url

def test_url(url):
    print(f"测试URL: {url}")
    result = extract_channel_id_from_url(url)
    if result:
        print(f"✅ 提取成功: {result}")
    else:
        print("❌ 提取失败")
    print("-" * 50)

if __name__ == "__main__":
    # 测试您的URL
    test_url("https://www.youtube.com/@TaxationExpert/videos")
    
    # 测试其他格式
    test_url("https://www.youtube.com/@TaxationExpert")
    test_url("https://www.youtube.com/c/TaxationExpert")
    test_url("https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw") 