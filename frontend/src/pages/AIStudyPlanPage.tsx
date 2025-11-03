import React, { useState } from 'react';
import { Card, Form, Input, Select, InputNumber, Button, Typography, message, Row, Col, Tag, Divider, List, Spin, Space, Badge, Collapse, Timeline, Tooltip } from 'antd';
import { RobotOutlined, CopyOutlined, ReloadOutlined } from '@ant-design/icons';
import apiService from '../services/api';
import { useNavigate } from 'react-router-dom';

const { Title, Text } = Typography;
const { Option } = Select;

const AIStudyPlanPage: React.FC = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [lastParams, setLastParams] = useState<any>(null);

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);
      setResult(null);
      const payload = {
        subject: values.subject,
        time_frame: values.time_frame,
        learning_goals: values.learning_goals || [],
        current_level: values.current_level,
        study_hours_per_week: values.study_hours_per_week,
      };
      setLastParams(payload);
      const resp = await apiService.generateAIStudyPlan(payload);
      setResult(resp.data);
      message.success('AI 学习计划生成成功');
      if (resp?.data?.saved_plan_id) {
        message.success(`已保存到学习计划（ID: ${resp.data.saved_plan_id}）`);
      }
    } catch (error: any) {
      // 处理后端错误响应
      const status = error?.response?.status;
      const msg = error?.response?.data?.message || '生成学习计划失败';
      setResult(error?.response?.data);
      if (status === 422) {
        message.error(`请求参数或AI响应不合法：${msg}`);
      } else if (status === 502) {
        message.error(`外部服务错误：${msg}`);
      } else if (status === 401) {
        message.warning('登录已过期，请重新登录');
      } else {
        message.error(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  const priorityColor = (p?: string) => {
    if (!p) return 'default';
    const val = String(p).toLowerCase();
    if (val === 'high') return 'volcano';
    if (val === 'medium') return 'gold';
    if (val === 'low') return 'green';
    return 'blue';
  };

  const renderPlan = () => {
    if (loading) {
      return (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 240 }}>
          <Spin tip="正在生成学习计划..." />
        </div>
      );
    }
    if (!result) {
      return <Text type="secondary">提交后将在此展示生成的学习计划或错误信息。</Text>;
    }

    const objectives: string[] = result.learning_objectives || [];
    const weeks: any[] = result.weekly_schedule || [];

    return (
      <div>
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <div>
            <Title level={3} style={{ marginTop: 0 }}>{result.plan_title || '学习计划'}</Title>
            {lastParams && (
              <Space wrap size={[8, 8]} style={{ marginTop: 8 }}>
                <Tag color="geekblue">科目：{lastParams.subject}</Tag>
                <Tag color="purple">时间范围：{lastParams.time_frame}</Tag>
                <Tag color="cyan">水平：{lastParams.current_level}</Tag>
                <Tag color="blue">每周：{lastParams.study_hours_per_week} 小时</Tag>
                <Tag>{weeks.length} 周</Tag>
              </Space>
            )}
            {result?.saved_plan_id && (
              <div style={{ marginTop: 8 }}>
                <Space>
                  <Tag color="green">已保存 (ID: {result.saved_plan_id})</Tag>
                  <Button size="small" onClick={() => navigate('/study-plans')}>查看学习计划</Button>
                </Space>
              </div>
            )}
            <div style={{ marginTop: 12 }}>
              <Text>{result.overview}</Text>
            </div>
          </div>

          <div>
            <Text strong>学习目标：</Text>
            <div style={{ marginTop: 8 }}>
              {objectives.length > 0 ? objectives.map((obj, idx) => (
                <Tag color="blue" key={idx} style={{ marginBottom: 8 }}>{obj}</Tag>
              )) : <Text type="secondary">暂无目标</Text>}
            </div>
          </div>

          <div>
            <Text strong>周计划：</Text>
            <Collapse accordion style={{ marginTop: 12 }}>
              {weeks.map((weekItem) => (
                <Collapse.Panel
                  header={
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                      <Space size={8}>
                        <Badge status="processing" />
                        <span>第 {weekItem.week} 周</span>
                        {weekItem.focus && <Tag color="blue">{weekItem.focus}</Tag>}
                      </Space>
                      <Space size={8}>
                        {Array.isArray(weekItem.tasks) && (
                          <Tag>{weekItem.tasks.length} 项任务</Tag>
                        )}
                      </Space>
                    </div>
                  }
                  key={weekItem.week}
                >
                  {Array.isArray(weekItem.tasks) && weekItem.tasks.length > 0 ? (
                    <Timeline mode="left">
                      {weekItem.tasks.map((task: any, i: number) => (
                        <Timeline.Item key={i} dot={<Badge color="#1890ff" />}> 
                          <Card size="small" bordered>
                            <Space direction="vertical" style={{ width: '100%' }}>
                              <Space align="baseline" style={{ justifyContent: 'space-between', width: '100%' }}>
                                <Text strong>{task.title}</Text>
                                <Space>
                                  {typeof task.estimated_hours === 'number' && (
                                    <Tag color="geekblue">{task.estimated_hours} 小时</Tag>
                                  )}
                                  {task.priority && <Tag color={priorityColor(task.priority)}>{task.priority}</Tag>}
                                </Space>
                              </Space>
                              {task.description && (
                                <Text type="secondary">{task.description}</Text>
                              )}
                              {Array.isArray(task.resources) && task.resources.length > 0 && (
                                <div>
                                  <Text type="secondary">资源：</Text>
                                  <Space wrap size={[8, 8]} style={{ marginTop: 4 }}>
                                    {task.resources.map((r: string, idx: number) => (
                                      <Tag key={idx}>{r}</Tag>
                                    ))}
                                  </Space>
                                </div>
                              )}
                            </Space>
                          </Card>
                        </Timeline.Item>
                      ))}
                    </Timeline>
                  ) : (
                    <Text type="secondary">本周暂无任务</Text>
                  )}
                </Collapse.Panel>
              ))}
            </Collapse>
          </div>

          <Space>
            <Tooltip title="复制计划 JSON 到剪贴板">
              <Button icon={<CopyOutlined />} onClick={() => navigator.clipboard.writeText(JSON.stringify(result, null, 2))}>复制 JSON</Button>
            </Tooltip>
            <Tooltip title="清空结果">
              <Button icon={<ReloadOutlined />} onClick={() => setResult(null)}>清空</Button>
            </Tooltip>
          </Space>
        </Space>
      </div>
    );
  };

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <RobotOutlined /> AI学习计划生成
        </Title>
        <Text type="secondary">填写学习目标与时长，调用后端生成结构化学习计划</Text>
      </div>

      <Row gutter={24} align="top">
        <Col xs={24} lg={10}>
          <Card title="生成参数">
            <Form
              form={form}
              layout="vertical"
              initialValues={{
                subject: '',
                time_frame: '8周',
                current_level: 'beginner',
                study_hours_per_week: 10,
                learning_goals: [],
              }}
            >
              <Row gutter={16}>
                <Col xs={24} md={12}>
                  <Form.Item
                    label="科目"
                    name="subject"
                    rules={[{ required: true, message: '请输入科目' }]}
                  >
                    <Input placeholder="例如：数学、英语、编程" />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item
                    label="时间范围"
                    name="time_frame"
                    rules={[{ required: true, message: '请输入时间范围' }]}
                  >
                    <Input placeholder="例如：8周、2个月" />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col xs={24} md={12}>
                  <Form.Item
                    label="当前水平"
                    name="current_level"
                    rules={[{ required: true, message: '请选择当前水平' }]}
                  >
                    <Select>
                      <Option value="beginner">初级</Option>
                      <Option value="intermediate">中级</Option>
                      <Option value="advanced">高级</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item
                    label="每周学习小时数"
                    name="study_hours_per_week"
                    rules={[{ required: true, message: '请输入每周学习小时数' }]}
                  >
                    <InputNumber min={1} max={80} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item label="学习目标" name="learning_goals">
                <Select mode="tags" placeholder="输入并回车添加目标，如：掌握基础语法">
                  {/* 使用 tags 模式，用户可自由输入目标 */}
                </Select>
              </Form.Item>

              <Button type="primary" onClick={handleSubmit} loading={loading}>
                生成学习计划
              </Button>
            </Form>
          </Card>
        </Col>
        <Col xs={24} lg={14}>
          <div style={{ position: 'sticky', top: 24 }}>
            <Card title="学习计划展示">{renderPlan()}</Card>
          </div>
        </Col>
      </Row>
    </div>
  );
};

export default AIStudyPlanPage;