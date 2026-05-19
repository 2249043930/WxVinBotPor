# WxVinBot - 微信车架号智能识别系统

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-brightgreen.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📖 项目介绍

**WxVinBot** 是一款专为汽车配件行业打造的微信智能机器人系统，通过先进的AI技术自动识别群聊中的车架号（VIN）图片，快速查询车型信息，并智能推送至供应商进行报价。系统支持多群管理、关键词触发通知、工作时间控制等高级功能，大幅提升汽配行业的工作效率。

### 🎯 核心能力

- **智能VIN识别**：基于多模态大模型，自动识别图片中的17位车架号
- **车型信息查询**：实时查询车辆品牌、型号、发动机、排量等详细信息
- **自动报价推送**：识别成功后自动@供应商和客服，推送报价请求
- **关键词触发**：支持报价/发货/成交关键词检测，自动通知相关人员
- **多群管理**：支持数百个微信群的同时监听和管理
- **数据统计**：完整的询价记录、成交统计、数据分析

---

## ✨ 功能特性

### 1. 智能VIN识别模块

| 功能 | 描述 |
|------|------|
| 图片识别 | 自动识别群聊中发送的车架号图片 |
| 多模型支持 | 支持OpenAI、豆包、通义千问等多种LLM |
| 智能纠错 | 自动纠正OCR识别错误，提高准确率 |
| 车型查询 | 自动查询并展示车型详细信息 |

### 2. 群聊管理模块

| 功能 | 描述 |
|------|------|
| 群列表管理 | 查看、添加、删除监听群聊 |
| 通知配置 | 配置询价/报价/发货/成交通知开关 |
| 工作时间 | 设置工作时间，非工作时间不处理 |
| 关键词配置 | 配置报价/发货/成交关键词 |

### 3. 车型配置模块

| 功能 | 描述 |
|------|------|
| 车型管理 | 管理支持查询的车型列表 |
| 供应商绑定 | 不同车型绑定不同供应商 |
| 客服配置 | 配置群专属客服 |

### 4. 数据统计模块

| 功能 | 描述 |
|------|------|
| 询价记录 | 查看所有VIN识别记录 |
| 成交统计 | 统计成交率、热门车型等 |
| 数据导出 | 支持导出Excel报表 |

### 5. 系统管理模块

| 功能 | 描述 |
|------|------|
| 用户管理 | 多用户权限管理 |
| API配置 | 配置LLM API密钥 |
| 日志管理 | 操作日志和系统日志 |

---

## 🏗️ 项目架构

### 技术栈

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层 (Frontend)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Vue 3     │  │  Element Plus│  │      Vite           │  │
│  │  (Composition│  │  (UI组件库)  │  │   (构建工具)        │  │
│  │   API)      │  │              │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API网关层 (API Gateway)                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   FastAPI   │  │   JWT认证   │  │    中间件(日志/跨域) │  │
│  │  (REST API) │  │  (安全)     │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      业务逻辑层 (Business Logic)              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  消息处理器  │  │  VIN调度器  │  │    关键词检测器     │  │
│  │             │  │             │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据访问层 (Data Access)                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  SQLAlchemy │  │   CRUD层    │  │    异步MySQL        │  │
│  │  (ORM)      │  │  (数据库操作)│  │   (aiomysql)       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      外部服务层 (External Services)           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  OpenAI API │  │  豆包API    │  │   微信WebSocket     │  │
│  │  (GPT-4V)   │  │  (Volcengine)│  │   (千寻框架)       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 后端架构

