# **AI教育助手系统架构设计文档**

| 版本 | 日期 | 作者 | 备注 |
| :--- | :--- | :--- | :--- |
| V1.0 | 2025-10-10 | Yuyang Ai | 初始版本创建 |

## 1. 引言

### 1.1 文档目的

本文档旨在详细阐述AI教育助手后端系统的整体架构、模块划分、数据库设计及API规范。其主要目的是为项目开发团队提供一个统一的技术框架和设计蓝图，确保系统在技术实现上的一致性、可扩展性和可维护性，并作为后续开发、测试和运维工作的核心指导文件。

### 1.2 项目背景

随着人工智能技术的飞速发展，其在教育领域的应用日益深入。个性化学习、即时答疑和自适应辅导成为提升学习效率的关键。本项目旨在打造一款AI教育助手，通过智能对话、学习计划管理和错题分析等功能，为用户提供一个7x24小时在线的个性化学习伙伴，解决传统学习中遇到的难题，激发学习兴趣。

### 1.3 设计范围

本文档的设计范围涵盖了AI教育助手的后端服务系统，具体包括：

  * 系统整体架构设计
  * 核心功能模块的划分与职责定义
  * 数据库的表结构设计
  * 缓存系统的应用策略
  * 对外暴露的API接口设计规范

本文档**不**包含前端UI/UX设计、具体的AI模型算法实现、以及CI/CD等运维部署细节。

### 1.4 读者对象

本文档的主要读者包括：

  * 项目经理
  * 后端开发工程师
  * 测试工程师
  * 运维工程师

## 2. 系统概述

### 2.1 系统目标

本系统旨在实现以下核心目标：

  * **高可用性：** 系统应具备稳定运行的能力，最大程度地减少服务中断时间。
  * **可扩展性：** 架构设计应支持未来业务增长带来的用户量和数据量的增加，易于横向扩展。
  * **可维护性：** 代码和模块结构清晰，遵循统一规范，便于未来功能的迭代和问题修复。
  * **安全性：** 保障用户数据的安全，包括密码存储、数据传输和访问控制。
  * **高性能：** 对用户请求能做出快速响应，尤其是在核心的AI对话交互上。

### 2.2 设计原则

  * **模块化/微服务化思想：** 系统按业务功能进行垂直拆分，模块之间职责单一，降低耦合度。
  * **前后端分离：** 后端专注于业务逻辑和数据处理，通过RESTful API为前端（Web/App）提供标准化的数据接口。
  * **无状态服务：** 应用服务本身不存储会话状态，状态信息通过客户端Token或分布式缓存管理，便于水平扩展和负载均衡。
  * **数据驱动：** 用户的学习行为数据是系统迭代和功能优化的核心依据。

### 2.3 技术选型

| 领域 | 技术 | 选型理由 |
| :--- | :--- | :--- |
| **编程语言** | Python 3.10+ | 拥有强大的AI/ML生态库，语法简洁，开发效率高。 |
| **Web框架** | FastAPI | 基于ASGI，性能卓越，支持异步处理高并发请求。自带Swagger UI，能自动生成交互式API文档，极大提升开发和联调效率。 |
| **关系型数据库** | MySQL 8.0 | 成熟稳定，社区支持广泛。适用于存储用户、学习计划等结构化核心业务数据，通过事务保证数据一致性。 |
| **内存数据库** | Redis | 高性能的键值存储。用于实现数据缓存、分布式会话管理（如JWT黑名单）、消息队列等，以提升系统性能和响应速度。 |
| **容器化技术** | Docker / Docker Compose | 提供一致的开发、测试和生产环境，简化环境搭建和部署流程，实现应用的快速交付。 |
| **API认证方案** | JWT (JSON Web Tokens) | 轻量、安全、易于跨域的无状态认证方案，适合前后端分离的架构。 |

## 3. 系统架构设计

### 3.1 逻辑架构图

系统采用分层架构，自上而下分为接入层、应用层和数据层。并依赖外部AI服务。

```
+-------------------------------------------------------------------+
|                           用户 (Web/App)                           |
+-------------------------------------------------------------------+
                              | (HTTPS)
+-------------------------------------------------------------------+
|                        接入层 (Nginx/API Gateway)                  |
|               (负载均衡, SSL卸载, 静态资源服务)                    |
+-------------------------------------------------------------------+
                              | (HTTP)
+-------------------------------------------------------------------+
|                       应用层 (FastAPI Service)                      |
|                                                                   |
|  +---------------------+  +----------------------+  +------------+ |
|  |   认证与授权模块     |  |   业务逻辑模块         |  | 外部服务  | |
|  | (JWT Middleware)    |  |  - 用户 (User)         |  |   交互模块 | |
|  +---------------------+  |  - 计划 (Plan)         |  +------------+ |
|                         |  |  - 错题 (ErrorLog)     |        |      |
|                         |  |  - 会话 (Conversation) |        |      |
|                         +----------------------+        |      |
+---------------------------------------------------------+------+---+
                              | (TCP)                         | (HTTPS)
      +-----------------------+-----------------------+     +-----------------+
      |                                               |     |                 |
+-----+----------------+ +----------------------------+-----+   外部AI服务    |
|   数据层 (Data Layer)  | |                          |     | (e.g., OpenAI,  |
|                        | |                          |     |  Google Gemini) |
| +--------------------+ | | +----------------------+ |     |                 |
| |   MySQL 数据库     | | | |      Redis 缓存      | |     +-----------------+
| | (存储持久化数据)   | | | | (缓存, Session等)    | |
| +--------------------+ | | +----------------------+ |
+------------------------+ +--------------------------+

```

### 3.2 部署视图

