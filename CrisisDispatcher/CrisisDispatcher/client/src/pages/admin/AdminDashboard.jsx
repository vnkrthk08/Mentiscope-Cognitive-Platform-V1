import { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, Tag, Spin, Typography, Space, Modal, Tabs, Button } from 'antd';
import {
  TeamOutlined,
  FileTextOutlined,
  TrophyOutlined,
  RiseOutlined,
  BarChartOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { adminService } from '../../api/services';
import dayjs from 'dayjs';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell
} from 'recharts';
import EventTimeline from './components/EventTimeline';
import ExportButtons from './components/ExportButtons';

const { Title, Text } = Typography;

const COLORS = ['#DC3545', '#FF6B6B', '#FFC107', '#28A745', '#1B3A5C', '#17A2B8'];

export default function AdminDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedSessionId, setSelectedSessionId] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const res = await adminService.getDashboard();
      setData(res.data.data);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const viewTimeline = (sessionId) => {
    setSelectedSessionId(sessionId);
    setIsModalVisible(true);
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: 80 }}><Spin size="large" /></div>;
  }

  if (!data) return null;

  const { stats, recentAssessments, scoreDistribution, moduleAvg } = data;

  const distLabels = ['0-19', '20-39', '40-59', '60-79', '80-100'];
  const distData = (scoreDistribution || []).map((item, i) => ({
    range: distLabels[i] || `${item._id}`,
    count: item.count,
  }));

  const moduleData = [
    { name: 'Level 1', score: Math.round(moduleAvg?.module1 || 0), fill: '#1B3A5C' },
    { name: 'Level 2', score: Math.round(moduleAvg?.module2 || 0), fill: '#DC3545' },
    { name: 'Level 3', score: Math.round(moduleAvg?.module3 || 0), fill: '#FFC107' },
    { name: 'Level 4', score: Math.round(moduleAvg?.module4 || 0), fill: '#17A2B8' },
  ];

  const columns = [
    {
      title: 'Student',
      dataIndex: ['studentId', 'name'],
      render: (name, record) => (
        <div>
          <Text strong>{name}</Text>
          <br />
          <Text type="secondary" style={{ fontSize: 12 }}>{record.studentId?.email}</Text>
        </div>
      ),
    },
    {
      title: 'Score',
      dataIndex: 'overallScore',
      render: (score) => (
        <Tag color={score >= 70 ? 'green' : score >= 40 ? 'orange' : 'red'} style={{ fontSize: 14, padding: '2px 12px' }}>
          {score}/100
        </Tag>
      ),
      sorter: (a, b) => a.overallScore - b.overallScore,
    },
    {
      title: 'Date',
      dataIndex: 'completedAt',
      render: (val) => dayjs(val).format('MMM DD, YYYY'),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Button 
          type="link" 
          icon={<EyeOutlined />} 
          onClick={() => viewTimeline(record.sessionId)}
        >
          View Timeline
        </Button>
      )
    },
  ];

  const prepareExportData = () => {
    return recentAssessments.map(a => ({
      Student_Name: a.studentId?.name,
      Student_Email: a.studentId?.email,
      Date: dayjs(a.completedAt).format('YYYY-MM-DD HH:mm:ss'),
      Overall_Score: a.overallScore,
      Recovery_Resilience: a.dimensions?.recoveryResilience,
      Stress_Tolerance: a.dimensions?.stressTolerance,
      Adaptation_Persistence: a.dimensions?.adaptationPersistence,
      Decision_Stability: a.dimensions?.decisionStability,
    }));
  };

  const items = [
    {
      key: 'analytics',
      label: 'Analytics',
      children: (
        <>
          {/* Stats Cards */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={12} sm={6}>
              <Card className="stat-card stat-card-primary card-hover">
                <Statistic
                  title="Total Students"
                  value={stats.totalStudents}
                  prefix={<TeamOutlined />}
                  valueStyle={{ color: '#1B3A5C' }}
                />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card className="stat-card stat-card-success card-hover">
                <Statistic
                  title="Assessments"
                  value={stats.totalAssessments}
                  prefix={<FileTextOutlined />}
                  valueStyle={{ color: '#28A745' }}
                />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card className="stat-card stat-card-warning card-hover">
                <Statistic
                  title="Average Score"
                  value={stats.avgScore}
                  suffix="/100"
                  prefix={<RiseOutlined />}
                  valueStyle={{ color: '#FFC107' }}
                />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card className="stat-card stat-card-accent card-hover">
                <Statistic
                  title="Highest Score"
                  value={stats.highestScore}
                  suffix="/100"
                  prefix={<TrophyOutlined />}
                  valueStyle={{ color: '#DC3545' }}
                />
              </Card>
            </Col>
          </Row>

          {/* Charts Row */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} md={12}>
              <Card title="Score Distribution" style={{ borderRadius: 12, height: '100%' }}>
                {distData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={240}>
                    <BarChart data={distData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis dataKey="range" tick={{ fontSize: 12 }} />
                      <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                      <Tooltip />
                      <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                        {distData.map((_, index) => (
                          <Cell key={index} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <Text type="secondary">No data yet</Text>
                )}
              </Card>
            </Col>
            <Col xs={24} md={12}>
              <Card title="Average Level Performance" style={{ borderRadius: 12, height: '100%' }}>
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={moduleData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Bar dataKey="score" radius={[6, 6, 0, 0]}>
                      {moduleData.map((entry, index) => (
                        <Cell key={index} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
          </Row>
        </>
      ),
    },
    {
      key: 'assessments',
      label: 'Assessments',
      children: (
        <Card
          title="Recent Assessments"
          extra={<ExportButtons data={prepareExportData()} filenamePrefix="Assessments" />}
          style={{ borderRadius: 12 }}
        >
          <Table
            columns={columns}
            dataSource={recentAssessments}
            rowKey="_id"
            pagination={{ pageSize: 10 }}
            scroll={{ x: 700 }}
          />
        </Card>
      ),
    },
    { key: 'students', label: 'Students', children: <Card><Text>Student management view coming soon.</Text></Card> },
    { key: 'sessions', label: 'Sessions', children: <Card><Text>Active and past session logs coming soon.</Text></Card> },
    { key: 'events', label: 'Event Logs', children: <Card><Text>Global raw event log query interface coming soon. Use Assessments tab to view specific timelines.</Text></Card> }
  ];

  return (
    <div className="animate-fade-in">
      <Title level={3} style={{ marginBottom: 24 }}>
        <BarChartOutlined style={{ marginRight: 8 }} />
        Admin Dashboard
      </Title>

      <Tabs defaultActiveKey="1" items={items} />

      <Modal
        title="Student Behavioural Timeline"
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
        width={700}
      >
        {selectedSessionId && <EventTimeline sessionId={selectedSessionId} />}
      </Modal>
    </div>
  );
}
