// API响应类型
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

// 用户相关类型
export interface User {
  id: number;
  username: string;
  email: string;
  nickname: string;
  avatar_url?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreateRequest {
  username: string;
  email: string;
  password: string;
  nickname: string;
}

export interface UserLoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// 学习计划相关类型
export interface StudyPlan {
  id: number;
  user_id: number;
  title: string;
  description: string;
  subject: string;
  difficulty_level: 'beginner' | 'intermediate' | 'advanced';
  estimated_duration: number;
  is_public: boolean;
  is_ai_generated?: boolean;
  created_at: string;
  updated_at: string;
}

export interface StudyPlanCreateRequest {
  title: string;
  description: string;
  subject: string;
  difficulty_level: 'beginner' | 'intermediate' | 'advanced';
  estimated_duration: number;
  is_public: boolean;
}

export interface StudyTask {
  id: number;
  study_plan_id: number;
  title: string;
  description: string;
  task_type: 'reading' | 'practice' | 'quiz' | 'project';
  difficulty_level: 'easy' | 'medium' | 'hard';
  estimated_duration: number;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

// 错题本相关类型
export interface ErrorLog {
  id: number;
  user_id: number;
  question: string;
  user_answer: string;
  correct_answer: string;
  subject: string;
  difficulty_level: 'easy' | 'medium' | 'hard';
  explanation: string;
  image_url?: string;
  created_at: string;
  updated_at: string;
}

export interface ErrorLogCreateRequest {
  question: string;
  user_answer: string;
  correct_answer: string;
  subject: string;
  difficulty_level: 'easy' | 'medium' | 'hard';
  explanation: string;
}

// 对话相关类型
export interface Conversation {
  id: number;
  user_id: number;
  title: string;
  subject: string;
  difficulty_level: 'beginner' | 'intermediate' | 'advanced';
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface ConversationCreateRequest {
  title: string;
  subject: string;
  difficulty_level: 'beginner' | 'intermediate' | 'advanced';
  is_public: boolean;
}

export interface Message {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  content_type: string;
  metadata_json?: any;
  tokens_used?: number;
  created_at: string;
}

export interface MessageCreateRequest {
  content: string;
  role?: 'user' | 'assistant' | 'system';
  content_type?: string;
  metadata_json?: any;
}

// 认证状态类型
export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// 表单验证类型
export interface LoginFormData {
  username: string;
  password: string;
}

export interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  nickname: string;
}