系统将通过Docker Compose进行容器化部署。

  * **app 服务:** 运行FastAPI应用程序的容器。
  * **db 服务:** 运行MySQL数据库的容器，数据通过volume进行持久化。
  * **redis 服务:** 运行Redis的容器，数据通过volume进行持久化。
  * 三个服务位于同一个Docker网络中，可以通过服务名互相访问。

## 4. 模块化设计

### 4.1 用户模块 (User Service)

  * **职责:** 负责管理用户账户生命周期和身份认证。
  * **核心功能:** 用户注册、邮箱验证、密码加密存储、用户登录与JWT生成、获取/修改用户个人资料。

### 4.2 学习计划模块 (Plan Service)

  * **职责:** 帮助用户创建和管理个性化的学习计划。
  * **核心功能:** 创建计划、添加学习任务、标记任务完成状态、查询计划列表与详情、归档已完成计划。

### 4.3 错题本模块 (Error Log Service)

  * **职责:** 自动或手动收集用户的错题，并提供复习功能。
  * **核心功能:** 添加错题（支持文本、图片）、按科目/知识点分类、查询错题、标记错题状态（已掌握/待复习）。

### 4.4 AI会话模块 (Conversation Service)

  * **职责:** 管理用户与AI之间的完整对话流程。
  * **核心功能:** 创建新会话、保存用户与AI的每一条消息、按时间顺序查询会话历史记录、为会话生成标题。

### 4.5 外部AI服务交互模块

  * **职责:** 作为系统与第三方大语言模型（LLM）API交互的统一出口。
  * **核心功能:** 封装对外部API的请求（如构建prompt、发送请求、处理返回结果）、管理API密钥、处理请求失败和重试逻辑。通过此模块隔离外部依赖，便于未来更换或升级AI模型。

## 5. 数据库设计

### 5.1 概念模型 (E-R Diagram)

  * **实体:** 用户(User)、学习计划(StudyPlan)、错题(ErrorLog)、会话(Conversation)、消息(Message)。
  * **关系:**
      * 一个`User`可以拥有多个`StudyPlan`、多个`ErrorLog`、多个`Conversation`（一对多）。
      * 一个`Conversation`包含多条`Message`（一对多）。

### 5.2 物理模型 (DDL)

```sql
-- 用户表 (users)
CREATE TABLE `users` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
  `password_hash` VARCHAR(255) NOT NULL COMMENT '哈希后的密码',
  `email` VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱',
  `nickname` VARCHAR(50) NULL COMMENT '昵称',
  `avatar_url` VARCHAR(255) NULL COMMENT '头像链接',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT='用户信息表';

-- 学习计划表 (study_plans)
CREATE TABLE `study_plans` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id` BIGINT NOT NULL COMMENT '用户ID',
  `title` VARCHAR(100) NOT NULL COMMENT '计划标题',
  `status` ENUM('ongoing', 'completed', 'archived') NOT NULL DEFAULT 'ongoing' COMMENT '计划状态',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) COMMENT='学习计划表';

-- 错题本表 (error_logs)
CREATE TABLE `error_logs` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id` BIGINT NOT NULL,
  `question_content` TEXT NOT NULL COMMENT '问题内容',
  `correct_answer` TEXT NULL COMMENT '正确答案',
  `status` ENUM('unresolved', 'resolved') NOT NULL DEFAULT 'unresolved' COMMENT '解决状态',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) COMMENT='错题本表';

-- AI会话表 (conversations)
CREATE TABLE `conversations` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id` BIGINT NOT NULL,
  `title` VARCHAR(100) NOT NULL COMMENT '会话标题',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) COMMENT='AI会话记录表';

-- 消息表 (messages)
CREATE TABLE `messages` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `conversation_id` BIGINT NOT NULL,
  `role` ENUM('user', 'assistant') NOT NULL COMMENT '角色：用户或AI助手',
  `content` TEXT NOT NULL COMMENT '消息内容',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`conversation_id`) REFERENCES `conversations`(`id`) ON DELETE CASCADE
) COMMENT='会话消息表';
```

## 6. 缓存设计

系统采用Redis作为缓存解决方案，主要应用场景如下：

  * **用户认证信息缓存：** 存储JWT的黑名单。当用户登出时，将其JWT加入黑名单，在有效期内该JWT将无法再次使用。
  * **热点数据缓存：** 对于不经常变动但访问频繁的数据，如用户的个人信息、系统配置等，进行缓存，降低数据库读取压力。
  * **API速率限制：** 针对特定API（如发送验证码），使用Redis记录用户在单位时间内的请求次数，防止恶意请求。

## 7. API 设计规范

### 7.1 RESTful 风格

所有API均遵循RESTful设计风格，使用标准的HTTP方法：

  * `GET`: 查询资源。
  * `POST`: 创建资源。
  * `PUT`/`PATCH`: 更新资源。
  * `DELETE`: 删除资源。

### 7.2 URI 命名规范

  * URI中只包含名词，不包含动词。
  * 所有API均以 `/api` 作为前缀。
  * 采用版本号控制，如 `/api/v1`。
  * 示例：`GET /api/v1/users/{user_id}/study-plans`

### 7.3 认证与授权

  * 除登录、注册等少数公开接口外，所有API均需进行身份认证。
  * 认证方式采用JWT，客户端需在HTTP请求头的 `Authorization` 字段中携带 `Bearer` 类型的Token。
      * `Authorization: Bearer <your_jwt_token>`

### 7.4 统一响应格式

所有API接口返回统一的JSON格式，便于客户端进行统一处理。

  * **成功响应:**
    ```json
    {
      "code": 0,
      "message": "Success",
      "data": {
        // 具体的业务数据
      }
    }
    ```
  * **失败响应:**
    ```json
    {
      "code": 1001, // 业务错误码，非0
      "message": "Invalid username or password.", // 错误信息
      "data": null
    }
    ```
