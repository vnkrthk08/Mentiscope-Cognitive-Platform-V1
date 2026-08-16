import { useState, useEffect } from 'react';
import { Card, Table, Tag, Input, Typography, Space, Collapse, Descriptions, Spin } from 'antd';
import { TeamOutlined, SearchOutlined } from '@ant-design/icons';
import { adminService } from '../../api/services';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

export default function StudentsPage() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({ page: 1, limit: 20, total: 0 });
  const [search, setSearch] = useState('');

  useEffect(() => {
    loadStudents();
  }, [pagination.page, search]);

  const loadStudents = async () => {
    setLoading(true);
    try {
      const res = await adminService.getStudents({
        page: pagination.page,
        limit: pagination.limit,
        search,
      });
      setStudents(res.data.data.students);
      setPagination((prev) => ({ ...prev, total: res.data.data.pagination.total }));
    } catch (error) {
      console.error('Failed to load students:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      render: (name) => <Text strong>{name}</Text>,
    },
    {
      title: 'Email',
      dataIndex: 'email',
    },
    {
      title: 'Registered',
      dataIndex: 'createdAt',
      render: (val) => dayjs(val).format('MMM DD, YYYY'),
      responsive: ['md'],
    },
    {
      title: 'Assessments',
      dataIndex: 'totalAssessments',
      render: (val) => <Tag color="blue">{val}</Tag>,
    },
    {
      title: 'Latest Score',
      dataIndex: ['latestScore', 'overallScore'],
      render: (score) => score != null ? (
        <Tag color={score >= 70 ? 'green' : score >= 40 ? 'orange' : 'red'} style={{ fontSize: 14 }}>
          {score}/100
        </Tag>
      ) : <Text type="secondary">—</Text>,
      sorter: (a, b) => (a.latestScore?.overallScore || 0) - (b.latestScore?.overallScore || 0),
    },
  ];

  const expandedRowRender = (record) => {
    const score = record.latestScore;
    if (!score) return <Text type="secondary">No assessment data available.</Text>;

    return (
      <div style={{ padding: '8px 0' }}>
        <Descriptions bordered size="small" column={{ xs: 1, sm: 2, md: 4 }}>
          <Descriptions.Item label="Overall Score">
            <Tag color={score.overallScore >= 70 ? 'green' : 'orange'}>{score.overallScore}/100</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Recovery & Resilience">
            {score.dimensions?.recoveryResilience || 0}%
          </Descriptions.Item>
          <Descriptions.Item label="Stress Tolerance">
            {score.dimensions?.stressTolerance || 0}%
          </Descriptions.Item>
          <Descriptions.Item label="Adaptation">
            {score.dimensions?.adaptationPersistence || 0}%
          </Descriptions.Item>
          <Descriptions.Item label="Decision Stability">
            {score.dimensions?.decisionStability || 0}%
          </Descriptions.Item>
          <Descriptions.Item label="Reaction Time">
            {score.metrics?.avgReactionTime || 0}ms
          </Descriptions.Item>
          <Descriptions.Item label="Decision Accuracy">
            {score.metrics?.decisionAccuracy || 0}%
          </Descriptions.Item>
          <Descriptions.Item label="Panic Clicks">
            {score.metrics?.panicClickFrequency || 0}
          </Descriptions.Item>
          <Descriptions.Item label="Module 1">{score.moduleScores?.module1 || 0}</Descriptions.Item>
          <Descriptions.Item label="Module 2">{score.moduleScores?.module2 || 0}</Descriptions.Item>
          <Descriptions.Item label="Module 3">{score.moduleScores?.module3 || 0}</Descriptions.Item>
          <Descriptions.Item label="Module 4">{score.moduleScores?.module4 || 0}</Descriptions.Item>
        </Descriptions>
      </div>
    );
  };

  return (
    <div className="animate-fade-in">
      <Title level={3} style={{ marginBottom: 24 }}>
        <TeamOutlined style={{ marginRight: 8 }} />
        Students
      </Title>

      <Card style={{ borderRadius: 12 }}>
        <div style={{ marginBottom: 16 }}>
          <Input
            placeholder="Search by name or email..."
            prefix={<SearchOutlined />}
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPagination((prev) => ({ ...prev, page: 1 }));
            }}
            allowClear
            style={{ maxWidth: 400 }}
          />
        </div>

        <Table
          columns={columns}
          dataSource={students}
          rowKey="id"
          loading={loading}
          expandable={{
            expandedRowRender,
            rowExpandable: (record) => record.latestScore != null,
          }}
          pagination={{
            current: pagination.page,
            pageSize: pagination.limit,
            total: pagination.total,
            showSizeChanger: false,
            onChange: (page) => setPagination((prev) => ({ ...prev, page })),
          }}
          scroll={{ x: 700 }}
        />
      </Card>
    </div>
  );
}
