# AI Education Assistant Backend

AI教育助手后端系统，基于FastAPI构建的现代化教育平台后端服务。

## 功能特性

- 🔐 **用户认证系统** - JWT认证，用户注册/登录
- 📚 **学习计划管理** - 创建和管理个性化学习计划
- 📝 **错题本功能** - 记录和分析学习中的错误
- 🤖 **AI对话系统** - 与AI助手进行教育对话
- 📊 **数据统计** - 学习进度和效果分析
- 🚀 **高性能架构** - 基于FastAPI的异步处理

## 技术栈

- **后端框架**: FastAPI
- **数据库**: MySQL 8.0
- **缓存**: Redis
- **认证**: JWT
- **容器化**: Docker & Docker Compose
- **AI集成**: OpenAI API

## 快速开始

### 环境要求

- Python 3.10+
- Docker & Docker Compose
- MySQL 8.0
- Redis

### 1. 克隆项目

```bash
git clone <repository-url>
cd ai-education-assistant
```

### 2. 环境配置

复制环境配置文件：

```bash
cp env.example .env
```

编辑 `.env` 文件，配置数据库连接、Redis连接和AI服务API密钥：

```env
# Database Configuration
DATABASE_URL=mysql+pymysql://root:password@db:3306/ai_education_assistant
DATABASE_HOST=db
DATABASE_PORT=3306
DATABASE_NAME=ai_education_assistant
DATABASE_USER=root
DATABASE_PASSWORD=password

# Redis Configuration
REDIS_URL=redis://redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# JWT Configuration
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# External AI Service Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
```

### 3. 使用Docker Compose运行

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f app
```

### 4. 手动安装和运行

```bash
# 安装Python依赖
pip install -r requirements.txt

# 启动MySQL和Redis服务
# (确保MySQL和Redis服务正在运行)

# 初始化数据库
python scripts/init_db.py

# 启动应用
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API文档

启动服务后，访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 项目结构

```
ai-education-assistant/
├── app/                    # 应用主目录
│   ├── api/               # API路由
│   │   └── v1/            # API版本1
│   ├── core/              # 核心配置
│   ├── db/                # 数据库配置
│   ├── models/            # 数据模型
│   ├── schemas/           # Pydantic模型
│   ├── services/          # 业务服务
│   ├── utils/             # 工具函数
│   └── main.py            # 应用入口
├── sql/                   # SQL脚本
├── scripts/               # 脚本文件
├── docker-compose.yml     # Docker Compose配置
├── Dockerfile             # Docker配置
├── requirements.txt       # Python依赖
└── README.md              # 项目说明
```

## API端点

### 认证相关
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/logout` - 用户登出
- `POST /api/v1/auth/refresh` - 刷新令牌
- `GET /api/v1/auth/me` - 获取当前用户信息

### 用户管理
- `GET /api/v1/users/me` - 获取个人资料
- `PUT /api/v1/users/me` - 更新个人资料
- `POST /api/v1/users/upload-avatar` - 上传头像
- `GET /api/v1/users/me/stats` - 获取用户统计

### 学习计划
- `POST /api/v1/study-plans/` - 创建学习计划
- `GET /api/v1/study-plans/` - 获取学习计划列表
- `GET /api/v1/study-plans/{id}` - 获取特定学习计划
- `PUT /api/v1/study-plans/{id}` - 更新学习计划
- `DELETE /api/v1/study-plans/{id}` - 删除学习计划

### 学习任务
- `POST /api/v1/study-plans/{id}/tasks` - 创建学习任务
- `GET /api/v1/study-plans/{id}/tasks` - 获取学习任务列表
- `PUT /api/v1/study-plans/{id}/tasks/{task_id}` - 更新学习任务
- `DELETE /api/v1/study-plans/{id}/tasks/{task_id}` - 删除学习任务

### 错题本
- `POST /api/v1/error-logs/` - 创建错题记录
- `GET /api/v1/error-logs/` - 获取错题列表
- `GET /api/v1/error-logs/{id}` - 获取特定错题
- `PUT /api/v1/error-logs/{id}` - 更新错题记录
- `DELETE /api/v1/error-logs/{id}` - 删除错题记录
- `POST /api/v1/error-logs/{id}/review` - 标记错题为已复习

### AI对话
- `POST /api/v1/conversations/` - 创建新对话
- `GET /api/v1/conversations/` - 获取对话列表
- `GET /api/v1/conversations/{id}` - 获取特定对话
- `POST /api/v1/conversations/{id}/messages` - 发送消息
- `GET /api/v1/conversations/{id}/messages` - 获取消息列表
- `POST /api/v1/conversations/{id}/messages/{msg_id}/ai-response` - 生成AI回复

## 开发指南

### 代码规范

项目使用以下工具确保代码质量：

```bash
# 代码格式化
black app/

# 导入排序
isort app/

# 代码检查
flake8 app/
```

### 测试

```bash
# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app
```

### 数据库迁移

```bash
# 生成迁移文件
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 部署

### 生产环境配置

1. 更新 `.env` 文件中的生产环境配置
2. 设置强密码和安全的SECRET_KEY
3. 配置正确的数据库和Redis连接
4. 设置AI服务的API密钥

### Docker部署

```bash
# 构建镜像
docker build -t ai-education-assistant .

# 运行容器
docker run -d -p 8000:8000 --env-file .env ai-education-assistant
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 邮箱: your-email@example.com

---

**注意**: 这是一个开发版本，请在生产环境中使用前进行充分测试。
