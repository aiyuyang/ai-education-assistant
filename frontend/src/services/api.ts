import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  ApiResponse, 
  User, 
  UserCreateRequest, 
  UserLoginRequest, 
  TokenResponse,
  StudyPlan,
  StudyPlanCreateRequest,
  StudyTask,
  ErrorLog,
  ErrorLogCreateRequest,
  Conversation,
  ConversationCreateRequest,
  Message,
  MessageCreateRequest
} from '../types';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
      timeout: 60000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器 - 添加认证token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          if (!config.headers) config.headers = {} as any;
          (config.headers as any).Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 响应拦截器 - 处理token过期
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // 认证相关API
  async register(userData: UserCreateRequest): Promise<ApiResponse<User>> {
    const response: AxiosResponse<ApiResponse<User>> = await this.api.post('/auth/register', userData);
    return response.data;
  }

  async login(credentials: UserLoginRequest): Promise<ApiResponse<TokenResponse>> {
    const params = new URLSearchParams();
    params.append('username', credentials.username);
    params.append('password', credentials.password);
    const response: AxiosResponse<ApiResponse<TokenResponse>> = await this.api.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    const response: AxiosResponse<ApiResponse<User>> = await this.api.get('/auth/me');
    return response.data;
  }

  async logout(): Promise<ApiResponse<null>> {
    const response: AxiosResponse<ApiResponse<null>> = await this.api.post('/auth/logout');
    return response.data;
  }

  // 用户相关API
  async getUserProfile(): Promise<ApiResponse<User>> {
    const response: AxiosResponse<ApiResponse<User>> = await this.api.get('/users/me');
    return response.data;
  }

  async updateUserProfile(userData: Partial<User>): Promise<ApiResponse<User>> {
    const response: AxiosResponse<ApiResponse<User>> = await this.api.put('/users/me', userData);
    return response.data;
  }

  async getUserStats(): Promise<ApiResponse<any>> {
    const response: AxiosResponse<ApiResponse<any>> = await this.api.get('/users/me/stats');
    return response.data;
  }

  // 学习计划相关API
  async getStudyPlans(): Promise<ApiResponse<StudyPlan[]>> {
    const response: AxiosResponse<ApiResponse<StudyPlan[]>> = await this.api.get('/study-plans');
    return response.data;
  }

  async createStudyPlan(planData: StudyPlanCreateRequest): Promise<ApiResponse<StudyPlan>> {
    const response: AxiosResponse<ApiResponse<StudyPlan>> = await this.api.post('/study-plans', planData);
    return response.data;
  }

  async getStudyPlan(id: number): Promise<ApiResponse<StudyPlan>> {
    const response: AxiosResponse<ApiResponse<StudyPlan>> = await this.api.get(`/study-plans/${id}`);
    return response.data;
  }

  async updateStudyPlan(id: number, planData: Partial<StudyPlanCreateRequest>): Promise<ApiResponse<StudyPlan>> {
    const response: AxiosResponse<ApiResponse<StudyPlan>> = await this.api.put(`/study-plans/${id}`, planData);
    return response.data;
  }

  async deleteStudyPlan(id: number): Promise<ApiResponse<null>> {
    const response: AxiosResponse<ApiResponse<null>> = await this.api.delete(`/study-plans/${id}`);
    return response.data;
  }

  async getStudyTasks(planId: number): Promise<ApiResponse<StudyTask[]>> {
    const response: AxiosResponse<ApiResponse<StudyTask[]>> = await this.api.get(`/study-plans/${planId}/tasks`);
    return response.data;
  }

  async createStudyTask(planId: number, taskData: Partial<StudyTask>): Promise<ApiResponse<StudyTask>> {
    const response: AxiosResponse<ApiResponse<StudyTask>> = await this.api.post(`/study-plans/${planId}/tasks`, taskData);
    return response.data;
  }

  // 错题本相关API
  async getErrorLogs(): Promise<ApiResponse<ErrorLog[]>> {
    const response: AxiosResponse<ApiResponse<ErrorLog[]>> = await this.api.get('/error-logs');
    return response.data;
  }

  async createErrorLog(logData: ErrorLogCreateRequest): Promise<ApiResponse<ErrorLog>> {
    const response: AxiosResponse<ApiResponse<ErrorLog>> = await this.api.post('/error-logs', logData);
    return response.data;
  }

  async getErrorLog(id: number): Promise<ApiResponse<ErrorLog>> {
    const response: AxiosResponse<ApiResponse<ErrorLog>> = await this.api.get(`/error-logs/${id}`);
    return response.data;
  }

  async updateErrorLog(id: number, logData: Partial<ErrorLogCreateRequest>): Promise<ApiResponse<ErrorLog>> {
    const response: AxiosResponse<ApiResponse<ErrorLog>> = await this.api.put(`/error-logs/${id}`, logData);
    return response.data;
  }

  async deleteErrorLog(id: number): Promise<ApiResponse<null>> {
    const response: AxiosResponse<ApiResponse<null>> = await this.api.delete(`/error-logs/${id}`);
    return response.data;
  }

  async getErrorLogStats(): Promise<ApiResponse<any>> {
    const response: AxiosResponse<ApiResponse<any>> = await this.api.get('/error-logs/stats/summary');
    return response.data;
  }

  // 对话相关API
  async getConversations(): Promise<ApiResponse<Conversation[]>> {
    const response: AxiosResponse<ApiResponse<Conversation[]>> = await this.api.get('/conversations');
    return response.data;
  }

  async createConversation(conversationData: ConversationCreateRequest): Promise<ApiResponse<Conversation>> {
    const response: AxiosResponse<ApiResponse<Conversation>> = await this.api.post('/conversations', conversationData);
    return response.data;
  }

  async getConversation(id: number): Promise<ApiResponse<Conversation>> {
    const response: AxiosResponse<ApiResponse<Conversation>> = await this.api.get(`/conversations/${id}`);
    return response.data;
  }

  async updateConversation(id: number, conversationData: Partial<ConversationCreateRequest>): Promise<ApiResponse<Conversation>> {
    const response: AxiosResponse<ApiResponse<Conversation>> = await this.api.put(`/conversations/${id}`, conversationData);
    return response.data;
  }

  async deleteConversation(id: number): Promise<ApiResponse<null>> {
    const response: AxiosResponse<ApiResponse<null>> = await this.api.delete(`/conversations/${id}`);
    return response.data;
  }

  async getMessages(conversationId: number): Promise<ApiResponse<Message[]>> {
    const response: AxiosResponse<ApiResponse<Message[]>> = await this.api.get(`/conversations/${conversationId}/messages`);
    return response.data;
  }

  async createMessage(conversationId: number, messageData: MessageCreateRequest): Promise<ApiResponse<Message>> {
    const response: AxiosResponse<ApiResponse<Message>> = await this.api.post(`/conversations/${conversationId}/messages`, messageData);
    return response.data;
  }

  async getConversationStats(): Promise<ApiResponse<any>> {
    const response: AxiosResponse<ApiResponse<any>> = await this.api.get('/conversations/stats/summary');
    return response.data;
  }

  // AI学习计划生成相关API
  async generateAIStudyPlan(planData: any): Promise<ApiResponse<any>> {
    const response: AxiosResponse<ApiResponse<any>> = await this.api.post('/study-plans/generate', planData);
    return response.data;
  }

  async getStudyPlansList(params?: { status?: string; subject?: string; page?: number; per_page?: number }): Promise<ApiResponse<StudyPlan[]>> {
    const response: AxiosResponse<ApiResponse<StudyPlan[]>> = await this.api.get('/study-plans/list', { params });
    return response.data;
  }
}

export default new ApiService();
