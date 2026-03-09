PKMS 个人知识管理系统
https://img.shields.io/badge/Python-3.11-blue
https://img.shields.io/badge/Flask-2.3-green
https://img.shields.io/badge/Docker-24.0-blue
https://img.shields.io/badge/license-MIT-green

PKMS (Personal Knowledge Management System) 是一个基于 Flask 开发的个人知识管理工具，旨在帮助用户高效整理笔记、管理标签，并集成 AI 能力提供智能摘要、问答和标签推荐功能。项目采用现代化架构，支持 Docker 一键部署。

✨ 功能特点
用户认证：注册、登录、会话管理（Flask-Login）

笔记管理：增删改查、分页、Markdown 支持

标签系统：多标签关联、标签云统计

AI 助手：

自动生成笔记摘要

基于笔记内容问答

智能推荐标签（支持通义千问、智谱、DeepSeek）

数据统计：笔记数量、标签频率、近7天更新、月度分布等可视化图表

异步任务：Celery + Redis 处理耗时的 AI 请求

容器化部署：Docker Compose 编排 Flask、Celery、Redis、Nginx

🛠️ 技术栈
组件	技术
后端框架	Flask + Flask-SQLAlchemy
数据库	SQLite（开发）、可扩展其他
任务队列	Celery + Redis
前端	Bootstrap 4 + Chart.js
反向代理	Nginx
容器化	Docker + Docker Compose
AI 集成	通义千问、智谱、DeepSeek API
🚀 快速开始（Docker 一键部署）
前置要求
安装 Docker 和 Docker Compose

（可选）申请 AI 服务 API 密钥（通义千问/智谱/DeepSeek）

步骤
1克隆仓库

bash
git clone https://github.com/yourusername/pkms.git
cd pkms
2配置环境变量
复制 .env.example 为 .env，并填入你的密钥：

bash
cp .env.example .env
# 编辑 .env 文件，填写必要的密钥
3启动所有服务

bash
docker-compose up -d
4访问应用
打开浏览器访问 http://localhost，即可开始使用。

常用命令
查看日志：docker-compose logs -f

停止服务：docker-compose down

重新构建：docker-compose up -d --build

🧪 本地开发运行（不使用 Docker）
环境要求
Python 3.11+

Redis（用于 Celery）

安装步骤
创建虚拟环境

bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
安装依赖

bash
pip install -r requirements.txt
配置环境变量
创建 .env 文件，参考 .env.example。

初始化数据库

bash
flask db upgrade
启动 Celery worker（新终端）

bash
celery -A app.celery_worker worker --loglevel=info
启动 Flask 应用

bash
flask run
访问 http://localhost:5000

⚙️ 环境变量说明
变量名	说明	示例
SECRET_KEY	Flask 密钥	your-secret-key
DATABASE_URL	数据库连接	sqlite:///app.db
REDIS_URL	Redis 地址（用于 Celery）	redis://redis:6379/0
AI_PROVIDER	AI 服务提供商	tongyi / zhipu / deepseek
TONGYI_API_KEY	通义千问 API 密钥	sk-xxx
ZHIPU_API_KEY	智谱 API 密钥	xxx
DEEPSEEK_API_KEY	DeepSeek API 密钥	sk-xxx
AI_TIMEOUT	AI 请求超时时间（秒）	8
📁 项目结构
text
pkms/
├── .env.example                # 环境变量示例
├── docker-compose.yml          # Docker 编排配置
├── Dockerfile                  # Flask 应用镜像构建
├── nginx/
│   └── nginx.conf              # Nginx 配置文件
├── app/                        # 应用主目录
│   ├── __init__.py             # 应用工厂
│   ├── extensions.py           # 扩展初始化
│   ├── models.py               # 数据库模型
│   ├── forms.py                # WTForms 表单
│   ├── ai_service.py           # AI 服务封装
│   ├── celery_worker.py        # Celery 实例
│   ├── tasks/                  # 异步任务
│   ├── blueprints/             # 蓝图（auth, main, notes）
│   ├── templates/              # Jinja2 模板
│   └── static/                 # 静态文件（CSS, JS, 图片）
├── requirements.txt            # Python 依赖
└── README.md                   # 本文档
🤝 贡献指南
欢迎提交 Issue 或 Pull Request。请确保代码风格符合 PEP8，并在提交前测试功能。

📄 许可证
本项目采用 MIT 许可证。详见 LICENSE 文件。

🌟 致谢
感谢所有开源项目和 AI 服务提供商的贡献。

特别感谢 Flask 和 Celery 社区。
