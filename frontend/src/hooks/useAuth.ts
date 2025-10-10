import { useMutation, useQuery, useQueryClient } from 'react-query';
import { useAuthStore } from '../store/authStore';
import apiService from '../services/api';
import { UserCreateRequest, UserLoginRequest, User } from '../types';
import { message } from 'antd';

export const useAuth = () => {
  const { user, isAuthenticated, login, logout, setLoading } = useAuthStore();

  // 获取当前用户信息
  const { data: currentUser, isLoading: isLoadingUser } = useQuery(
    'currentUser',
    () => apiService.getCurrentUser(),
    {
      enabled: isAuthenticated,
      onSuccess: (response) => {
        if (response.code === 0) {
          login(response.data, localStorage.getItem('access_token') || '');
        }
      },
      onError: () => {
        logout();
      },
    }
  );

  // 登录
  const loginMutation = useMutation(
    (credentials: UserLoginRequest) => apiService.login(credentials),
    {
      onSuccess: async (response) => {
        if (response.code === 0) {
          const { access_token, refresh_token } = response.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);

          // 获取并写入用户信息（等待完成后再让调用方继续）
          const userResponse = await apiService.getCurrentUser();
          if (userResponse.code === 0) {
            login(userResponse.data, access_token);
            message.success('登录成功！');
          } else {
            message.error('获取用户信息失败');
          }
        } else {
          message.error(response.message || '登录失败');
        }
      },
      onError: (error: any) => {
        message.error(error.response?.data?.message || '登录失败');
      },
    }
  );

  // 注册
  const registerMutation = useMutation(
    (userData: UserCreateRequest) => apiService.register(userData),
    {
      onSuccess: (response) => {
        if (response.code === 0) {
          message.success('注册成功！请登录');
        } else {
          message.error(response.message || '注册失败');
        }
      },
      onError: (error: any) => {
        message.error(error.response?.data?.message || '注册失败');
      },
    }
  );

  // 登出
  const logoutMutation = useMutation(() => apiService.logout(), {
    onSuccess: () => {
      logout();
      message.success('已退出登录');
    },
    onError: () => {
      logout();
    },
  });

  return {
    user: currentUser?.data || user,
    isAuthenticated,
    isLoading: isLoadingUser || loginMutation.isLoading || registerMutation.isLoading,
    login: loginMutation.mutate,
    // expose async version for awaiting in UI flows
    loginAsync: loginMutation.mutateAsync,
    register: registerMutation.mutate,
    logout: logoutMutation.mutate,
    isLoggingIn: loginMutation.isLoading,
    isRegistering: registerMutation.isLoading,
  };
};

