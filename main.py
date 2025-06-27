from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import re
import requests
import json
import os
import hashlib
import base64
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import threading
import time
import pytz
import csv
from io import StringIO, BytesIO
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from cryptography.fernet import Fernet
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

# 香港时区
HK_TIMEZONE = pytz.timezone('Asia/Hong_Kong')

DB_CONN_STR = "postgresql://postgres:aiAI918918%40lq518.kl9418m@db.tlavhgppuovlshaologk.supabase.co:5432/postgres"

def get_conn():
    return psycopg2.connect(DB_CONN_STR, cursor_factory=RealDictCursor)

def load_fernet():
    with open("secret.key", "rb") as key_file:
        key = key_file.read()
    return Fernet(key)

def encrypt_api_key(api_key):
    return api_key  # 明文存储

def decrypt_api_key(encrypted_key):
    return encrypted_key  # 明文读取

def hash_api_key(api_key):
    """生成API密钥的哈希值用于唯一标识"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def add_api_key(api_key):
    """添加API密钥到数据库"""
    try:
        key_hash = hash_api_key(api_key)
        encrypted_key = encrypt_api_key(api_key)
        
        if not encrypted_key:
            return False, "密钥加密失败"
        
        conn = get_conn()
        cursor = conn.cursor()
        
        # 检查是否已存在
        cursor.execute('SELECT id FROM api_keys WHERE key_hash = %s', (key_hash,))
        if cursor.fetchone():
            conn.close()
            return False, "API密钥已存在"
        
        # 验证密钥有效性
        if not test_api_key(api_key):
            conn.close()
            return False, "API密钥无效或配额已用完"
        
        # 插入新密钥
        cursor.execute('''
            INSERT INTO api_keys (key_hash, key_encrypted, quota_used, last_used, is_valid)
            VALUES (%s, %s, 0, %s, 1)
        ''', (key_hash, encrypted_key, datetime.now()))
        
        conn.commit()
        conn.close()
        return True, "API密钥添加成功"
        
    except Exception as e:
        return False, f"添加失败: {str(e)}"

def test_api_key(api_key):
    """测试API密钥是否有效"""
    try:
        url = "https://www.googleapis.com/youtube/v3/channels"
        params = {
            'part': 'id',
            'id': 'UC_x5XG1OV2P6uZZ5FSM9Ttw',  # Google Developers频道ID
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return 'items' in data
        elif response.status_code == 403:
            # 检查是否是配额问题
            error_data = response.json()
            if 'error' in error_data and 'code' in error_data['error']:
                if error_data['error']['code'] == 403:
                    return False  # 配额用完或密钥无效
        return False
        
    except Exception as e:
        print(f"测试API密钥失败: {e}")
        return False

def get_available_api_key():
    """获取可用的API密钥（轮询方式）"""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        # 获取所有有效且未超配额的密钥
        cursor.execute('''
            SELECT id, key_encrypted, quota_used, quota_limit 
            FROM api_keys 
            WHERE is_valid = 1 AND quota_used < quota_limit
            ORDER BY last_used ASC
        ''')
        
        keys = cursor.fetchall()
        conn.close()
        
        if not keys:
            return None
        
        # 选择使用最少的密钥
        key_id, encrypted_key, quota_used, quota_limit = keys[0]
        api_key = decrypt_api_key(encrypted_key)
        
        if api_key:
            # 更新使用时间
            update_key_usage(key_id)
            return api_key
        
        return None
        
    except Exception as e:
        print(f"获取API密钥失败: {e}")
        return None

def update_key_usage(key_id):
    """更新密钥使用情况"""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE api_keys 
            SET quota_used = quota_used + 1, last_used = %s
            WHERE id = %s
        ''', (datetime.now(), key_id))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"更新密钥使用情况失败: {e}")

def log_key_usage(key_id, operation, success, error_message=None):
    """记录密钥使用日志"""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO key_usage (key_id, operation, success, error_message)
            VALUES (%s, %s, %s, %s)
        ''', (key_id, operation, success, error_message))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"记录密钥使用日志失败: {e}")

def check_api_keys_validity():
    """检查所有API密钥的有效性"""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, key_encrypted FROM api_keys WHERE is_valid = 1')
        keys = cursor.fetchall()
        
        for key_id, encrypted_key in keys:
            api_key = decrypt_api_key(encrypted_key)
            if api_key:
                is_valid = test_api_key(api_key)
                cursor.execute('''
                    UPDATE api_keys 
                    SET is_valid = %s, last_checked = %s
                    WHERE id = %s
                ''', (1 if is_valid else 0, datetime.now(), key_id))
                
                if not is_valid:
                    print(f"API密钥 {key_id} 已失效")
        
        conn.commit()
        conn.close()
        print(f"API密钥检查完成，时间: {datetime.now(HK_TIMEZONE)}")
        
    except Exception as e:
        print(f"检查API密钥有效性失败: {e}")

def reset_daily_quotas():
    """重置每日配额"""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE api_keys SET quota_used = 0')
        conn.commit()
        conn.close()
        
        print(f"每日配额重置完成，时间: {datetime.now(HK_TIMEZONE)}")
        
    except Exception as e:
        print(f"重置配额失败: {e}")

def background_tasks():
    """后台任务：定期检查API密钥和重置配额"""
    while True:
        try:
            now = datetime.now(HK_TIMEZONE)
            
            # 每天凌晨2点重置配额
            if now.hour == 2 and now.minute == 0:
                reset_daily_quotas()
            
            # 每天检查一次API密钥有效性
            if now.hour == 3 and now.minute == 0:
                check_api_keys_validity()
            
            time.sleep(60)  # 每分钟检查一次
            
        except Exception as e:
            print(f"后台任务错误: {e}")
            time.sleep(60)

# 启动后台任务
def start_background_tasks():
    """启动后台任务线程"""
    thread = threading.Thread(target=background_tasks, daemon=True)
    thread.start()

def extract_channel_id_from_url(url):
    """从YouTube URL中提取频道ID"""
    try:
        # 清理URL
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # 解析URL
        parsed_url = urlparse(url)
        
        # 检查是否是YouTube域名
        if 'youtube.com' not in parsed_url.netloc and 'youtu.be' not in parsed_url.netloc:
            return None
        
        # 处理不同的URL格式
        path = parsed_url.path
        
        # 1. 直接频道ID格式: /channel/UC...
        channel_match = re.search(r'/channel/(UC[a-zA-Z0-9_-]+)', path)
        if channel_match:
            return channel_match.group(1)
        
        # 2. 自定义URL格式: /c/channelname 或 /user/username
        custom_match = re.search(r'/(c|user)/([^/]+)', path)
        if custom_match:
            identifier = custom_match.group(2)
            return get_channel_id_from_identifier(identifier)
        
        # 3. 新格式: /@channelname
        handle_match = re.search(r'/@([^/]+)', path)
        if handle_match:
            identifier = handle_match.group(1)
            return get_channel_id_from_identifier(identifier)
        
        # 4. 检查查询参数中的频道ID
        query_params = parse_qs(parsed_url.query)
        if 'channel_id' in query_params:
            return query_params['channel_id'][0]
        
        return None
        
    except Exception as e:
        print(f"Error extracting channel ID: {e}")
        return None

def get_channel_id_from_identifier(identifier):
    """通过频道标识符获取真实的频道ID（增强版）"""
    api_key = get_available_api_key()
    if api_key:
        # 优先用 googleapiclient 官方库多方式查找
        try:
            youtube = build('youtube', 'v3', developerKey=api_key)
            # 1. 直接用 channels().list (forUsername)
            request = youtube.channels().list(
                part="id",
                forUsername=identifier
            )
            response = request.execute()
            if response.get('items'):
                return response['items'][0]['id']
            # 2. 用 search().list (q)
            request = youtube.search().list(
                part="snippet",
                q=identifier,
                type="channel",
                maxResults=1
            )
            response = request.execute()
            if response.get('items'):
                return response['items'][0]['snippet']['channelId']
        except HttpError as e:
            print(f"Google API client error: {e}")
        except Exception as e:
            print(f"Google API client error: {e}")
        # 兜底：用原有 requests 逻辑
        cid = get_channel_id_via_api(identifier, api_key)
        if cid:
            return cid
    # 最后用页面抓取兜底
    return get_channel_id_from_page(identifier)

def get_channel_id_via_api(identifier, api_key):
    """通过YouTube API获取频道ID"""
    try:
        # 尝试通过搜索API获取频道信息
        search_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': identifier,
            'type': 'channel',
            'key': api_key,
            'maxResults': 1
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('items'):
                return data['items'][0]['snippet']['channelId']
        
        # 如果搜索失败，尝试直接通过频道API
        channel_url = "https://www.googleapis.com/youtube/v3/channels"
        params = {
            'part': 'id',
            'forUsername': identifier,
            'key': api_key
        }
        
        response = requests.get(channel_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('items'):
                return data['items'][0]['id']
                
    except Exception as e:
        print(f"API Error: {e}")
    
    return None

def get_channel_id_from_page(identifier):
    """从YouTube页面中提取频道ID（备用方案）"""
    try:
        # 尝试访问频道页面
        url = f"https://www.youtube.com/@{identifier}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # 在页面源码中查找频道ID
            content = response.text
            
            # 查找各种可能的频道ID模式
            patterns = [
                r'"channelId":"(UC[a-zA-Z0-9_-]+)"',
                r'channel_id=([^&"]+)',
                r'data-channel-id="(UC[a-zA-Z0-9_-]+)"',
                r'channel/(UC[a-zA-Z0-9_-]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    return match.group(1)
        
        # 如果@格式失败，尝试/c/格式
        url = f"https://www.youtube.com/c/{identifier}"
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            content = response.text
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    return match.group(1)
                    
    except Exception as e:
        print(f"Page extraction error: {e}")
    
    return None

def check_channel_exists(channel_id):
    """检查频道ID是否已存在于数据库中"""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM channels WHERE channel_id = %s', (channel_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        print(f"Database error: {e}")
        return False

def save_channel(channel_id, channel_url):
    """保存频道ID到数据库"""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO channels (channel_id, channel_url) VALUES (%s, %s)', 
                      (channel_id, channel_url))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving channel: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/add_key', methods=['POST'])
def add_key():
    """添加API密钥"""
    try:
        data = request.get_json()
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            return jsonify({'success': False, 'message': '请输入API密钥'})
        
        success, message = add_api_key(api_key)
        return jsonify({'success': success, 'message': message})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})

@app.route('/api/keys', methods=['GET'])
def get_keys():
    """获取API密钥状态"""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, quota_used, quota_limit, is_valid, last_used, created_at
            FROM api_keys
            ORDER BY created_at DESC
        ''')
        
        keys = cursor.fetchall()
        conn.close()
        
        key_list = []
        for key in keys:
            key_list.append({
                'id': key[0],
                'quota_used': key[1],
                'quota_limit': key[2],
                'is_valid': bool(key[3]),
                'last_used': key[4],
                'created_at': key[5],
                'quota_percentage': round((key[1] / key[2]) * 100, 1) if key[2] > 0 else 0
            })
        
        return jsonify({'success': True, 'keys': key_list})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取密钥列表失败: {str(e)}'})

@app.route('/api/query', methods=['POST'])
def query_channel():
    """查询频道ID是否存在"""
    try:
        data = request.get_json()
        channel_url = data.get('channel_url', '').strip()
        
        if not channel_url:
            return jsonify({'success': False, 'message': '请输入频道URL'})
        
        # 提取频道ID
        channel_id = extract_channel_id_from_url(channel_url)
        
        if not channel_id:
            return jsonify({'success': False, 'message': '无法提取频道ID，请检查URL格式是否正确'})
        
        # 检查是否已存在，并返回保存时间
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT created_at FROM channels WHERE channel_id = %s', (channel_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return jsonify({
                'success': True, 
                'message': '频道已存在',
                'channel_id': channel_id,
                'exists': True,
                'saved_at': result[0]
            })
        else:
            return jsonify({
                'success': True, 
                'message': '没有频道记录',
                'channel_id': channel_id,
                'exists': False
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'})

@app.route('/api/upload', methods=['POST'])
def upload_channel():
    """上传并保存频道ID"""
    try:
        data = request.get_json()
        channel_url = data.get('channel_url', '').strip()
        
        if not channel_url:
            return jsonify({'success': False, 'message': '请输入频道URL'})
        
        # 提取频道ID
        channel_id = extract_channel_id_from_url(channel_url)
        
        if not channel_id:
            return jsonify({'success': False, 'message': '无法提取频道ID，请检查URL格式是否正确'})
        
        # 保存频道ID
        if save_channel(channel_id, channel_url):
            return jsonify({
                'success': True, 
                'message': '频道ID保存成功',
                'channel_id': channel_id
            })
        else:
            return jsonify({'success': False, 'message': '频道ID已存在或保存失败'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'上传失败: {str(e)}'})

@app.route('/api/channels', methods=['GET'])
def get_channels():
    """获取所有已保存的频道"""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT channel_id, channel_url, created_at FROM channels ORDER BY created_at DESC')
        channels = cursor.fetchall()
        conn.close()
        
        channel_list = []
        for channel in channels:
            channel_list.append({
                'channel_id': channel[0],
                'channel_url': channel[1],
                'created_at': channel[2]
            })
        
        return jsonify({'success': True, 'channels': channel_list})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取频道列表失败: {str(e)}'})

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/download_channels', methods=['GET'])
def download_channels():
    """导出所有频道为CSV文件"""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT channel_id, channel_url, created_at FROM channels ORDER BY created_at DESC')
        channels = cursor.fetchall()
        conn.close()

        # 生成CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['频道ID', '频道URL', '保存时间'])
        for channel in channels:
            writer.writerow(channel)
        csv_data = output.getvalue().encode('utf-8-sig')
        output.close()

        return app.response_class(
            csv_data,
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=channels.csv'
            }
        )
    except Exception as e:
        return '导出失败: ' + str(e), 500

if __name__ == '__main__':
    start_background_tasks()
    print("YouTube频道ID提取工具已启动")
    port = int(os.environ.get("PORT", 8080))  # 兼容本地和云平台
    app.run(debug=True, host='0.0.0.0', port=port) 