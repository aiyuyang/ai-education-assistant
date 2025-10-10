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
  FileTextOutlined,
  QuestionCircleOutlined,
  CloseCircleOutlined
} from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import apiService from '../services/api';
import { ErrorLog, ErrorLogCreateRequest } from '../types';
import { useNavigate } from 'react-router-dom';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const ErrorLogsPage: React.FC = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingLog, setEditingLog] = useState<ErrorLog | null>(null);
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

  // 获取错题列表
  const { data: logsData, isLoading } = useQuery(
    'errorLogs',
    () => apiService.getErrorLogs(),
    {
      onError: handleApiError
    }
  );

  // 获取错题统计
  const { data: statsData } = useQuery(
    'errorLogStats',
    () => apiService.getErrorLogStats(),
    {
      onError: handleApiError
    }
  );

  // 创建错题记录
  const createMutation = useMutation(
    (data: ErrorLogCreateRequest) => apiService.createErrorLog(data),
    {
      onSuccess: () => {
        message.success('错题记录创建成功');
        setIsModalVisible(false);
        form.resetFields();
        queryClient.invalidateQueries('errorLogs');
        queryClient.invalidateQueries('errorLogStats');
      },
      onError: handleApiError
    }
  );

  // 更新错题记录
  const updateMutation = useMutation(
    ({ id, data }: { id: number; data: Partial<ErrorLogCreateRequest> }) => 
      apiService.updateErrorLog(id, data),
    {
      onSuccess: () => {
        message.success('错题记录更新成功');
        setIsModalVisible(false);
        setEditingLog(null);
        form.resetFields();
        queryClient.invalidateQueries('errorLogs');
      },
      onError: handleApiError
    }
  );

  // 删除错题记录
  const deleteMutation = useMutation(
    (id: number) => apiService.deleteErrorLog(id),
    {
      onSuccess: () => {
        message.success('错题记录删除成功');
        queryClient.invalidateQueries('errorLogs');
        queryClient.invalidateQueries('errorLogStats');
      },
      onError: handleApiError
    }
  );

  const handleCreate = () => {
    setEditingLog(null);
    setIsModalVisible(true);
    form.resetFields();
  };

  const handleEdit = (log: ErrorLog) => {
    setEditingLog(log);
    setIsModalVisible(true);
    form.setFieldsValue({
      subject: log.subject,
      topic: (log as any).topic,
      question_content: (log as any).question_content,
      correct_answer: (log as any).correct_answer,
      explanation: (log as any).explanation,
      difficulty: ((log as any).difficulty || (log as any).difficulty_level || 'MEDIUM'),
    });
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingLog) {
        updateMutation.mutate({ id: editingLog.id, data: values });
      } else {
        createMutation.mutate(values);
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
      title: '题目',
      dataIndex: 'question_content',
      key: 'question_content',
      width: 360,
      render: (text: string, record: ErrorLog) => (
        <div style={{ maxWidth: 280 }}>
          <Text ellipsis={{ tooltip: (record as any)?.question_content || '' }}>{(record as any)?.question_content || '-'}</Text>
        </div>
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
      title: '主题',
      dataIndex: 'topic',
      key: 'topic',
      render: (topic: string) => topic || '-',
    },
    {
      title: '难度',
      dataIndex: 'difficulty',
      key: 'difficulty',
      render: (level: string) => {
        const colors = {
          EASY: 'green',
          MEDIUM: 'orange',
          HARD: 'red'
        };
        const labels = {
          EASY: '简单',
          MEDIUM: '中等',
          HARD: '困难'
        };
        return <Tag color={colors[(level as any) as keyof typeof colors] || 'default'}>{labels[(level as any) as keyof typeof labels] || level}</Tag>;
      },
    },
    {
      title: '正确答案',
      dataIndex: 'correct_answer',
      key: 'correct_answer',
      width: 200,
      render: (text: string) => (text || '-')
    },
    {
      title: '记录时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, record: ErrorLog) => (
        <Space>
          <Button 
            type="link" 
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这条错题记录吗？"
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

  const logs = Array.isArray(logsData?.data) ? (logsData!.data as any[]) : [];
  const statsRaw: any = statsData?.data || {};
  const subjects = statsRaw.subjects_distribution || statsRaw.subjects || {};
  const difficultyDist = statsRaw.difficulty_distribution || {};
  const totalCount =
    typeof statsRaw.total_count === 'number'
      ? statsRaw.total_count
      : logs.length;

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>错题本</Title>
        <Button 
          type="primary" 
          icon={<PlusOutlined />}
          onClick={handleCreate}
          size="large"
        >
          记录错题
        </Button>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic title="总错题数" value={totalCount} prefix={<FileTextOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="本月错题"
              value={logs.filter(log => {
                const logDate = new Date(log.created_at);
                const now = new Date();
                return logDate.getMonth() === now.getMonth() && 
                       logDate.getFullYear() === now.getFullYear();
              }).length}
              prefix={<QuestionCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="困难题数"
              value={difficultyDist.HARD || logs.filter((log: any) => (log.difficulty || log.difficulty_level) === 'HARD').length}
              prefix={<CloseCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="学科数量"
              value={Object.keys(subjects).length}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 学科统计 */}
      {Object.keys(subjects).length > 0 && (
        <Card title="学科错题分布" style={{ marginBottom: '24px' }}>
          <Row gutter={16}>
            {Object.entries(subjects).map(([subject, count]) => (
              <Col span={6} key={subject}>
                <Card size="small">
                  <Statistic
                    title={subject}
                    value={count as number}
                    prefix={<FileTextOutlined />}
                  />
                </Card>
              </Col>
            ))}
          </Row>
        </Card>
      )}

      {/* 错题列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={Array.isArray(logs) ? logs : []}
          loading={isLoading}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条错题记录`,
          }}
          expandable={{
            expandedRowRender: (record) => (
              <div style={{ padding: '16px', background: '#fafafa', borderRadius: '6px' }}>
                <Title level={5}>题目详情</Title>
                <Text>{(record as any).question_content || '-'}</Text>
                
                <Title level={5} style={{ marginTop: '16px' }}>正确答案</Title>
                <Text type="success">{(record as any).correct_answer || '-'}</Text>
                
                <Title level={5} style={{ marginTop: '16px' }}>解析</Title>
                <Text>{(record as any).explanation || '-'}</Text>
              </div>
            ),
            rowExpandable: (record) => !!(record as any).explanation,
          }}
        />
      </Card>

      {/* 创建/编辑模态框 */}
      <Modal
        title={editingLog ? '编辑错题记录' : '记录错题'}
        open={isModalVisible}
        onOk={handleSubmit}
        onCancel={() => {
          setIsModalVisible(false);
          setEditingLog(null);
          form.resetFields();
        }}
        confirmLoading={createMutation.isLoading || updateMutation.isLoading}
        width={700}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            difficulty: 'MEDIUM',
          }}
        >
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
            name="topic"
            label="主题（可选）"
          >
            <Input placeholder="如：函数、古诗、语法等" />
          </Form.Item>

          <Form.Item
            name="question_content"
            label="题目"
            rules={[{ required: true, message: '请输入题目' }]}
          >
            <TextArea 
              rows={3} 
              placeholder="请输入题目内容" 
            />
          </Form.Item>

          <Form.Item
            name="correct_answer"
            label="正确答案"
            rules={[{ required: true, message: '请输入正确答案' }]}
          >
            <TextArea 
              rows={2} 
              placeholder="请输入正确答案" 
            />
          </Form.Item>

          <Form.Item
            name="difficulty"
            label="难度等级"
            rules={[{ required: true, message: '请选择难度等级' }]}
          >
            <Select>
              <Option value="EASY">简单</Option>
              <Option value="MEDIUM">中等</Option>
              <Option value="HARD">困难</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="explanation"
            label="解析"
            rules={[{ required: true, message: '请输入题目解析' }]}
          >
            <TextArea 
              rows={4} 
              placeholder="请输入题目解析，帮助理解错误原因" 
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ErrorLogsPage;
