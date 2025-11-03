import React, { useState, useRef, useEffect } from 'react';
import { 
  Card, 
  Button, 
  Input, 
  List, 
  Avatar, 
  Typography, 
  Space, 
  Modal, 
  Form, 
  Select, 
  Switch,
  message,
  Popconfirm,
  Row,
  Col,
  Statistic,
  Spin
} from 'antd';
import { 
  SendOutlined, 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  MessageOutlined,
  UserOutlined,
  RobotOutlined,
  CommentOutlined
} from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import apiService from '../services/api';
import { Conversation, ConversationCreateRequest, Message, MessageCreateRequest } from '../types';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const ConversationsPage: React.FC = () => {
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingConversation, setEditingConversation] = useState<Conversation | null>(null);
  const [newMessage, setNewMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [form] = Form.useForm();
  const queryClient = useQueryClient();

  // 获取对话列表
  const { data: conversationsData, isLoading: conversationsLoading } = useQuery(
    'conversations',
    () => apiService.getConversations(),
    {
      onError: () => {
        message.error('获取对话列表失败');
      }
    }
  );

  // 获取消息列表
  const { data: messagesData, isLoading: messagesLoading } = useQuery(
    ['messages', selectedConversation?.id],
    () => selectedConversation 
      ? apiService.getMessages(selectedConversation.id) 
      : Promise.resolve({ code: 0 as any, message: 'ok', data: [] }),
    {
      enabled: !!selectedConversation,
      onError: () => {
        message.error('获取消息失败');
      }
    }
  );

  // 获取对话统计
  const { data: statsData } = useQuery(
    'conversationStats',
    () => apiService.getConversationStats(),
    {
      onError: () => {
        message.error('获取对话统计失败');
      }
    }
  );

  // 创建对话
  const createConversationMutation = useMutation(
    (data: ConversationCreateRequest) => apiService.createConversation(data),
    {
      onSuccess: (response) => {
        message.success('对话创建成功');
        setIsModalVisible(false);
        form.resetFields();
        queryClient.invalidateQueries('conversations');
        queryClient.invalidateQueries('conversationStats');
        setSelectedConversation(response.data);
      },
      onError: (error: any) => {
        message.error(error.response?.data?.message || '创建失败');
      }
    }
  );

  // 更新对话
  const updateConversationMutation = useMutation(
    ({ id, data }: { id: number; data: Partial<ConversationCreateRequest> }) => 
      apiService.updateConversation(id, data),
    {
      onSuccess: () => {
        message.success('对话更新成功');
        setIsModalVisible(false);
        setEditingConversation(null);
        form.resetFields();
        queryClient.invalidateQueries('conversations');
      },
      onError: (error: any) => {
        message.error(error.response?.data?.message || '更新失败');
      }
    }
  );

  // 删除对话
  const deleteConversationMutation = useMutation(
    (id: number) => apiService.deleteConversation(id),
    {
      onSuccess: () => {
        message.success('对话删除成功');
        queryClient.invalidateQueries('conversations');
        queryClient.invalidateQueries('conversationStats');
        if (selectedConversation) {
          setSelectedConversation(null);
        }
      },
      onError: (error: any) => {
        message.error(error.response?.data?.message || '删除失败');
      }
    }
  );

  // 发送消息
  const sendMessageMutation = useMutation(
    ({ conversationId, data }: { conversationId: number; data: MessageCreateRequest }) => 
      apiService.createMessage(conversationId, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['messages', selectedConversation?.id]);
        setNewMessage('');
        setIsSending(false);
      },
      onError: (error: any) => {
        message.error(error.response?.data?.message || '发送失败');
        setIsSending(false);
      }
    }
  );

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messagesData]);

  const handleCreateConversation = () => {
    setEditingConversation(null);
    setIsModalVisible(true);
    form.resetFields();
  };

  const handleEditConversation = (conversation: Conversation) => {
    setEditingConversation(conversation);
    setIsModalVisible(true);
    form.setFieldsValue({
      title: conversation.title,
      subject: conversation.subject,
      difficulty_level: conversation.difficulty_level,
      is_public: conversation.is_public,
    });
  };

  const handleSubmitConversation = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingConversation) {
        updateConversationMutation.mutate({ id: editingConversation.id, data: values });
      } else {
        createConversationMutation.mutate(values);
      }
    } catch (error) {
      console.error('表单验证失败:', error);
    }
  };

  const handleDeleteConversation = (id: number) => {
    deleteConversationMutation.mutate(id);
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !selectedConversation) return;
    
    setIsSending(true);
    
    // 发送用户消息
    await sendMessageMutation.mutateAsync({
      conversationId: selectedConversation.id,
      data: {
        content: newMessage,
        role: 'user'
      }
    });

    // 模拟AI回复
    setTimeout(() => {
      sendMessageMutation.mutate({
        conversationId: selectedConversation.id,
        data: {
          content: `我理解你的问题："${newMessage}"。这是一个很好的问题，让我来帮你分析一下...`,
          role: 'assistant'
        }
      });
    }, 1000);
  };

  const conversations = conversationsData?.data || [];
  const messages = messagesData?.data || [];
  const stats = statsData?.data || { total_conversations: 0, subjects: {} };

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>AI对话</Title>
        <Button 
          type="primary" 
          icon={<PlusOutlined />}
          onClick={handleCreateConversation}
          size="large"
        >
          新建对话
        </Button>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总对话数"
              value={stats.total_conversations || 0}
              prefix={<MessageOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="活跃对话"
              value={conversations.length}
              prefix={<CommentOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="公开对话"
              value={conversations.filter(c => c.is_public).length}
              prefix={<UserOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总消息数"
              value={stats.total_messages || 0}
              prefix={<MessageOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        {/* 对话列表 */}
        <Col span={8}>
          <Card title="对话列表" style={{ height: '600px' }}>
            <List
              loading={conversationsLoading}
              dataSource={conversations}
              renderItem={(conversation) => (
                <List.Item
                  style={{ 
                    cursor: 'pointer',
                    backgroundColor: selectedConversation?.id === conversation.id ? '#e6f7ff' : 'transparent',
                    borderRadius: '6px',
                    margin: '4px 0',
                    padding: '12px'
                  }}
                  onClick={() => setSelectedConversation(conversation)}
                  actions={[
                    <Button 
                      type="link" 
                      icon={<EditOutlined />}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEditConversation(conversation);
                      }}
                    />,
                    <Popconfirm
                      title="确定要删除这个对话吗？"
                      onConfirm={(e) => {
                        e?.stopPropagation();
                        handleDeleteConversation(conversation.id);
                      }}
                      okText="确定"
                      cancelText="取消"
                    >
                      <Button 
                        type="link" 
                        danger 
                        icon={<DeleteOutlined />}
                        onClick={(e) => e.stopPropagation()}
                      />
                    </Popconfirm>
                  ]}
                >
                  <List.Item.Meta
                    avatar={<Avatar icon={<MessageOutlined />} />}
                    title={conversation.title}
                    description={
                      <Space>
                        <Text type="secondary">{conversation.subject}</Text>
                        <Text type="secondary">•</Text>
                        <Text type="secondary">{new Date(conversation.created_at).toLocaleDateString()}</Text>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* 消息区域 */}
        <Col span={16}>
          <Card 
            title={selectedConversation ? selectedConversation.title : '选择对话'} 
            style={{ height: '600px' }}
            bodyStyle={{ padding: 0 }}
          >
            {selectedConversation ? (
              <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                {/* 消息列表 */}
                <div style={{ 
                  flex: 1, 
                  padding: '16px 24px', 
                  overflowY: 'auto',
                  maxHeight: '440px'
                }}>
                  {messagesLoading ? (
                    <div style={{ textAlign: 'center', padding: '50px' }}>
                      <Spin />
                    </div>
                  ) : (
                    <List
                      dataSource={messages}
                      renderItem={(message) => (
                        <List.Item style={{ border: 'none', padding: '8px 0' }}>
                          <div style={{ 
                            display: 'flex', 
                            justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                            width: '100%',
                            padding: '4px 0'
                          }}>
                            <div style={{
                              maxWidth: '70%',
                              padding: '12px 16px',
                              borderRadius: '12px',
                              backgroundColor: message.role === 'user' ? '#1890ff' : '#f0f0f0',
                              color: message.role === 'user' ? 'white' : 'black'
                            }}>
                              <Space>
                                {message.role === 'user' ? (
                                  <UserOutlined />
                                ) : (
                                  <RobotOutlined />
                                )}
                                <Text style={{ color: message.role === 'user' ? 'white' : 'black' }}>
                                  {message.content}
                                </Text>
                              </Space>
                            </div>
                          </div>
                        </List.Item>
                      )}
                    />
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* 输入区域 */}
                <div style={{ 
                  padding: '12px 16px', 
                  borderTop: '1px solid #f0f0f0',
                  backgroundColor: '#fafafa'
                }}>
                  <Space.Compact style={{ width: '100%' }}>
                    <TextArea
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      placeholder="输入你的问题..."
                      autoSize={{ minRows: 1, maxRows: 4 }}
                      onPressEnter={(e) => {
                        if (e.shiftKey) return;
                        e.preventDefault();
                        handleSendMessage();
                      }}
                    />
                    <Button 
                      type="primary" 
                      icon={<SendOutlined />}
                      onClick={handleSendMessage}
                      loading={isSending}
                      disabled={!newMessage.trim()}
                    >
                      发送
                    </Button>
                  </Space.Compact>
                </div>
              </div>
            ) : (
              <div style={{ 
                height: '100%', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                color: '#999'
              }}>
                <div style={{ textAlign: 'center' }}>
                  <MessageOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
                  <Text>选择一个对话开始聊天</Text>
                </div>
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {/* 创建/编辑对话模态框 */}
      <Modal
        title={editingConversation ? '编辑对话' : '新建对话'}
        open={isModalVisible}
        onOk={handleSubmitConversation}
        onCancel={() => {
          setIsModalVisible(false);
          setEditingConversation(null);
          form.resetFields();
        }}
        confirmLoading={createConversationMutation.isLoading || updateConversationMutation.isLoading}
        width={500}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            difficulty_level: 'beginner',
            is_public: false,
          }}
        >
          <Form.Item
            name="title"
            label="对话标题"
            rules={[{ required: true, message: '请输入对话标题' }]}
          >
            <Input placeholder="请输入对话标题" />
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

export default ConversationsPage;
