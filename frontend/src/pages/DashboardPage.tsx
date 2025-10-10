import React from 'react';
import { Card, Row, Col, Statistic, Typography, Button, Space, Progress, List } from 'antd';
import { 
  BookOutlined, 
  FileTextOutlined, 
  MessageOutlined, 
  PlusOutlined,
  TrophyOutlined,
  ClockCircleOutlined,
  FireOutlined,
  StarOutlined,
  RocketOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useQuery } from 'react-query';
import apiService from '../services/api';

const { Title, Text } = Typography;

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  // 获取用户统计
  const { data: statsData } = useQuery(
    'userStats',
    () => apiService.getUserStats(),
    {
      onError: () => {
        // 静默处理错误，使用默认值
      }
    }
  );

  // 获取学习计划
  const { data: plansData } = useQuery(
    'studyPlans',
    () => apiService.getStudyPlans(),
    {
      onError: () => {
        // 静默处理错误，使用默认值
      }
    }
  );

  const stats = statsData?.data || {
    study_plans_count: 0,
    error_logs_count: 0,
    conversations_count: 0,
    total_study_time: 0
  };

  const plans = plansData?.data || [];

  const quickActions = [
    {
      title: '创建学习计划',
      icon: <PlusOutlined />,
      color: '#1890ff',
      onClick: () => navigate('/study-plans'),
      description: '制定新的学习计划'
    },
    {
      title: '记录错题',
      icon: <FileTextOutlined />,
      color: '#f5222d',
      onClick: () => navigate('/error-logs'),
      description: '记录学习中的错题'
    },
    {
      title: 'AI对话',
      icon: <MessageOutlined />,
      color: '#52c41a',
      onClick: () => navigate('/conversations'),
      description: '与AI助手交流学习'
    },
    {
      title: '个人资料',
      icon: <BookOutlined />,
      color: '#fa8c16',
      onClick: () => navigate('/profile'),
      description: '查看个人信息'
    }
  ];

  const achievements = [
    {
      title: '学习新手',
      description: '完成第一个学习计划',
      icon: <TrophyOutlined />,
      color: '#faad14',
      unlocked: stats.study_plans_count > 0
    },
    {
      title: '错题收集家',
      description: '记录10道错题',
      icon: <FileTextOutlined />,
      color: '#f5222d',
      unlocked: stats.error_logs_count >= 10
    },
    {
      title: 'AI助手',
      description: '与AI对话10次',
      icon: <MessageOutlined />,
      color: '#52c41a',
      unlocked: stats.conversations_count >= 10
    },
    {
      title: '学习达人',
      description: '学习时长超过50小时',
      icon: <ClockCircleOutlined />,
      color: '#1890ff',
      unlocked: stats.total_study_time >= 50
    }
  ];

  const recentActivities = [
    {
      title: '完成了Python基础语法学习',
      time: '2小时前',
      type: 'study'
    },
    {
      title: '记录了3道数学错题',
      time: '1天前',
      type: 'error'
    },
    {
      title: '与AI助手讨论了算法问题',
      time: '2天前',
      type: 'conversation'
    },
    {
      title: '创建了新的学习计划',
      time: '3天前',
      type: 'plan'
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>
          欢迎回来，{user?.nickname || user?.username}！
        </Title>
        <Text type="secondary">继续您的学习之旅，探索更多知识</Text>
      </div>

      {/* 学习统计 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="学习计划"
              value={stats.study_plans_count}
              prefix={<BookOutlined style={{ color: '#1890ff' }} />}
              suffix="个"
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="错题记录"
              value={stats.error_logs_count}
              prefix={<FileTextOutlined style={{ color: '#f5222d' }} />}
              suffix="道"
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="AI对话"
              value={stats.conversations_count}
              prefix={<MessageOutlined style={{ color: '#52c41a' }} />}
              suffix="次"
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="学习时长"
              value={stats.total_study_time}
              prefix={<ClockCircleOutlined style={{ color: '#fa8c16' }} />}
              suffix="小时"
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* 快速操作 */}
        <Col xs={24} lg={12}>
          <Card title="快速操作" extra={<RocketOutlined />}>
            <Row gutter={[12, 12]}>
              {quickActions.map((action, index) => (
                <Col span={12} key={index}>
                  <Card
                    size="small"
                    hoverable
                    onClick={action.onClick}
                    style={{ 
                      textAlign: 'center',
                      cursor: 'pointer',
                      border: `2px solid ${action.color}20`
                    }}
                  >
                    <div style={{ color: action.color, fontSize: '24px', marginBottom: '8px' }}>
                      {action.icon}
                    </div>
                    <Text strong>{action.title}</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {action.description}
                    </Text>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>

        {/* 最近活动 */}
        <Col xs={24} lg={12}>
          <Card title="最近活动" extra={<FireOutlined />}>
            <List
              size="small"
              dataSource={recentActivities}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={
                      item.type === 'study' ? <BookOutlined style={{ color: '#1890ff' }} /> :
                      item.type === 'error' ? <FileTextOutlined style={{ color: '#f5222d' }} /> :
                      item.type === 'conversation' ? <MessageOutlined style={{ color: '#52c41a' }} /> :
                      <PlusOutlined style={{ color: '#fa8c16' }} />
                    }
                    title={<Text strong>{item.title}</Text>}
                    description={<Text type="secondary">{item.time}</Text>}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        {/* 学习进度 */}
        <Col xs={24} lg={16}>
          <Card title="学习进度">
            <Row gutter={16}>
              <Col span={12}>
                <div style={{ textAlign: 'center', marginBottom: '16px' }}>
                  <Text strong>本月学习进度</Text>
                  <Progress 
                    type="circle" 
                    percent={75} 
                    strokeColor="#1890ff"
                    format={() => '75%'}
                  />
                </div>
              </Col>
              <Col span={12}>
                <div style={{ textAlign: 'center', marginBottom: '16px' }}>
                  <Text strong>年度目标</Text>
                  <Progress 
                    type="circle" 
                    percent={45} 
                    strokeColor="#52c41a"
                    format={() => '45%'}
                  />
                </div>
              </Col>
            </Row>
            
            {plans.length > 0 && (
              <div style={{ marginTop: '16px' }}>
                <Text strong>进行中的学习计划：</Text>
                <List
                  size="small"
                  dataSource={plans.slice(0, 3)}
                  renderItem={(plan) => (
                    <List.Item>
                      <List.Item.Meta
                        avatar={<BookOutlined />}
                        title={plan.title}
                        description={`${plan.subject} • ${plan.difficulty_level}`}
                      />
                      <Progress 
                        percent={Math.floor(Math.random() * 100)} 
                        size="small" 
                        style={{ width: '100px' }}
                      />
                    </List.Item>
                  )}
                />
              </div>
            )}
          </Card>
        </Col>

        {/* 成就徽章 */}
        <Col xs={24} lg={8}>
          <Card title="成就徽章" extra={<StarOutlined />}>
            <Row gutter={[8, 8]}>
              {achievements.map((achievement, index) => (
                <Col span={12} key={index}>
                  <Card
                    size="small"
                    style={{ 
                      textAlign: 'center',
                      opacity: achievement.unlocked ? 1 : 0.5,
                      backgroundColor: achievement.unlocked ? `${achievement.color}10` : '#f5f5f5'
                    }}
                  >
                    <div style={{ 
                      color: achievement.unlocked ? achievement.color : '#d9d9d9', 
                      fontSize: '24px', 
                      marginBottom: '8px' 
                    }}>
                      {achievement.icon}
                    </div>
                    <Text strong style={{ fontSize: '12px' }}>{achievement.title}</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: '10px' }}>
                      {achievement.description}
                    </Text>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardPage;
