-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS ai_education_assistant CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE ai_education_assistant;

-- 用户表 (users)
CREATE TABLE IF NOT EXISTS `users` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
  `password_hash` VARCHAR(255) NOT NULL COMMENT '哈希后的密码',
  `email` VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱',
  `nickname` VARCHAR(50) NULL COMMENT '昵称',
  `avatar_url` VARCHAR(255) NULL COMMENT '头像链接',
  `is_active` BOOLEAN DEFAULT TRUE COMMENT '账户是否激活',
  `is_verified` BOOLEAN DEFAULT FALSE COMMENT '邮箱是否验证',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX `idx_username` (`username`),
  INDEX `idx_email` (`email`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户信息表';

-- 学习计划表 (study_plans)
CREATE TABLE IF NOT EXISTS `study_plans` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id` BIGINT NOT NULL COMMENT '用户ID',
  `title` VARCHAR(100) NOT NULL COMMENT '计划标题',
  `description` TEXT NULL COMMENT '计划描述',
  `subject` VARCHAR(50) NULL COMMENT '科目',
  `difficulty_level` VARCHAR(20) NULL COMMENT '难度',
  `estimated_duration` INT NULL COMMENT '预计时长(天)',
  `is_public` BOOLEAN DEFAULT FALSE COMMENT '是否公开',
  `is_ai_generated` BOOLEAN DEFAULT FALSE COMMENT '是否AI生成',
  `status` ENUM('ongoing', 'completed', 'archived') NOT NULL DEFAULT 'ongoing' COMMENT '计划状态',
  `start_date` DATE NULL COMMENT '开始日期',
  `end_date` DATE NULL COMMENT '结束日期',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_status` (`status`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学习计划表';

-- 学习任务表 (study_tasks)
CREATE TABLE IF NOT EXISTS `study_tasks` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `plan_id` BIGINT NOT NULL COMMENT '计划ID',
  `title` VARCHAR(200) NOT NULL COMMENT '任务标题',
  `description` TEXT NULL COMMENT '任务描述',
  `status` ENUM('pending', 'in_progress', 'completed') NOT NULL DEFAULT 'pending' COMMENT '任务状态',
  `priority` ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'medium' COMMENT '优先级',
  `due_date` DATETIME NULL COMMENT '截止时间',
  `completed_at` DATETIME NULL COMMENT '完成时间',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  FOREIGN KEY (`plan_id`) REFERENCES `study_plans`(`id`) ON DELETE CASCADE,
  INDEX `idx_plan_id` (`plan_id`),
  INDEX `idx_status` (`status`),
  INDEX `idx_due_date` (`due_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学习任务表';

-- 错题本表 (error_logs)
CREATE TABLE IF NOT EXISTS `error_logs` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id` BIGINT NOT NULL COMMENT '用户ID',
  `subject` VARCHAR(50) NULL COMMENT '科目',
  `topic` VARCHAR(100) NULL COMMENT '知识点',
  `question_content` TEXT NOT NULL COMMENT '问题内容',
  `question_image_url` VARCHAR(255) NULL COMMENT '问题图片URL',
  `correct_answer` TEXT NULL COMMENT '正确答案',
  `explanation` TEXT NULL COMMENT '解析',
  `difficulty` ENUM('easy', 'medium', 'hard') NOT NULL DEFAULT 'medium' COMMENT '难度',
  `status` ENUM('unresolved', 'resolved', 'mastered') NOT NULL DEFAULT 'unresolved' COMMENT '解决状态',
  `review_count` INT DEFAULT 0 COMMENT '复习次数',
  `last_reviewed_at` DATETIME NULL COMMENT '最后复习时间',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_subject` (`subject`),
  INDEX `idx_status` (`status`),
  INDEX `idx_difficulty` (`difficulty`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='错题本表';

-- AI会话表 (conversations)
CREATE TABLE IF NOT EXISTS `conversations` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id` BIGINT NOT NULL COMMENT '用户ID',
  `title` VARCHAR(100) NOT NULL COMMENT '会话标题',
  `summary` TEXT NULL COMMENT '会话摘要',
  `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否活跃',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_is_active` (`is_active`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI会话记录表';

-- 消息表 (messages)
CREATE TABLE IF NOT EXISTS `messages` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `conversation_id` BIGINT NOT NULL COMMENT '会话ID',
  `role` ENUM('user', 'assistant', 'system') NOT NULL COMMENT '角色：用户、AI助手或系统',
  `content` TEXT NOT NULL COMMENT '消息内容',
  `content_type` ENUM('text', 'image', 'file') NOT NULL DEFAULT 'text' COMMENT '内容类型',
  `metadata` JSON NULL COMMENT '元数据（如文件信息等）',
  `tokens_used` INT NULL COMMENT '使用的token数量',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  FOREIGN KEY (`conversation_id`) REFERENCES `conversations`(`id`) ON DELETE CASCADE,
  INDEX `idx_conversation_id` (`conversation_id`),
  INDEX `idx_role` (`role`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='会话消息表';

-- 用户会话表 (user_sessions) - 用于JWT黑名单管理
CREATE TABLE IF NOT EXISTS `user_sessions` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id` BIGINT NOT NULL COMMENT '用户ID',
  `token_jti` VARCHAR(255) UNIQUE NOT NULL COMMENT 'JWT ID',
  `is_revoked` BOOLEAN DEFAULT FALSE COMMENT '是否已撤销',
  `expires_at` DATETIME NOT NULL COMMENT '过期时间',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_token_jti` (`token_jti`),
  INDEX `idx_expires_at` (`expires_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户会话表';

-- 系统配置表 (system_configs)
CREATE TABLE IF NOT EXISTS `system_configs` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `key` VARCHAR(100) UNIQUE NOT NULL COMMENT '配置键',
  `value` TEXT NOT NULL COMMENT '配置值',
  `description` VARCHAR(255) NULL COMMENT '配置描述',
  `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否启用',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX `idx_key` (`key`),
  INDEX `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- 插入默认系统配置
INSERT INTO `system_configs` (`key`, `value`, `description`) VALUES
('max_conversation_length', '100', '单次对话最大消息数量'),
('max_file_size', '10485760', '最大文件上传大小（字节）'),
('rate_limit_per_minute', '60', '每分钟API请求限制'),
('ai_model_default', 'gpt-3.5-turbo', '默认AI模型'),
('conversation_timeout', '1800', '会话超时时间（秒）')
ON DUPLICATE KEY UPDATE `value` = VALUES(`value`);