```
backend/
├── app/
│   ├── api/v1/              # API路由层
│   │   ├── auth.py          # 认证接口
│   │   ├── group.py         # 群管理接口
│   │   ├── car_model.py     # 车型配置接口
│   │   ├── statistics.py    # 统计接口
│   │   └── ...
│   ├── core/                # 核心组件
│   │   ├── config.py        # 配置管理
│   │   ├── security.py      # 安全工具
│   │   ├── middleware.py    # 中间件
│   │   └── logger.py        # 日志配置
│   ├── crud/                # 数据库CRUD操作
│   ├── models/              # SQLAlchemy模型
│   ├── modules/wxbot/       # 微信机器人模块
│   │   ├── bot.py           # 千寻Bot封装
│   │   ├── bot_manager.py   # Bot管理器
│   │   ├── message_handler.py # 消息处理器
│   │   ├── vin_recognizer.py  # VIN识别器
│   │   └── websocket_client.py # WebSocket客户端
│   ├── schemas/             # Pydantic数据模型
│   └── db/                  # 数据库配置
├── alembic/                 # 数据库迁移
├── requirements.txt         # Python依赖
└── init_db.py              # 数据库初始化脚本
```

### 前端架构

```
frontend/
├── src/
│   ├── api/                 # API接口封装
│   ├── components/          # 公共组件
│   ├── views/               # 页面视图
│   │   ├── dashboard/       # 数据看板
│   │   ├── group/           # 群管理
│   │   ├── car-model/       # 车型配置
│   │   └── ...
│   ├── router/              # Vue Router配置
│   ├── stores/              # Pinia状态管理
│   ├── types/               # TypeScript类型定义
│   └── utils/               # 工具函数
├── public/
└── package.json
```

---

## 📁 项目模块详解

### 1. 微信机器人模块 (`app/modules/wxbot/`)

#### 1.1 BotManager - 机器人管理器
- **职责**：管理WebSocket连接、监听群聊、消息分发
- **核心功能**：
  - 自动重连机制
  - 多群监听管理
  - 消息去重处理
  - 心跳检测

#### 1.2 MessageHandler - 消息处理器
- **职责**：处理各类微信消息
- **消息类型**：
  - 文本消息：关键词检测、保存记录
  - 图片消息：VIN识别、车型查询、自动回复
  - 语音/视频/表情：仅保存记录
- **关键词触发**：
  ```python
  # 报价关键词触发
  if "报价关键词" in message:
      await reply_inquirer(group_id, "已有报价")
  
  # 发货关键词触发
  if "发货关键词" in message:
      await reply_inquirer(group_id, "已发货")
  
  # 成交关键词触发
  if "成交关键词" in message:
      await reply_inquirer(group_id, "已成交")
      await update_deal_status(vin_code)
  ```

#### 1.3 VINRecognizer - VIN识别器
- **职责**：调用LLM API识别图片中的VIN码
- **支持模型**：
  - OpenAI GPT-4V
  - 豆包（Volcengine）
  - 通义千问
- **识别流程**：
  1. 图片Base64编码
  2. 构建Prompt提示词
  3. 调用LLM API
  4. 解析并校验VIN格式
  5. 返回识别结果

#### 1.4 VINScheduler - VIN调度器
- **职责**：管理VIN查询流程
- **缓存策略**：
  - 先查本地数据库
  - 未命中则调外部API
  - 结果缓存到数据库

### 2. 群管理模块

#### 2.1 群列表管理
- 查看所有监听群聊
- 添加/删除群聊
- 启用/禁用群聊

#### 2.2 通知配置
```json
{
  "inquiry_notify": true,      // 询价通知
  "quote_notify": true,        // 报价通知
  "delivery_notify": true,     // 发货通知
  "deal_notify": true,         // 成交通知
  "work_start_time": "09:00",  // 工作开始时间
  "work_end_time": "18:00",    // 工作结束时间
  "keywords_config": {
    "quote_keywords": ["100", "元", "价格"],
    "delivery_keywords": ["发货", "快递"],
    "deal_keywords": ["成交", "已付款"]
  }
}
```

### 3. 车型配置模块

#### 3.1 车型管理
- 车型CRUD操作
- 车型与供应商绑定
- 群聊专属车型配置

#### 3.2 供应商管理
- 供应商信息管理
- 供应商wxid绑定
- 多供应商轮询（扩展）

### 4. 数据统计模块

#### 4.1 询价记录
- VIN识别记录列表
- 识别状态（成功/失败）
- 询价人、报价人信息
- 是否成交标记

