import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Row, Col, Button, Typography, Tag, Table, Statistic, Space, Spin, Empty } from 'antd';
import {
  PlayCircleOutlined,
  TrophyOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  BarChartOutlined,
  RocketOutlined,
} from '@ant-design/icons';
import { useAuth } from '../../contexts/AuthContext';
import { studentService } from '../../api/services';
import ScoreGauge from '../../components/ScoreGauge';
import dayjs from 'dayjs';

const { Title, Text, Paragraph } = Typography;

export default function StudentDashboard() {
  const [profile, setProfile] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [profileRes, resultRes] = await Promise.all([
        studentService.getProfile(),
        studentService.getResult(),
      ]);
      setProfile(profileRes.data.data);
      setResults(resultRes.data.data);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: 'Date',
      dataIndex: 'completedAt',
      render: (val) => dayjs(val).format('MMM DD, YYYY - HH:mm'),
    },
    {
      title: 'Overall Score',
      dataIndex: 'overallScore',
      render: (score) => (
        <Tag color={score >= 70 ? 'green' : score >= 40 ? 'orange' : 'red'}>
          {score}/100
        </Tag>
      ),
      sorter: (a, b) => a.overallScore - b.overallScore,
    },
    {
      title: 'Recovery',
      dataIndex: ['dimensions', 'recoveryResilience'],
      render: (v) => `${v || 0}%`,
    },
    {
      title: 'Stress',
      dataIndex: ['dimensions', 'stressTolerance'],
      render: (v) => `${v || 0}%`,
    },
    {
      title: 'Adaptation',
      dataIndex: ['dimensions', 'adaptationPersistence'],
      render: (v) => `${v || 0}%`,
    },
    {
      title: 'Stability',
      dataIndex: ['dimensions', 'decisionStability'],
      render: (v) => `${v || 0}%`,
    },
    {
      title: 'Action',
      render: (_, record) => (
        <Button type="link" onClick={() => navigate('/results', { state: { scoreId: record._id } })}>
          View Details
        </Button>
      ),
    },
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 80 }}>
        <Spin size="large" />
      </div>
    );
  }

  const latestScore = profile?.latestScore;
  const isInProgress = profile?.assessmentStatus === 'in-progress';

  return (
    <div className="animate-fade-in">
      {/* Welcome Section */}
      <Card
        style={{
          marginBottom: 24,
          background: 'linear-gradient(135deg, #0A0F1E 0%, #131A2D 100%)',
          border: '1px solid rgba(255, 77, 79, 0.2)',
          boxShadow: '0 0 20px rgba(255, 77, 79, 0.1)',
          borderRadius: 16,
        }}
      >
        <Row align="middle" gutter={[24, 24]}>
          <Col xs={24} md={16}>
            <Title level={2} style={{ color: '#fff', margin: 0 }}>
              Welcome back, {user?.name}! 👋
            </Title>
            <Paragraph style={{ color: 'rgba(255,255,255,0.7)', fontSize: 16, marginTop: 8, marginBottom: 20 }}>
              Ready to test your emotional regulation? The platform continuously records behavioural interactions 
              during the emergency response simulation to evaluate your decision-making under stress.
            </Paragraph>
            <Button
              type="primary"
              size="large"
              icon={isInProgress ? <RocketOutlined /> : <PlayCircleOutlined />}
              onClick={() => navigate('/assessment')}
              style={{
                height: 48,
                fontSize: 16,
                fontWeight: 600,
                background: 'linear-gradient(135deg, #FF4D4F 0%, #FF7875 100%)',
                border: 'none',
                borderRadius: 10,
                paddingInline: 32,
                boxShadow: '0 4px 14px rgba(255, 77, 79, 0.4)',
              }}
            >
              {isInProgress ? 'Resume Assessment' : 'Start Assessment'}
            </Button>
          </Col>
          <Col xs={24} md={8} style={{ textAlign: 'center' }}>
            {latestScore ? (
              <ScoreGauge score={latestScore.overallScore} size={150} label="Latest Score" />
            ) : (
              <div style={{
                width: 150,
                height: 150,
                borderRadius: '50%',
                background: 'rgba(255,255,255,0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto',
              }}>
                <Text style={{ color: 'rgba(255,255,255,0.6)', textAlign: 'center', fontSize: 13 }}>
                  No assessment<br />completed yet
                </Text>
              </div>
            )}
          </Col>
        </Row>
      </Card>

      {/* Stats Row */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card className="stat-card stat-card-primary card-hover">
            <Statistic
              title="Assessments"
              value={profile?.totalAssessments || 0}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card className="stat-card stat-card-accent card-hover">
            <Statistic
              title="Latest Score"
              value={latestScore?.overallScore || '—'}
              suffix={latestScore ? '/100' : ''}
              prefix={<TrophyOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card className="stat-card stat-card-success card-hover">
            <Statistic
              title="Status"
              value={isInProgress ? 'In Progress' : 'Ready'}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card className="stat-card stat-card-warning card-hover">
            <Statistic
              title="Best Dimension"
              value={latestScore ? getBestDimension(latestScore.dimensions) : '—'}
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* Assessment History */}
      <Card
        title={
          <Space>
            <ClockCircleOutlined />
            <span>Assessment History</span>
          </Space>
        }
        style={{ borderRadius: 12 }}
      >
        {results.length > 0 ? (
          <Table
            columns={columns}
            dataSource={results}
            rowKey="_id"
            pagination={{ pageSize: 5 }}
            scroll={{ x: 800 }}
          />
        ) : (
          <Empty
            description="No assessments completed yet"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          >
            <Button type="primary" onClick={() => navigate('/assessment')}>
              Take Your First Assessment
            </Button>
          </Empty>
        )}
      </Card>
    </div>
  );
}

function getBestDimension(dimensions) {
  if (!dimensions) return '—';
  const map = {
    recoveryResilience: 'Recovery',
    stressTolerance: 'Stress',
    adaptationPersistence: 'Adaptation',
    decisionStability: 'Stability',
  };
  let best = '';
  let max = -1;
  for (const [key, label] of Object.entries(map)) {
    if ((dimensions[key] || 0) > max) {
      max = dimensions[key] || 0;
      best = label;
    }
  }
  return best;
}
