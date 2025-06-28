from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from supabase import create_client, Client
import pytz
from datetime import datetime
import csv
from io import StringIO
import base64
import hashlib
import requests
import urllib.parse

# 替换为你的 Supabase 项目URL和service_role密钥
SUPABASE_URL = "https://lbufaargeejqtuwmdmlr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxidWZhYXJnZWVqcXR1d21kbWxyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDk5MjY4NiwiZXhwIjoyMDY2NTY4Njg2fQ.JxVnUWmj_8vPMiJnz4MYgHfoING53ch0nY99YCzHZl4"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxidWZhYXJnZWVqcXR1d21kbWxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA5OTI2ODYsImV4cCI6MjA2NjU2ODY4Nn0.RdQzCAsiXUTRgnlI7J4VaeETem2iKp10ZtY5Br2YRVs"
HK_TZ = pytz.timezone('Asia/Hong_Kong')

app = Flask(__name__)
CORS(app)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/add_channel', methods=['POST'])
def add_channel():
    data = request.get_json()
    url = data.get('url', '').strip()
    channel_id = extract_official_channel_id(url)
    if not channel_id:
        return jsonify({'success': False, 'message': '无法识别频道ID'})
    try:
        # 检查是否已存在
        exists = supabase.table('channels').select('channel_id').eq('channel_id', channel_id).execute()
        if exists.data:
            return jsonify({'success': True, 'message': '频道已存在', 'channel_id': channel_id, 'exists': True})
        # 插入新频道
        res = supabase.table('channels').insert({'channel_id': channel_id}).execute()
        if res.error:
            return jsonify({'success': False, 'message': f'添加失败: {res.error.message}'})
        return jsonify({'success': True, 'message': '添加成功', 'channel_id': channel_id, 'exists': False})
    except Exception as e:
        return jsonify({'success': False, 'message': f'添加失败: {e}'})

@app.route('/api/channels', methods=['GET'])
def get_channels():
    try:
        res = supabase.table('channels').select('channel_id, created_at').order('created_at', desc=True).execute()
        if res.error:
            return jsonify({'success': False, 'message': f'查询失败: {res.error.message}'})
        return jsonify({'success': True, 'channels': res.data})
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {e}'})

@app.route('/api/download_channels', methods=['GET'])
def download_channels():
    try:
        res = supabase.table('channels').select('channel_id').order('created_at', desc=True).execute()
        if res.error:
            return jsonify({'success': False, 'message': f'导出失败: {res.error.message}'})
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(['channel_id'])
        for r in res.data:
            cw.writerow([r['channel_id']])
        output = si.getvalue()
        return send_file(
            StringIO(output),
            mimetype='text/csv',
            as_attachment=True,
            download_name='channels.csv'
        )
    except Exception as e:
        return jsonify({'success': False, 'message': f'导出失败: {e}'})

@app.route('/api/add_key', methods=['POST'])
def add_key():
    data = request.get_json()
    api_key = data.get('api_key', '').strip()
    if not api_key:
        return jsonify({'success': False, 'message': 'API密钥不能为空'})
    try:
        api_key_bytes = api_key.encode('utf-8')
        api_key_b64 = base64.b64encode(api_key_bytes).decode('utf-8')
        key_hash = hashlib.sha256(api_key_bytes).hexdigest()
        res = supabase.table('api_keys').insert({
            'key_encrypted': api_key_b64,
            'key_hash': key_hash
        }).execute()
        if not res.data:
            return jsonify({'success': False, 'message': '添加失败，未返回数据'})
        return jsonify({'success': True, 'message': '添加成功'})
    except Exception as e:
        # 检查唯一约束冲突，友好提示
        if 'duplicate key value violates unique constraint' in str(e):
            return jsonify({'success': False, 'message': '该API密钥已存在，请勿重复添加'})
        return jsonify({'success': False, 'message': f'添加失败: {e}'})

@app.route('/api/keys', methods=['GET'])
def get_keys():
    try:
        res = supabase.table('api_keys').select('id, key_encrypted, created_at, is_valid, quota_used, quota_limit, last_used').order('created_at', desc=True).execute()
        if res.error:
            return jsonify({'success': False, 'message': f'查询失败: {res.error.message}'})
        return jsonify({'success': True, 'keys': res.data})
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {e}'})

@app.route('/api/query', methods=['POST'])
def query_channel():
    data = request.get_json()
    url = data.get('channel_url', '').strip()
    channel_id = extract_official_channel_id(url)
    if not channel_id:
        return jsonify({'success': False, 'message': '无法识别频道ID，请检查URL链接是否正确'})
    try:
        # 查询频道是否已存在
        res = supabase.table('channels').select('channel_id, created_at').eq('channel_id', channel_id).execute()
        if res.data:
            return jsonify({
                'success': True,
                'message': '频道已存在',
                'channel_id': channel_id,
                'exists': True,
                'saved_at': res.data[0].get('created_at')
            })
        else:
            return jsonify({
                'success': True,
                'message': '频道没有欺骗记录，<span style="color:#d32f2f;font-weight:bold;">如果他欺骗了你，请点击上传</span>',
                'channel_id': channel_id,
                'exists': False
            })
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {e}'})

