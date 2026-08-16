import { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Typography, Spin, message, Button, Row, Col, Steps, Divider } from 'antd';
import {
  CheckCircleOutlined,
  ThunderboltOutlined,
  ExperimentOutlined,
  AimOutlined,
  PlayCircleOutlined,
  InfoCircleOutlined,
  ClockCircleOutlined,
  AlertOutlined,
  SafetyCertificateOutlined,
  RocketOutlined,
} from '@ant-design/icons';
import { assessmentService } from '../../api/services';
import { MODULE_INFO } from '../../simulation/scenarios/scenarioData';
import CommandCenter from '../../simulation/game/CommandCenter';

const { Title, Text, Paragraph } = Typography;

// ── Guidelines / Instructions Screen ──────────────────────────────
function AssessmentGuidelines({ onBegin, loading: startLoading }) {
  const moduleSteps = [
    {
      icon: '📋',
      title: 'Module 1 — Baseline',
      color: '#1B3A5C',
      desc: 'Single emergencies with generous timers. Establishes your baseline decision-making ability under calm conditions.',
      tip: 'Take your time and focus on accuracy.',
    },
    {
      icon: '⚡',
      title: 'Module 2 — Stress',
      color: '#DC3545',
      desc: 'Multiple simultaneous emergencies with shorter timers. Tests how you perform under pressure.',
      tip: 'Stay calm — incidents arrive rapidly.',
    },
    {
      icon: '🔄',
      title: 'Module 3 — Recovery',
      color: '#FFC107',
      desc: 'Equipment failures and setbacks force you to adapt. Measures your resilience after unexpected problems.',
      tip: 'Don\'t panic on failure — recover quickly.',
    },
    {
      icon: '🎯',
      title: 'Module 4 — Adaptive',
      color: '#17A2B8',
      desc: 'Emergencies dynamically escalate mid-response. Tests your ability to adapt strategy in real-time.',
      tip: 'Watch for situation updates and adjust.',
    },
  ];

  const scoringDimensions = [
    {
      icon: <SafetyCertificateOutlined style={{ fontSize: 22, color: '#03A9F4' }} />,
      title: 'Recovery & Resilience',
      weight: '30%',
      desc: 'How quickly you bounce back from failures and maintain performance after setbacks.',
    },
    {
      icon: <ThunderboltOutlined style={{ fontSize: 22, color: '#FF4D4F' }} />,
      title: 'Stress Tolerance',
      weight: '25%',
      desc: 'Your accuracy and calmness under time pressure and simultaneous emergencies.',
    },
    {
      icon: <AimOutlined style={{ fontSize: 22, color: '#FFC107' }} />,
      title: 'Adaptation & Persistence',
      weight: '25%',
      desc: 'Your ability to change strategy when situations escalate and keep trying after difficulties.',
    },
    {
      icon: <ExperimentOutlined style={{ fontSize: 22, color: '#9C27B0' }} />,
      title: 'Decision Stability',
      weight: '20%',
      desc: 'Consistency of your decisions over time — avoiding erratic or impulsive choices.',
    },
  ];

  return (
    <div className="animate-fade-in" style={{ maxWidth: 900, margin: '0 auto', paddingBottom: 60 }}>
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: 36 }}>
        <div style={{
          width: 72, height: 72, borderRadius: '50%',
          background: 'linear-gradient(135deg, rgba(255,77,79,0.2) 0%, rgba(255,77,79,0.05) 100%)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          margin: '0 auto 16px',
          border: '2px solid rgba(255,77,79,0.3)',
        }}>
          <InfoCircleOutlined style={{ fontSize: 32, color: '#FF4D4F' }} />
        </div>
        <Title level={2} style={{ color: '#fff', margin: 0 }}>
          Assessment Briefing
        </Title>
        <Text type="secondary" style={{ fontSize: 16 }}>
          Read carefully before you begin the simulation
        </Text>
      </div>

      {/* What is this? */}
      <Card style={{
        borderRadius: 16,
        marginBottom: 20,
        border: '1px solid rgba(255,77,79,0.15)',
        background: 'linear-gradient(135deg, #131A2D 0%, #0E1525 100%)',
      }}>
        <Title level={4} style={{ color: '#FF4D4F', margin: '0 0 12px' }}>
          <RocketOutlined /> What Is This Assessment?
        </Title>
        <Paragraph style={{ color: 'rgba(255,255,255,0.8)', fontSize: 15, margin: 0, lineHeight: 1.8 }}>
          You are the <strong style={{ color: '#FF4D4F' }}>Crisis Dispatch Commander</strong>. 
          Emergency incidents will appear on your screen — your job is to <strong>select the correct emergency resources</strong> (Ambulance, 
          Fire Truck, Police Unit, Medical Team, or Rescue Team) and <strong>dispatch them before time runs out</strong>.
        </Paragraph>
        <Paragraph style={{ color: 'rgba(255,255,255,0.8)', fontSize: 15, margin: '12px 0 0', lineHeight: 1.8 }}>
          The system continuously records your behavioural interactions — <strong>reaction speed</strong>, <strong>decision accuracy</strong>, 
          <strong> panic responses</strong>, and <strong>recovery from failures</strong> — to generate an{' '}
          <strong style={{ color: '#00E676' }}>Emotional Regulation Score</strong>.
        </Paragraph>
      </Card>

      {/* How to Play */}
      <Card style={{
        borderRadius: 16,
        marginBottom: 20,
        border: '1px solid rgba(0,230,118,0.15)',
        background: 'linear-gradient(135deg, #131A2D 0%, #0E1525 100%)',
      }}>
        <Title level={4} style={{ color: '#00E676', margin: '0 0 16px' }}>
          <PlayCircleOutlined /> How to Play
        </Title>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {[
            { step: '1', text: 'An emergency incident card appears with a description and countdown timer.', color: '#03A9F4' },
            { step: '2', text: 'Click on the incident card to SELECT it (it highlights when selected).', color: '#FFC107' },
            { step: '3', text: 'From the Resource Bay at the bottom, click the correct resource(s) to dispatch.', color: '#00E676' },
            { step: '4', text: 'If the correct resources are dispatched, the unit heads out. If not, try again before the timer expires.', color: '#FF4D4F' },
            { step: '5', text: 'The assessment tracks everything — speed, accuracy, panic clicks, and how you handle surprises.', color: '#9C27B0' },
          ].map(({ step, text, color }) => (
            <div key={step} style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
              <div style={{
                minWidth: 32, height: 32, borderRadius: '50%',
                background: `${color}22`, border: `1.5px solid ${color}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 700, color, fontSize: 14,
              }}>
                {step}
              </div>
              <Text style={{ color: 'rgba(255,255,255,0.85)', fontSize: 14, lineHeight: '32px' }}>{text}</Text>
            </div>
          ))}
        </div>
      </Card>

      {/* The 4 Modules */}
      <Card style={{
        borderRadius: 16,
        marginBottom: 20,
        border: '1px solid rgba(27,58,92,0.4)',
        background: 'linear-gradient(135deg, #131A2D 0%, #0E1525 100%)',
      }}>
        <Title level={4} style={{ color: '#03A9F4', margin: '0 0 16px' }}>
          <ClockCircleOutlined /> The 4 Modules
        </Title>
        <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
          You will progress through 4 modules automatically. Each module increases in difficulty.
        </Text>
        <Row gutter={[12, 12]}>
          {moduleSteps.map((mod, i) => (
            <Col xs={24} sm={12} key={i}>
              <div style={{
                padding: 16,
                borderRadius: 12,
                background: `${mod.color}0A`,
                border: `1px solid ${mod.color}30`,
                height: '100%',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                  <span style={{ fontSize: 20 }}>{mod.icon}</span>
                  <Text strong style={{ color: mod.color, fontSize: 14 }}>{mod.title}</Text>
                </div>
                <Text style={{ color: 'rgba(255,255,255,0.7)', fontSize: 13, display: 'block', lineHeight: 1.5 }}>
                  {mod.desc}
                </Text>
                <div style={{
                  marginTop: 8,
                  padding: '4px 10px',
                  background: 'rgba(255,255,255,0.05)',
                  borderRadius: 6,
                  fontSize: 12,
                  color: 'rgba(255,255,255,0.5)',
                }}>
                  💡 <em>{mod.tip}</em>
                </div>
              </div>
            </Col>
          ))}
        </Row>
      </Card>

      {/* Scoring Dimensions */}
      <Card style={{
        borderRadius: 16,
        marginBottom: 24,
        border: '1px solid rgba(156,39,176,0.2)',
        background: 'linear-gradient(135deg, #131A2D 0%, #0E1525 100%)',
      }}>
        <Title level={4} style={{ color: '#CE93D8', margin: '0 0 16px' }}>
          <AlertOutlined /> How You're Scored
        </Title>
        <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
          Your final Emotional Regulation Score is calculated from these 4 dimensions:
        </Text>
        <Row gutter={[12, 12]}>
          {scoringDimensions.map((dim, i) => (
            <Col xs={24} sm={12} key={i}>
              <div style={{
                padding: 14,
                borderRadius: 10,
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(255,255,255,0.06)',
                height: '100%',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                  {dim.icon}
                  <div>
                    <Text strong style={{ color: '#fff', fontSize: 14 }}>{dim.title}</Text>
                    <Text style={{ color: 'rgba(255,255,255,0.4)', fontSize: 11, marginLeft: 8 }}>({dim.weight})</Text>
                  </div>
                </div>
                <Text style={{ color: 'rgba(255,255,255,0.6)', fontSize: 13, lineHeight: 1.5 }}>{dim.desc}</Text>
              </div>
            </Col>
          ))}
        </Row>
      </Card>

      {/* Important Tips */}
      <Card style={{
        borderRadius: 16,
        marginBottom: 32,
        border: '1px solid rgba(255,196,0,0.2)',
        background: 'linear-gradient(135deg, rgba(255,196,0,0.05) 0%, #0E1525 100%)',
      }}>
        <Title level={4} style={{ color: '#FFC400', margin: '0 0 12px' }}>
          ⚡ Important Tips
        </Title>
        <ul style={{ color: 'rgba(255,255,255,0.8)', fontSize: 14, lineHeight: 2, paddingLeft: 20, margin: 0 }}>
          <li>Read each incident description carefully before dispatching.</li>
          <li><strong>Don't click randomly</strong> — random resource clicks without selecting an incident count as <em>panic clicks</em> and lower your score.</li>
          <li>If an equipment failure occurs, <strong>stay calm and select an alternative</strong>. Recovery time is measured.</li>
          <li>In later modules, situations can <strong>change mid-response</strong>. Watch for red alerts and adapt.</li>
          <li>The assessment runs continuously — <strong>you cannot pause or restart</strong> once you begin.</li>
        </ul>
      </Card>

      {/* Begin Button */}
      <div style={{ textAlign: 'center' }}>
        <Button
          type="primary"
          size="large"
          icon={<PlayCircleOutlined />}
          loading={startLoading}
          onClick={onBegin}
          style={{
            height: 56,
            fontSize: 18,
            fontWeight: 700,
            background: 'linear-gradient(135deg, #FF4D4F 0%, #FF7875 100%)',
            border: 'none',
            borderRadius: 14,
            paddingInline: 48,
            boxShadow: '0 6px 20px rgba(255, 77, 79, 0.4)',
          }}
        >
          Begin Assessment
        </Button>
        <div style={{ marginTop: 10 }}>
          <Text type="secondary" style={{ fontSize: 12 }}>
            By clicking, you acknowledge the instructions and will start Module 1.
          </Text>
        </div>
      </div>
    </div>
  );
}

// ── Main Assessment Page ──────────────────────────────────────────
export default function AssessmentPage() {
  const [sessionId, setSessionId] = useState(null);
  const [currentModule, setCurrentModule] = useState(0); // 0 = loading
  const [loading, setLoading] = useState(false); // for the Begin button
  const [completing, setCompleting] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [showGuidelines, setShowGuidelines] = useState(true); // show instructions first
  const navigate = useNavigate();

  useEffect(() => {
    if (completed) {
      navigate('/results');
    }
  }, [completed, navigate]);

  const startOrResume = async () => {
    setLoading(true);
    try {
      const res = await assessmentService.start();
      const { session, currentModule: mod, resumed } = res.data.data;
      setSessionId(session._id);
      setCurrentModule(mod || 1);
      setShowGuidelines(false); // hide guidelines, show the game

      // If resuming an existing session, skip guidelines
      if (resumed) {
        message.info('Resuming your in-progress assessment...');
      }
    } catch (error) {
      message.error('Failed to start assessment');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogEvent = useCallback(async (eventData) => {
    try {
      await assessmentService.logEvent(eventData);
    } catch (error) {
      console.error('Failed to log event:', error);
    }
  }, []);

  const handleModuleComplete = useCallback(async (moduleNum) => {
    if (moduleNum < 4) {
      // Transition to next module with a brief pause
      message.success(`Module ${moduleNum} completed! Moving to Module ${moduleNum + 1}...`);
      setTimeout(() => {
        setCurrentModule(moduleNum + 1);
      }, 2000);
    } else {
      // All modules complete — calculate score
      setCompleting(true);
      try {
        await assessmentService.complete({ sessionId });
        setCompleted(true);
        message.success('Assessment completed! 🎉');
      } catch (error) {
        message.error('Failed to complete assessment');
        console.error(error);
      } finally {
        setCompleting(false);
      }
    }
  }, [sessionId]);

  // Show Guidelines screen first
  if (showGuidelines) {
    return <AssessmentGuidelines onBegin={startOrResume} loading={loading} />;
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 80 }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>
          <Text type="secondary">Preparing assessment...</Text>
        </div>
      </div>
    );
  }

  if (completing) {
    return (
      <div style={{ textAlign: 'center', padding: 80 }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>
          <Text type="secondary">Calculating your emotional regulation score...</Text>
        </div>
      </div>
    );
  }

  const moduleInfo = MODULE_INFO[currentModule];

  return (
    <div className="simulation-container">
      {/* Module Progress */}
      <div className="module-progress">
        {[1, 2, 3, 4].map((m, i) => (
          <div key={m} style={{ display: 'flex', alignItems: 'center', flex: i < 3 ? 1 : 'unset', gap: 8 }}>
            <div className={`module-step ${m === currentModule ? 'active' : m < currentModule ? 'completed' : 'pending'}`}>
              {m < currentModule ? <CheckCircleOutlined /> : m}
            </div>
            {i < 3 && <div className={`module-connector ${m < currentModule ? 'completed' : ''}`} />}
          </div>
        ))}
      </div>

      {/* Module Header */}
      <Card style={{
        marginBottom: 20,
        borderRadius: 12,
        background: `linear-gradient(135deg, ${moduleInfo.color}15 0%, ${moduleInfo.color}08 100%)`,
        borderLeft: `4px solid ${moduleInfo.color}`,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontSize: 32 }}>{moduleInfo.icon}</span>
          <div>
            <Title level={4} style={{ margin: 0, color: moduleInfo.color }}>
              Module {currentModule}: {moduleInfo.title}
            </Title>
            <Text type="secondary">{moduleInfo.description}</Text>
          </div>
        </div>
      </Card>

      {/* Module Content */}
      {currentModule > 0 && currentModule <= 4 && (
        <CommandCenter
          sessionId={sessionId}
          currentLevel={currentModule}
          onLogEvent={handleLogEvent}
          onLevelComplete={handleModuleComplete}
        />
      )}
    </div>
  );
}
