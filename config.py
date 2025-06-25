import os

# 应用配置
class Config:
    # 基本设置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DEBUG = True
    
    # YouTube API设置
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY') or 'YOUR_YOUTUBE_API_KEY'
    
    # 数据库设置
    DATABASE_PATH = 'youtube_channels.db'
    
    # 服务器设置
    HOST = '0.0.0.0'
    PORT = 5000
    
    # 请求超时设置
    REQUEST_TIMEOUT = 10
    
    # 用户代理设置
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36' 