@app.route('/api/upload', methods=['POST'])
def upload_channel():
    data = request.get_json()
    url = data.get('channel_url', '').strip()
    channel_id = extract_official_channel_id(url)
    if not channel_id:
        # 新增：尝试查库，看是否已存在
        # 先用 clean_youtube_url 处理
        cleaned_url = clean_youtube_url(url)
        # 尝试查找所有已保存的频道ID
        all_channels = supabase.table('channels').select('channel_id').execute()
        if all_channels.data:
            for ch in all_channels.data:
                if cleaned_url in ch.get('channel_id', ''):
                    return jsonify({'success': False, 'message': '频道已存在', 'channel_id': ch['channel_id']})
        return jsonify({'success': False, 'message': '无法识别频道ID'})
    try:
        # 查重
        res = supabase.table('channels').select('channel_id').eq('channel_id', channel_id).execute()
        if res.data:
            return jsonify({'success': False, 'message': '频道已存在', 'channel_id': channel_id})
        # 插入
        res = supabase.table('channels').insert({'channel_id': channel_id}).execute()
        if not res.data:
            return jsonify({'success': False, 'message': '上传失败，未返回数据'})
        return jsonify({'success': True, 'message': '频道成功上传到<span style="color:#d32f2f;font-weight:bold;">黑名单</span>', 'channel_id': channel_id})
    except Exception as e:
        return jsonify({'success': False, 'message': f'上传失败: {e}'})

def get_youtube_api_key():
    # 从api_keys表中选取第一个有效密钥（可扩展为轮询、配额判断等）
    res = supabase.table('api_keys').select('key_encrypted').eq('is_valid', True).limit(1).execute()
    if res.data:
        key_b64 = res.data[0]['key_encrypted']
        return base64.b64decode(key_b64).decode('utf-8')
    # 兜底：选取任意一个密钥
    res = supabase.table('api_keys').select('key_encrypted').limit(1).execute()
    if res.data:
        key_b64 = res.data[0]['key_encrypted']
        return base64.b64decode(key_b64).decode('utf-8')
    return None

def clean_youtube_url(url):
    """只保留主路径部分，去除/videos、/about等多余路径"""
    import re
    url = url.strip()
    # 1. @handle
    m = re.search(r'youtube\.com/(@[\w\.-]+)', url)
    if m:
        return f"https://www.youtube.com/{m.group(1)}"
    # 2. /user/xxx
    m = re.search(r'youtube\.com/(user/[\w\.-]+)', url)
    if m:
        return f"https://www.youtube.com/{m.group(1)}"
    # 3. /c/xxx
    m = re.search(r'youtube\.com/(c/[\w\.-]+)', url)
    if m:
        return f"https://www.youtube.com/{m.group(1)}"
    # 4. /channel/UCxxxx
    m = re.search(r'youtube\.com/(channel/UC[\w-]+)', url)
    if m:
        return f"https://www.youtube.com/{m.group(1)}"
    return url

def extract_official_channel_id(url):
    import re
    import urllib.parse
    url = urllib.parse.unquote(url)  # 先解码
    print("原始URL:", url, flush=True)
    url = clean_youtube_url(url)
    print("清洗后URL:", url, flush=True)
    # 1. 先正则提取UC开头ID
    m = re.search(r'(UC[\w-]{20,})', url)
    if m:
        print("正则提取UC ID:", m.group(1), flush=True)
        return m.group(1)
    # 2. 其它格式，统一用API查
    api_key = get_youtube_api_key()
    print("API KEY:", api_key, flush=True)
    if not api_key:
        print("未获取到API KEY", flush=True)
        return None
    # handle (@xxx)
    m = re.search(r'youtube\.com/(?:@)([\w\.-]+)', url)
    if m:
        handle = m.group(1)
        api_url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forHandle={handle}&key={api_key}"
        print("handle查API:", api_url, flush=True)
        resp = requests.get(api_url)
        data = resp.json()
        print("API返回:", data, flush=True)
        if 'items' in data and data['items']:
            return data['items'][0]['id']
    # user
    m = re.search(r'youtube\.com/user/([\w\.-]+)', url)
    if m:
        username = m.group(1)
        api_url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forUsername={username}&key={api_key}"
        print("user查API:", api_url, flush=True)
        resp = requests.get(api_url)
        data = resp.json()
        print("API返回:", data, flush=True)
        if 'items' in data and data['items']:
            return data['items'][0]['id']
    # /c/自定义名
    m = re.search(r'youtube\.com/c/([\w\.-]+)', url)
    if m:
        cname = m.group(1)
        api_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={cname}&key={api_key}"
        print("c查API:", api_url, flush=True)
        resp = requests.get(api_url)
        data = resp.json()
        print("API返回:", data, flush=True)
        if 'items' in data and data['items']:
            return data['items'][0]['snippet']['channelId']
    # youtu.be短链、其它特殊情况可继续补充
    print("全部分支未命中，返回None", flush=True)
    return None

if __name__ == '__main__':
    app.run(debug=True, port=8080) 