#### 4.2 数据看板
- 今日询价数
- 今日成交数
- 识别成功率
- 热门车型TOP10
- 询价趋势图

---

## 🚀 项目部署指南

### 环境要求

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| Python | 3.11+ | 后端运行环境 |
| Node.js | 18+ | 前端构建环境 |
| MySQL | 8.0+ | 数据存储 |
| Redis | 6.0+ | 缓存（可选） |

### 一、服务器准备

#### 1.1 安装基础软件（Ubuntu示例）

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python
sudo apt install python3.11 python3.11-venv python3-pip -y

# 安装Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 安装MySQL
sudo apt install mysql-server -y
sudo mysql_secure_installation

# 安装Git
sudo apt install git -y
```

#### 1.2 配置MySQL

```bash
# 登录MySQL
sudo mysql -u root -p

# 创建数据库
CREATE DATABASE wxvinbot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 创建用户
CREATE USER 'wxvinbot'@'localhost' IDENTIFIED BY 'your_password';

# 授权
GRANT ALL PRIVILEGES ON wxvinbot.* TO 'wxvinbot'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 二、后端部署

#### 2.1 克隆项目

```bash
cd /opt
git clone https://github.com/your-repo/WxVinBot.git
cd WxVinBot/backend
```

#### 2.2 创建虚拟环境

```bash
# 创建虚拟环境
python3.11 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

#### 2.3 安装依赖

```bash
pip install -r requirements.txt
```

#### 2.4 配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑配置文件
nano .env
```

**`.env` 文件内容：**

```env
# 应用配置
APP_NAME="WxVinBot"
APP_VERSION="1.0.0"
DEBUG=false

# 数据库配置
DATABASE_URL="mysql+aiomysql://wxvinbot:your_password@localhost:3306/wxvinbot?charset=utf8mb4"

# JWT配置
SECRET_KEY="your-super-secret-key-change-this-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# 微信千寻配置
QIANXUN_API_URL="http://127.0.0.1:7778"
QIANXUN_API_KEY="your_qianxun_api_key"

# LLM API配置（至少配置一个）
# OpenAI
OPENAI_API_KEY="sk-your-openai-key"
OPENAI_BASE_URL="https://api.openai.com/v1"
OPENAI_MODEL="gpt-4o"

# 豆包
VOLCENGINE_API_KEY="your-volcengine-key"
VOLCENGINE_MODEL="ep-xxx-xxx"

# 通义千问
DASHSCOPE_API_KEY="your-dashscope-key"

# VIN查询API
VIN_API_URL="https://api.example.com/vin"
VIN_API_KEY="your-vin-api-key"

# 日志配置
LOG_LEVEL="INFO"
```

#### 2.5 初始化数据库

```bash
# 方式1：使用初始化脚本
python init_db.py

# 方式2：应用启动时自动创建（推荐）
# 直接启动应用即可
```

#### 2.6 启动后端服务

**开发模式：**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**生产模式（使用Gunicorn）：**
```bash
# 安装gunicorn
pip install gunicorn

# 启动（4个工作进程）
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --daemon
```

**使用Systemd服务（推荐生产环境）：**

创建服务文件：
```bash
sudo nano /etc/systemd/system/wxvinbot.service
```

内容：
```ini
[Unit]
Description=WxVinBot Backend
After=network.target mysql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/WxVinBot/backend
Environment="PATH=/opt/WxVinBot/backend/venv/bin"
EnvironmentFile=/opt/WxVinBot/backend/.env
ExecStart=/opt/WxVinBot/backend/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable wxvinbot
sudo systemctl start wxvinbot
sudo systemctl status wxvinbot
```

### 三、前端部署

#### 3.1 进入前端目录

```bash
cd /opt/WxVinBot/frontend
```

#### 3.2 安装依赖

```bash
npm install
```

#### 3.3 配置API地址

```bash
# 编辑配置文件
nano .env.production
```

内容：
```env
VITE_API_BASE_URL=http://your-server-ip:8000/api/v1
```

#### 3.4 构建生产版本

```bash
npm run build
```

构建输出在 `dist/` 目录

