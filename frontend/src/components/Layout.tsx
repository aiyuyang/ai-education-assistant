import React, { useState } from 'react';
import { Layout as AntLayout, Menu, Avatar, Dropdown, Button, Space, Typography } from 'antd';
import { 
  DashboardOutlined, 
  BookOutlined, 
  FileTextOutlined, 
  MessageOutlined, 
  UserOutlined,
  LogoutOutlined,
  SettingOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  RobotOutlined
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const { Header, Sider, Content } = AntLayout;
const { Text } = Typography;

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '仪表板',
    },
    {
      key: '/study-plans',
      icon: <BookOutlined />,
      label: '学习计划',
    },
    {
      key: '/ai-study-plan',
      icon: <RobotOutlined />,
      label: 'AI学习计划生成',
    },
    {
      key: '/error-logs',
      icon: <FileTextOutlined />,
      label: '错题本',
    },
    {
      key: '/conversations',
      icon: <MessageOutlined />,
      label: 'AI对话',
    },
  ];

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人资料',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '设置',
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  const handleUserMenuClick = ({ key }: { key: string }) => {
    switch (key) {
      case 'profile':
        navigate('/profile');
        break;
      case 'settings':
        // TODO: 实现设置页面
        break;
      case 'logout':
        logout();
        navigate('/login');
        break;
    }
  };

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        style={{
          background: '#fff',
          boxShadow: '2px 0 8px rgba(0,0,0,0.1)',
        }}
      >
        <div style={{ 
          padding: '16px', 
          textAlign: 'center',
          borderBottom: '1px solid #f0f0f0',
          marginBottom: '16px'
        }}>
          <Text strong style={{ fontSize: collapsed ? '16px' : '18px', color: '#1890ff' }}>
            {collapsed ? 'AI' : 'AI教育助手'}
          </Text>
        </div>
        
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ border: 'none' }}
        />
      </Sider>
      
      <AntLayout>
        <Header style={{ 
          padding: '0 24px', 
          background: '#fff',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{ fontSize: '16px', width: 64, height: 64 }}
          />
          
          <Space>
            <Dropdown
              menu={{ 
                items: userMenuItems,
                onClick: handleUserMenuClick 
              }}
              placement="bottomRight"
            >
              <Space style={{ cursor: 'pointer' }}>
                <Avatar icon={<UserOutlined />} />
                <Text strong>{user?.nickname || user?.username}</Text>
              </Space>
            </Dropdown>
          </Space>
        </Header>
        
        <Content style={{ 
          margin: '24px 16px',
          padding: 24,
          background: '#fff',
          borderRadius: '8px',
          minHeight: 'calc(100vh - 112px)',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          {children}
        </Content>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout;

