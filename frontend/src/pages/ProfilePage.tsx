import React, { useState } from 'react';
import { 
  Card, 
  Form, 
  Input, 
  Button, 
  Avatar, 
  Upload, 
  message, 
  Typography, 
  Row, 
  Col, 
  Statistic,
  Divider,
  Space,
  Tag
} from 'antd';
import { 
  UserOutlined, 
  MailOutlined, 
  CalendarOutlined,
  BookOutlined,
  FileTextOutlined,
  MessageOutlined,
  UploadOutlined,
  EditOutlined
} from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import apiService from '../services/api';
import { useAuth } from '../hooks/useAuth';

const { Title, Text } = Typography;

const ProfilePage: React.FC = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [form] = Form.useForm();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  // 获取用户统计
  const { data: statsData } = useQuery(
    'userStats',
    () => apiService.getUserStats(),
    {
      onError: () => {
        message.error('获取用户统计失败');
      }
    }
  );

  // 更新用户信息
  const updateMutation = useMutation(
    (data: any) => apiService.updateUserProfile(data),
    {
      onSuccess: (response) => {
        message.success('个人信息更新成功');
        setIsEditing(false);
        // 触发相关数据的刷新（若有对应的 query key）
        try { queryClient.invalidateQueries('userStats'); } catch {}
        try { queryClient.invalidateQueries('userProfile'); } catch {}
      },
      onError: (error: any) => {
        message.error(error.response?.data?.message || '更新失败');
      }
    }
  );

  const handleEdit = () => {
    setIsEditing(true);
    form.setFieldsValue({
      nickname: user?.nickname,
    });
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      updateMutation.mutate(values);
    } catch (error) {
      console.error('表单验证失败:', error);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    form.resetFields();
  };

  const stats = statsData?.data || {
    study_plans_count: 0,
    error_logs_count: 0,
    conversations_count: 0,
    total_study_time: 0
  };

  return (
    <div>
      <Title level={2}>个人资料</Title>
      
      <Row gutter={24}>
        {/* 个人信息卡片 */}
        <Col span={8}>
          <Card>
            <div style={{ textAlign: 'center', marginBottom: '24px' }}>
              <Avatar 
                size={100} 
                icon={<UserOutlined />}
                style={{ marginBottom: '16px' }}
              />
              <Title level={3} style={{ margin: 0 }}>
                {user?.nickname || user?.username}
              </Title>
              <Text type="secondary">@{user?.username}</Text>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <Space>
                <MailOutlined />
                <Text>{user?.email}</Text>
              </Space>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <Space>
                <CalendarOutlined />
                <Text>注册时间: {user?.created_at ? new Date(user.created_at).toLocaleDateString() : '未知'}</Text>
              </Space>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <Space>
                <Text>状态:</Text>
                <Tag color={user?.is_active ? 'green' : 'red'}>
                  {user?.is_active ? '活跃' : '非活跃'}
                </Tag>
                <Tag color={user?.is_verified ? 'blue' : 'orange'}>
                  {user?.is_verified ? '已验证' : '未验证'}
                </Tag>
              </Space>
            </div>

            {!isEditing ? (
              <Button 
                type="primary" 
                icon={<EditOutlined />}
                onClick={handleEdit}
                block
              >
                编辑资料
              </Button>
            ) : (
              <Space style={{ width: '100%' }}>
                <Button 
                  type="primary" 
                  onClick={handleSubmit}
                  loading={updateMutation.isLoading}
                  style={{ flex: 1 }}
                >
                  保存
                </Button>
                <Button 
                  onClick={handleCancel}
                  style={{ flex: 1 }}
                >
                  取消
                </Button>
              </Space>
            )}
          </Card>
        </Col>

        {/* 编辑表单 */}
        <Col span={16}>
          {isEditing ? (
            <Card title="编辑个人信息">
              <Form
                form={form}
                layout="vertical"
                onFinish={handleSubmit}
              >
                <Form.Item
                  name="nickname"
                  label="昵称"
                  rules={[{ required: true, message: '请输入昵称' }]}
                >
                  <Input placeholder="请输入昵称" />
                </Form.Item>

                <Form.Item label="头像">
                  <Upload
                    name="avatar"
                    listType="picture-card"
                    showUploadList={false}
                    beforeUpload={() => {
                      message.info('头像上传功能开发中...');
                      return false;
                    }}
                  >
                    <div>
                      <UploadOutlined />
                      <div style={{ marginTop: 8 }}>上传头像</div>
                    </div>
                  </Upload>
                </Form.Item>
              </Form>
            </Card>
          ) : (
            <Card title="个人简介">
              <Text>
                个人简介功能开发中...
              </Text>
            </Card>
          )}
        </Col>
      </Row>

      <Divider />

      {/* 学习统计 */}
      <Card title="学习统计">
        <Row gutter={16}>
          <Col span={6}>
            <Statistic
              title="学习计划"
              value={stats.study_plans_count}
              prefix={<BookOutlined />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="错题记录"
              value={stats.error_logs_count}
              prefix={<FileTextOutlined />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="AI对话"
              value={stats.conversations_count}
              prefix={<MessageOutlined />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="学习时长"
              value={stats.total_study_time}
              suffix="小时"
              prefix={<CalendarOutlined />}
            />
          </Col>
        </Row>
      </Card>

      {/* 最近活动 */}
      <Card title="最近活动" style={{ marginTop: '24px' }}>
        <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
          <CalendarOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
          <Text>最近活动记录功能开发中...</Text>
        </div>
      </Card>

      {/* 成就徽章 */}
      <Card title="成就徽章" style={{ marginTop: '24px' }}>
        <Row gutter={16}>
          <Col span={8}>
            <Card size="small" style={{ textAlign: 'center' }}>
              <BookOutlined style={{ fontSize: '32px', color: '#52c41a', marginBottom: '8px' }} />
              <div>学习新手</div>
              <Text type="secondary">完成第一个学习计划</Text>
            </Card>
          </Col>
          <Col span={8}>
            <Card size="small" style={{ textAlign: 'center' }}>
              <FileTextOutlined style={{ fontSize: '32px', color: '#1890ff', marginBottom: '8px' }} />
              <div>错题收集家</div>
              <Text type="secondary">记录10道错题</Text>
            </Card>
          </Col>
          <Col span={8}>
            <Card size="small" style={{ textAlign: 'center' }}>
              <MessageOutlined style={{ fontSize: '32px', color: '#fa8c16', marginBottom: '8px' }} />
              <div>AI助手</div>
              <Text type="secondary">与AI对话10次</Text>
            </Card>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default ProfilePage;