#### 3.5 部署到Nginx

```bash
# 安装Nginx
sudo apt install nginx -y

# 复制构建文件
sudo cp -r dist/* /var/www/wxvinbot/

# 创建Nginx配置
sudo nano /etc/nginx/sites-available/wxvinbot
```

Nginx配置：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /var/www/wxvinbot;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/wxvinbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 四、微信千寻框架配置

#### 4.1 安装千寻框架

参考千寻官方文档安装微信机器人框架，确保：
- 框架运行在 `ws://127.0.0.1:7778`
- 已登录微信账号
- 框架API密钥正确配置

#### 4.2 配置Webhook

在千寻框架中配置消息推送地址：
```
http://your-server-ip:8000/api/v1/callback/wxbot
```

### 五、SSL配置（HTTPS）

使用Certbot获取免费SSL证书：

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

---

## 📖 使用指南

### 一、首次使用

#### 1.1 访问系统

打开浏览器访问：
- 前端：`http://your-domain.com`
- 后端API文档：`http://your-domain.com/docs`

#### 1.2 默认账号

系统首次启动时会自动创建管理员账号：
- 用户名：`admin`
- 密码：`admin123`

**⚠️ 重要：首次登录后请立即修改密码！**

### 二、基础配置

#### 2.1 配置API密钥

进入 **系统管理 → 接口配置**：
1. 配置OpenAI API密钥（用于VIN识别）
2. 配置豆包API密钥（备用）
3. 配置VIN查询API

#### 2.2 添加监听群聊

进入 **厂群管理 → 群管理**：
1. 点击「自动获取微信群」同步群列表
2. 启用需要监听的群聊
3. 配置群通知设置

#### 2.3 配置车型和供应商

进入 **车型配置 → 车型管理**：
1. 添加常用车型
2. 配置供应商信息
3. 绑定车型与供应商

### 三、日常使用

#### 3.1 群聊中使用

在配置的监听群中：

1. **发送VIN图片**
   - 用户发送车架号图片
   - 机器人自动识别并回复车型信息
   - @供应商和客服进行报价

2. **关键词触发**
   - 供应商发送"100元" → 机器人@询货人"已有报价"
   - 发送"已发货" → 机器人@询货人"已发货"
   - 发送"成交" → 机器人@询货人"已成交"

#### 3.2 查看统计数据

进入 **数据统计**：
- 查看今日询价数、成交数
- 分析热门车型
- 导出数据报表

### 四、高级功能

#### 4.1 工作时间设置

在群通知配置中设置工作时间，非工作时间：
- 只保存消息记录
- 不进行VIN识别
- 不触发关键词回复

#### 4.2 关键词配置

为每个群配置不同的关键词：
- 报价关键词："100", "元", "价格"
- 发货关键词："发货", "快递", "物流"
- 成交关键词："成交", "已付款", "确定"

#### 4.3 多供应商管理

一个车型可绑定多个供应商：
- 主供应商优先通知
- 支持供应商轮询（扩展功能）

---

## 🔧 故障排查

### 常见问题

#### 1. 后端启动失败

```bash
# 检查日志
journalctl -u wxvinbot -f

# 检查数据库连接
python -c "from app.db.session import engine; import asyncio; asyncio.run(engine.connect())"

# 检查端口占用
sudo lsof -i :8000
```

#### 2. VIN识别失败

- 检查LLM API密钥是否正确
- 检查API余额是否充足
- 查看后端日志中的错误信息

#### 3. 微信消息未接收

- 检查千寻框架是否正常运行
- 检查WebSocket连接状态
- 检查回调地址配置

#### 4. 数据库连接错误

```bash
# 测试MySQL连接
mysql -u wxvinbot -p -h localhost wxvinbot

# 检查数据库表是否存在
python init_db.py
```

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📞 联系方式

- 项目主页：https://github.com/your-repo/WxVinBot
- 问题反馈：https://github.com/your-repo/WxVinBot/issues
- 邮箱：support@wxvinbot.com

---

**Made with ❤️ for Auto Parts Industry**
