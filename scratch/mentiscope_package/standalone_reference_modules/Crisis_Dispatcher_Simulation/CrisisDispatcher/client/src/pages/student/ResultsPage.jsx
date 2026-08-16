import { useState, useEffect } from 'react';
import { Card, Typography, Row, Col, Progress, Spin, Button, Result, Rate, Statistic, Divider, Tag } from 'antd';
import {
  SafetyCertificateOutlined,
  WarningOutlined,
  AimOutlined,
  DashboardOutlined,
  TrophyOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import { studentService } from '../../api/services';
import { useNavigate } from 'react-router-dom';

const { Title, Text } = Typography;

export default function ResultsPage() {
  const [resultData, setResultData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadResults();
  }, []);

  const loadResults = async () => {
    try {
      const res = await studentService.getResult();
      const scores = res.data.data;
      // Backend returns an array of scores sorted by completedAt desc — take the latest
      if (Array.isArray(scores) && scores.length > 0) {
        setResultData(scores[0]);
      } else if (scores && !Array.isArray(scores)) {
        setResultData(scores);
      } else {
        setError('No completed assessment found.');
      }
    } catch (err) {
      if (err.response?.status === 404) {
        setError('No completed assessment found.');
      } else {
        setError('Failed to load results. Please try again.');
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: 100 }}><Spin size="large" /></div>;
  }

  if (error) {
    return (
      <Card style={{ maxWidth: 600, margin: '40px auto', textAlign: 'center', borderRadius: 16 }}>
        <Result
          status="warning"
          title={error}
          extra={
            <Button type="primary" size="large" onClick={() => navigate('/dashboard')}>
              Return to Dashboard
            </Button>
          }
        />
      </Card>
    );
  }

  const { overallScore, dimensions, metrics, gameplayStats } = resultData;

  // Calculate Star Rating based on overallScore
  let rating = 0;
  if (overallScore >= 90) rating = 5;
  else if (overallScore >= 75) rating = 4;
  else if (overallScore >= 60) rating = 3;
  else if (overallScore >= 40) rating = 2;
  else if (overallScore > 0) rating = 1;

  return (
    <div className="animate-fade-in" style={{ paddingBottom: 60 }}>
      <div style={{ textAlign: 'center', marginBottom: 40 }}>
        <Title level={2} style={{ color: '#FFC107', textShadow: '0 2px 10px rgba(255,193,7,0.3)', margin: 0 }}>
          MISSION COMPLETE
        </Title>
        <Text type="secondary" style={{ fontSize: 16 }}>Command Center Simulation Finished</Text>
      </div>

      <Row gutter={[24, 24]}>
        {/* Left Column: Mission Summary & Stats */}
        <Col xs={24} lg={10}>
          <Card 
            title={<><TrophyOutlined style={{ color: '#FFC107' }} /> MISSION SUMMARY</>}
            style={{ borderRadius: 12, height: '100%', border: '1px solid #1B3A5C' }}
            bodyStyle={{ padding: 24 }}
          >
            <div style={{ textAlign: 'center', marginBottom: 24 }}>
              <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>MISSION RATING</Text>
              <Rate disabled defaultValue={rating} style={{ fontSize: 36, color: '#FFC107' }} />
            </div>
            
            <Divider />

            <Row gutter={[16, 24]}>
              <Col span={12}>
                <Statistic 
                  title="Incidents Resolved" 
                  value={gameplayStats?.incidentsResolved || 0} 
                  prefix={<CheckCircleOutlined style={{ color: '#4CAF50' }}/>} 
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="Citizens Saved" 
                  value={gameplayStats?.citizensSaved || 0} 
                  prefix={<SafetyCertificateOutlined style={{ color: '#00E676' }}/>} 
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="Lives Lost" 
                  value={gameplayStats?.livesLost || 0} 
                  prefix={<WarningOutlined style={{ color: '#F44336' }}/>} 
                  valueStyle={{ color: '#F44336' }}
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="Resources Used" 
                  value={gameplayStats?.resourcesUsed || 0} 
                  prefix={<AimOutlined style={{ color: '#03A9F4' }}/>} 
                />
              </Col>
              <Col span={24}>
                <Statistic 
                  title="Average Response Time" 
                  value={((metrics?.avgReactionTime || 0) / 1000).toFixed(1)} 
                  suffix="seconds"
                  prefix={<DashboardOutlined style={{ color: '#FF9800' }}/>} 
                />
              </Col>
            </Row>
          </Card>
        </Col>

        {/* Right Column: Behavioural Assessment */}
        <Col xs={24} lg={14}>
          <Card 
            title={<><DashboardOutlined style={{ color: '#00E676' }} /> BEHAVIOURAL ASSESSMENT</>}
            style={{ borderRadius: 12, border: '1px solid #1B3A5C', marginBottom: 24 }}
          >
            <div style={{ textAlign: 'center', marginBottom: 32 }}>
              <Text type="secondary">Overall Emotional Regulation Score</Text>
              <div style={{ display: 'flex', justifyContent: 'center', marginTop: 12 }}>
                <Progress 
                  type="dashboard" 
                  percent={overallScore} 
                  strokeColor={overallScore >= 70 ? '#00E676' : overallScore >= 40 ? '#FFC107' : '#FF4D4F'}
                  format={percent => <span style={{ color: '#fff', fontSize: 32, fontWeight: 'bold' }}>{percent}</span>}
                  width={150}
                />
              </div>
            </div>

            <Row gutter={[24, 24]}>
              <Col xs={12} sm={6} style={{ textAlign: 'center' }}>
                <Progress type="circle" percent={dimensions?.recoveryResilience || 0} width={80} strokeColor="#03A9F4" format={p => <span style={{ color: '#fff' }}>{p}%</span>} />
                <Text style={{ display: 'block', marginTop: 8, fontSize: 12 }}>Recovery & Resilience</Text>
              </Col>
              <Col xs={12} sm={6} style={{ textAlign: 'center' }}>
                <Progress type="circle" percent={dimensions?.stressTolerance || 0} width={80} strokeColor="#FF4D4F" format={p => <span style={{ color: '#fff' }}>{p}%</span>} />
                <Text style={{ display: 'block', marginTop: 8, fontSize: 12 }}>Stress Tolerance</Text>
              </Col>
              <Col xs={12} sm={6} style={{ textAlign: 'center' }}>
                <Progress type="circle" percent={dimensions?.adaptationPersistence || 0} width={80} strokeColor="#FFC107" format={p => <span style={{ color: '#fff' }}>{p}%</span>} />
                <Text style={{ display: 'block', marginTop: 8, fontSize: 12 }}>Adaptation & Persistence</Text>
              </Col>
              <Col xs={12} sm={6} style={{ textAlign: 'center' }}>
                <Progress type="circle" percent={dimensions?.decisionStability || 0} width={80} strokeColor="#9C27B0" format={p => <span style={{ color: '#fff' }}>{p}%</span>} />
                <Text style={{ display: 'block', marginTop: 8, fontSize: 12 }}>Decision Stability</Text>
              </Col>
            </Row>
          </Card>

          <Card 
            title="Behavioural Metrics Details"
            style={{ borderRadius: 12, border: '1px solid #1B3A5C' }}
            size="small"
          >
            <Row gutter={[16, 12]}>
              <Col span={12}><Text type="secondary">Avg. Reaction Time:</Text></Col>
              <Col span={12} style={{ textAlign: 'right' }}><Tag color="blue">{((metrics?.avgReactionTime || 0)/1000).toFixed(1)}s</Tag></Col>
              
              <Col span={12}><Text type="secondary">Panic Clicks:</Text></Col>
              <Col span={12} style={{ textAlign: 'right' }}><Tag color="red">{metrics?.panicClickFrequency || 0}</Tag></Col>
              
              <Col span={12}><Text type="secondary">Recovery Latency:</Text></Col>
              <Col span={12} style={{ textAlign: 'right' }}><Tag color="orange">{((metrics?.avgRecoveryLatency || 0)/1000).toFixed(1)}s</Tag></Col>
              
              <Col span={12}><Text type="secondary">Decision Accuracy:</Text></Col>
              <Col span={12} style={{ textAlign: 'right' }}><Tag color="green">{metrics?.decisionAccuracy || 0}%</Tag></Col>
              
              <Col span={12}><Text type="secondary">Strategy Changes:</Text></Col>
              <Col span={12} style={{ textAlign: 'right' }}><Tag color="purple">{metrics?.strategyChanges || 0}</Tag></Col>
              
              <Col span={12}><Text type="secondary">Adaptation Rate:</Text></Col>
              <Col span={12} style={{ textAlign: 'right' }}><Tag color="cyan">{(metrics?.adaptationRate || 0)}/1.0</Tag></Col>
            </Row>
          </Card>
        </Col>
      </Row>

      <div style={{ textAlign: 'center', marginTop: 40 }}>
        <Button type="primary" size="large" onClick={() => navigate('/dashboard')} style={{ padding: '0 40px' }}>
          Return to Command Center
        </Button>
      </div>
    </div>
  );
}
