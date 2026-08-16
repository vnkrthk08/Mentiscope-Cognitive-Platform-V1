import { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Typography, Spin, Space } from 'antd';
import {
  BarChartOutlined,
  ClockCircleOutlined,
  AimOutlined,
  HeartOutlined,
  SafetyOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import { adminService } from '../../api/services';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, Area, AreaChart, RadarChart, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, Radar, Legend,
} from 'recharts';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

export default function AnalyticsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const res = await adminService.getResults({ page: 1, limit: 100 });
      setData(res.data.data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: 80 }}><Spin size="large" /></div>;
  }

  if (!data) return null;

  const { analytics, trend } = data;

  const trendData = (trend || []).map((t, i) => ({
    index: i + 1,
    date: dayjs(t.completedAt).format('MM/DD'),
    score: t.overallScore,
    stress: t.dimensions?.stressTolerance || 0,
    stability: t.dimensions?.decisionStability || 0,
    reactionTime: t.metrics?.avgReactionTime || 0,
  }));

  const dimensionAvg = [
    { dimension: 'Recovery', value: Math.round(analytics?.avgRecovery || 0) },
    { dimension: 'Stress', value: Math.round(analytics?.avgStress || 0) },
    { dimension: 'Adaptation', value: Math.round(analytics?.avgAdaptation || 0) },
    { dimension: 'Decision', value: Math.round(analytics?.avgDecision || 0) },
  ];

  const dimensionColors = ['#28A745', '#DC3545', '#17A2B8', '#FFC107'];

  return (
    <div className="animate-fade-in">
      <Title level={3} style={{ marginBottom: 24 }}>
        <BarChartOutlined style={{ marginRight: 8 }} />
        Analytics
      </Title>

      {/* Summary Stats */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={8} md={4}>
          <Card className="stat-card stat-card-primary card-hover" bodyStyle={{ padding: 16 }}>
            <Statistic title="Avg Score" value={Math.round(analytics?.avgOverall || 0)} suffix="/100"
              valueStyle={{ fontSize: 22 }} />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card className="stat-card stat-card-accent card-hover" bodyStyle={{ padding: 16 }}>
            <Statistic title="Avg Reaction" value={Math.round(analytics?.avgReactionTime || 0)} suffix="ms"
              prefix={<ClockCircleOutlined />} valueStyle={{ fontSize: 22 }} />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card className="stat-card stat-card-success card-hover" bodyStyle={{ padding: 16 }}>
            <Statistic title="Avg Accuracy" value={Math.round(analytics?.avgAccuracy || 0)} suffix="%"
              prefix={<AimOutlined />} valueStyle={{ fontSize: 22 }} />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card className="stat-card stat-card-warning card-hover" bodyStyle={{ padding: 16 }}>
            <Statistic title="Recovery" value={Math.round(analytics?.avgRecovery || 0)} suffix="%"
              prefix={<HeartOutlined />} valueStyle={{ fontSize: 22 }} />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card className="stat-card stat-card-primary card-hover" bodyStyle={{ padding: 16 }}>
            <Statistic title="Stress Tol." value={Math.round(analytics?.avgStress || 0)} suffix="%"
              prefix={<ThunderboltOutlined />} valueStyle={{ fontSize: 22 }} />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={4}>
          <Card className="stat-card stat-card-success card-hover" bodyStyle={{ padding: 16 }}>
            <Statistic title="Stability" value={Math.round(analytics?.avgDecision || 0)} suffix="%"
              prefix={<SafetyOutlined />} valueStyle={{ fontSize: 22 }} />
          </Card>
        </Col>
      </Row>

      {/* Score Trend */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={16}>
          <Card title="Score Trend (Last 30 Assessments)" style={{ borderRadius: 12, height: '100%' }}>
            {trendData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={trendData}>
                  <defs>
                    <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#1B3A5C" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#1B3A5C" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Area type="monotone" dataKey="score" stroke="#1B3A5C" fill="url(#scoreGrad)" strokeWidth={2} name="Overall Score" />
                  <Line type="monotone" dataKey="stress" stroke="#DC3545" strokeWidth={1.5} dot={false} name="Stress Tolerance" />
                  <Line type="monotone" dataKey="stability" stroke="#FFC107" strokeWidth={1.5} dot={false} name="Decision Stability" />
                  <Legend />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <Text type="secondary">No trend data available yet</Text>
            )}
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Average Dimension Scores" style={{ borderRadius: 12, height: '100%' }}>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={dimensionAvg}>
                <PolarGrid stroke="#e8e8e8" />
                <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 10 }} />
                <Radar name="Average" dataKey="value" stroke="#1B3A5C" fill="#1B3A5C" fillOpacity={0.25} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Reaction Time Trend */}
      <Card title="Reaction Time Trend" style={{ borderRadius: 12 }}>
        {trendData.length > 0 ? (
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={(val) => `${val}ms`} />
              <Line type="monotone" dataKey="reactionTime" stroke="#17A2B8" strokeWidth={2} dot={{ fill: '#17A2B8' }} name="Reaction Time (ms)" />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <Text type="secondary">No data available</Text>
        )}
      </Card>
    </div>
  );
}
