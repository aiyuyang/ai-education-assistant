import React, { useState } from 'react';
import { 
  Card, 
  Button, 
  Table, 
  Tag, 
  Space, 
  Modal, 
  Form, 
  Input, 
  Select, 
  InputNumber,
  Switch,
  message,
  Popconfirm,
  Typography,
  Row,
  Col,
  Statistic
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  BookOutlined,
  ClockCircleOutlined,
  UserOutlined
} from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/api';
import { StudyPlan, StudyPlanCreateRequest } from '../types';

const { Title } = Typography;
const { Option } = Select;

const StudyPlansPage: React.FC = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingPlan, setEditingPlan] = useState<StudyPlan | null>(null);
  const [form] = Form.useForm();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const handleApiError = (error: any) => {
    const status = error?.response?.status;
    if (status === 401) {
      message.warning('登录已过期，请重新登录');
      navigate('/login');
      return;
    }
    message.error(error?.response?.data?.message || '请求失败');
  };

  // 获取学习计划列表
  const { data: plansData, isLoading } = useQuery(
    'studyPlans',
    () => apiService.getStudyPlans(),
    {
      onError: handleApiError
    }
  );

  // 创建学习计划
  const createMutation = useMutation(
    (data: StudyPlanCreateRequest) => apiService.createStudyPlan(data),
    {
      onSuccess: () => {
        message.success('学习计划创建成功');
        setIsModalVisible(false);
        form.resetFields();
        queryClient.invalidateQueries('studyPlans');
      },
      onError: handleApiError
    }
  );

  // 更新学习计划
  const updateMutation = useMutation(
    ({ id, data }: { id: number; data: Partial<StudyPlanCreateRequest> }) => 
      apiService.updateStudyPlan(id, data),
    {
      onSuccess: () => {
        message.success('学习计划更新成功');
        setIsModalVisible(false);
        setEditingPlan(null);
        form.resetFields();
        queryClient.invalidateQueries('studyPlans');
      },
      onError: handleApiError
    }
  );

  // 删除学习计划
  const deleteMutation = useMutation(
    (id: number) => apiService.deleteStudyPlan(id),
    {
      onSuccess: () => {
        message.success('学习计划删除成功');
        queryClient.invalidateQueries('studyPlans');
      },
      onError: handleApiError
    }
  );

  const handleCreate = () => {
    setEditingPlan(null);
    setIsModalVisible(true);
    form.resetFields();
  };

  const handleEdit = (plan: StudyPlan) => {
    setEditingPlan(plan);
    setIsModalVisible(true);
    form.setFieldsValue({
      title: plan.title,
      description: plan.description,
      subject: plan.subject,
      difficulty_level: plan.difficulty_level,
      estimated_duration: plan.estimated_duration,
      is_public: plan.is_public,
    });
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      // 强制数值与布尔类型
      const payload: StudyPlanCreateRequest = {
        title: values.title,
        description: values.description,
        subject: values.subject,
        difficulty_level: values.difficulty_level,
        estimated_duration: Number(values.estimated_duration) || 1,
        is_public: !!values.is_public,
      };
      
      if (editingPlan) {
        updateMutation.mutate({ id: editingPlan.id, data: payload });
      } else {
        createMutation.mutate(payload);
      }
    } catch (error) {
      console.error('表单验证失败:', error);
    }
  };

  const handleDelete = (id: number) => {
    deleteMutation.mutate(id);
  };

  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      render: (text: string, record: StudyPlan) => (
        <Space>
          <BookOutlined />
          <span style={{ fontWeight: 'bold' }}>{text}</span>
        </Space>
      ),
    },
    {
      title: '学科',
      dataIndex: 'subject',
      key: 'subject',
      render: (subject: string) => (
        <Tag color="blue">{subject}</Tag>
      ),
    },
    {
      title: '难度',
      dataIndex: 'difficulty_level',
      key: 'difficulty_level',
      render: (level: string) => {
        const colors = {
          beginner: 'green',
          intermediate: 'orange',
          advanced: 'red'
        };
        const labels = {
          beginner: '初级',
          intermediate: '中级',
          advanced: '高级'
        };
        return <Tag color={colors[level as keyof typeof colors]}>{labels[level as keyof typeof labels]}</Tag>;
      },
    },
    {
      title: '预计时长',
      dataIndex: 'estimated_duration',
      key: 'estimated_duration',
      render: (duration: number) => (
        <Space>
          <ClockCircleOutlined />
          {duration} 天
        </Space>
      ),
    },
    {
      title: '公开',
      dataIndex: 'is_public',
      key: 'is_public',
      render: (isPublic: boolean) => (
        <Tag color={isPublic ? 'green' : 'default'}>
          {isPublic ? '公开' : '私有'}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, record: StudyPlan) => (
        <Space>
          <Button 
            type="link" 
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个学习计划吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button 
              type="link" 
              danger 
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const plans = plansData?.data || [];

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>学习计划管理</Title>
        <Button 
          type="primary" 
          icon={<PlusOutlined />}
          onClick={handleCreate}
          size="large"
        >
          创建学习计划
        </Button>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总计划数"
              value={plans.length}
              prefix={<BookOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="公开计划"
              value={plans.filter(p => p.is_public).length}
              prefix={<UserOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总学习时长"
              value={plans.reduce((sum: number, p: any) => sum + (Number(p?.estimated_duration ?? 0) || 0), 0)}
              suffix="天"
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="平均时长"
              value={plans.length > 0 ? Math.round(
                plans.reduce((sum: number, p: any) => sum + (Number(p?.estimated_duration ?? 0) || 0), 0) / plans.length
              ) : 0}
              suffix="天"
            />
          </Card>
        </Col>
      </Row>

      {/* 学习计划表格 */}
      <Card>
        <Table
          columns={columns}
          dataSource={plans}
          loading={isLoading}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 个学习计划`,
          }}
        />
      </Card>

      {/* 创建/编辑模态框 */}
      <Modal
        title={editingPlan ? '编辑学习计划' : '创建学习计划'}
        open={isModalVisible}
        onOk={handleSubmit}
        onCancel={() => {
          setIsModalVisible(false);
          setEditingPlan(null);
          form.resetFields();
        }}
        confirmLoading={createMutation.isLoading || updateMutation.isLoading}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            difficulty_level: 'beginner',
            estimated_duration: 7,
            is_public: false,
          }}
        >
          <Form.Item
            name="title"
            label="计划标题"
            rules={[{ required: true, message: '请输入计划标题' }]}
          >
            <Input placeholder="请输入学习计划标题" />
          </Form.Item>

          <Form.Item
            name="description"
            label="计划描述"
            rules={[{ required: true, message: '请输入计划描述' }]}
          >
            <Input.TextArea 
              rows={4} 
              placeholder="请描述学习计划的内容和目标" 
            />
          </Form.Item>

          <Form.Item
            name="subject"
            label="学科"
            rules={[{ required: true, message: '请选择学科' }]}
          >
            <Select placeholder="请选择学科">
              <Option value="数学">数学</Option>
              <Option value="语文">语文</Option>
              <Option value="英语">英语</Option>
              <Option value="物理">物理</Option>
              <Option value="化学">化学</Option>
              <Option value="生物">生物</Option>
              <Option value="历史">历史</Option>
              <Option value="地理">地理</Option>
              <Option value="政治">政治</Option>
              <Option value="编程">编程</Option>
              <Option value="其他">其他</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="difficulty_level"
            label="难度等级"
            rules={[{ required: true, message: '请选择难度等级' }]}
          >
            <Select>
              <Option value="beginner">初级</Option>
              <Option value="intermediate">中级</Option>
              <Option value="advanced">高级</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="estimated_duration"
            label="预计学习时长（天）"
            rules={[{ required: true, message: '请输入预计学习时长' }]}
          >
            <InputNumber 
              min={1} 
              max={365} 
              style={{ width: '100%' }}
              placeholder="请输入预计学习天数"
            />
          </Form.Item>

          <Form.Item
            name="is_public"
            label="是否公开"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default StudyPlansPage;
