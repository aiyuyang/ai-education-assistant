# AI教育助手前端应用

这是一个基于React + TypeScript + Ant Design的现代化前端应用，为AI教育助手系统提供用户界面。

## 功能特性

- 🔐 **用户认证**: 登录、注册、JWT令牌管理
- 📊 **仪表板**: 学习统计、快速操作、最近活动
- 📚 **学习计划**: 创建和管理学习计划
- 📝 **错题本**: 记录和管理错题
- 🤖 **AI对话**: 与AI助手进行学习对话
- 📱 **响应式设计**: 支持桌面和移动设备
- 🎨 **现代化UI**: 基于Ant Design的美观界面

## 技术栈

- **React 18**: 现代化的React框架
- **TypeScript**: 类型安全的JavaScript
- **Ant Design**: 企业级UI组件库
- **React Router**: 客户端路由
- **React Query**: 数据获取和状态管理
- **Zustand**: 轻量级状态管理
- **Axios**: HTTP客户端

## 快速开始

### 环境要求

- Node.js 16+
- npm 或 yarn

### 安装依赖

```bash
cd frontend
npm install
```

### 环境配置

复制环境变量模板文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置API地址：

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_TITLE=AI教育助手
REACT_APP_VERSION=1.0.0
```

### 启动开发服务器

```bash
npm start
```

应用将在 http://localhost:3000 启动

### 构建生产版本

```bash
npm run build
```

## 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── components/         # 可复用组件
│   ├── pages/             # 页面组件
│   ├── hooks/             # 自定义Hooks
│   ├── services/          # API服务
│   ├── store/             # 状态管理
│   ├── types/             # TypeScript类型定义
│   ├── utils/             # 工具函数
│   ├── App.tsx            # 主应用组件
│   └── index.tsx          # 应用入口
├── package.json           # 项目配置
└── tsconfig.json          # TypeScript配置
```

## 主要页面

- **登录页面** (`/login`): 用户登录
- **注册页面** (`/register`): 用户注册
- **仪表板** (`/dashboard`): 学习概览和快速操作
- **学习计划** (`/study-plans`): 学习计划管理
- **错题本** (`/error-logs`): 错题记录管理
- **AI对话** (`/conversations`): AI助手对话

## API集成

前端通过RESTful API与后端通信：

- **认证API**: 用户登录、注册、登出
- **用户API**: 用户信息管理
- **学习计划API**: 学习计划CRUD操作
- **错题本API**: 错题记录CRUD操作
- **对话API**: AI对话管理

## 状态管理

使用Zustand进行状态管理：

- **认证状态**: 用户信息、登录状态
- **UI状态**: 加载状态、错误信息

## 开发指南

### 添加新页面

1. 在 `src/pages/` 创建页面组件
2. 在 `App.tsx` 添加路由
3. 使用 `ProtectedRoute` 包装需要认证的页面

### 添加新API

1. 在 `src/services/api.ts` 添加API方法
2. 在 `src/types/index.ts` 定义相关类型
3. 在组件中使用React Query调用API

### 样式规范

- 使用Ant Design组件
- 遵循Ant Design设计规范
- 响应式设计，支持移动端

## 部署

### Docker部署

```bash
# 构建镜像
docker build -t ai-education-frontend .

# 运行容器
docker run -p 3000:3000 ai-education-frontend
```

### Nginx部署

```bash
# 构建生产版本
npm run build

# 将build目录部署到Nginx
```

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License

