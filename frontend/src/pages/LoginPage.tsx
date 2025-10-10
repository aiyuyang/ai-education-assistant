import React from 'react';
import { Form, Input, Button, Card, Typography, Space, Divider } from 'antd';
import { UserOutlined, LockOutlined, LoginOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { LoginFormData } from '../types';

const { Title, Text } = Typography;

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { loginAsync, isLoggingIn } = useAuth();

  const onFinish = async (values: LoginFormData) => {
    try {
      await loginAsync(values);
      navigate('/dashboard');
    } catch (error) {
      console.error('Login error:', error);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px'
    }}>
      <Card
        style={{
          width: '100%',
          maxWidth: 400,
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          borderRadius: '12px',
          border: 'none'
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <Title level={2} style={{ color: '#1890ff', marginBottom: '8px' }}>
            <LoginOutlined /> AI教育助手
          </Title>
          <Text type="secondary">欢迎回来，请登录您的账户</Text>
        </div>

        <Form
          name="login"
          onFinish={onFinish}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: '请输入用户名或邮箱!' },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名或邮箱"
              style={{ borderRadius: '8px' }}
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: '请输入密码!' },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
              style={{ borderRadius: '8px' }}
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={isLoggingIn}
              style={{
                width: '100%',
                height: '48px',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: 'bold'
              }}
            >
              {isLoggingIn ? '登录中...' : '登录'}
            </Button>
          </Form.Item>
        </Form>

        <Divider>
          <Text type="secondary">还没有账户？</Text>
        </Divider>

        <div style={{ textAlign: 'center' }}>
          <Space>
            <Link to="/register">
              <Button type="link" style={{ padding: 0 }}>
                立即注册
              </Button>
            </Link>
            <Text type="secondary">|</Text>
            <Button type="link" style={{ padding: 0 }}>
              忘记密码？
            </Button>
          </Space>
        </div>

        <div style={{ 
          marginTop: '24px', 
          padding: '16px', 
          backgroundColor: '#f6f8fa', 
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            演示账户：testuser / test123
          </Text>
        </div>
      </Card>
    </div>
  );
};

export default LoginPage;

