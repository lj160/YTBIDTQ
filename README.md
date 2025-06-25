# YouTube频道ID提取工具

一个专门用于提取和管理YouTube频道ID的Web应用。

## 功能特点

- 🔍 **频道ID提取**：从各种格式的YouTube频道URL中提取频道ID
- 📊 **查询功能**：检查频道ID是否已存在于数据库中
- 💾 **保存功能**：将新的频道ID保存到数据库
- 📱 **响应式设计**：支持桌面和移动设备
- 🎨 **现代化界面**：美观的用户界面和流畅的交互体验

## 支持的URL格式

- `https://www.youtube.com/channel/UC...`
- `https://www.youtube.com/c/channelname`
- `https://www.youtube.com/user/username`
- `https://www.youtube.com/@channelname`

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置YouTube API密钥

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 YouTube Data API v3
4. 创建API密钥
5. 在 `main.py` 文件中替换 `YOUR_YOUTUBE_API_KEY` 为您的实际API密钥

### 3. 运行应用

```bash
python main.py
```

应用将在 `http://localhost:5000` 启动

## 使用说明

1. **查询频道**：
   - 在输入框中粘贴YouTube频道URL
   - 点击"查询"按钮
   - 系统会显示频道ID和是否存在记录

2. **保存频道**：
   - 在输入框中粘贴YouTube频道URL
   - 点击"上传"按钮
   - 系统会提取频道ID并保存到数据库

3. **查看已保存频道**：
   - 页面底部会显示所有已保存的频道列表
   - 包含频道URL、频道ID和保存时间

## 技术栈

- **后端**：Python Flask
- **前端**：HTML5, CSS3, JavaScript
- **数据库**：SQLite
- **API**：YouTube Data API v3

## 文件结构

```
YTBIDTQ/
├── main.py              # Flask后端应用
├── requirements.txt     # Python依赖
├── README.md           # 项目说明
├── templates/
│   └── index.html      # 前端界面
└── youtube_channels.db # SQLite数据库（自动创建）
```

## 注意事项

- 需要有效的YouTube API密钥才能正常工作
- 建议在生产环境中使用更安全的数据库（如PostgreSQL）
- API调用有配额限制，请合理使用

## 许可证

MIT License 