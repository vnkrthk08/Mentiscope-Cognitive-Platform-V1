import { useState, useRef, useCallback, useEffect } from 'react';
import { Button, message, Badge } from 'antd';
import { SendOutlined, WarningOutlined } from '@ant-design/icons';
import ScenarioCard from '../components/ScenarioCard';
import ResourcePanel from '../components/ResourcePanel';
import TimerBar from '../components/TimerBar';
import { MODULE_2_SCENARIOS } from '../scenarios/scenarioData';

const PANIC_THRESHOLD_MS = 500; // Clicks within 500ms = panic

/**
 * Module 2 — Stress Induction
 * Multiple simultaneous emergencies, shorter timers, resource limits, misinformation.
 */
export default function Module2Stress({ sessionId, onLogEvent, onModuleComplete }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedResources, setSelectedResources] = useState([]);
  const [submitted, setSubmitted] = useState(false);
  const [panicCount, setPanicCount] = useState(0);
  const [clickTimestamps, setClickTimestamps] = useState([]);
  const scenarioLoadTime = useRef(Date.now());
  const scenarios = MODULE_2_SCENARIOS;

  // Track rapid clicking for panic detection
  const detectPanicClick = useCallback((timestamp) => {
    setClickTimestamps((prev) => {
      const recent = [...prev, timestamp].filter(t => timestamp - t < 2000);
      const rapidClicks = recent.filter((t, i) =>
        i > 0 && t - recent[i - 1] < PANIC_THRESHOLD_MS
      ).length;

      if (rapidClicks >= 2) {
        setPanicCount((p) => p + 1);
        onLogEvent({
          sessionId,
          module: 2,
          scenarioId: scenarios[currentIndex]?.id,
          eventType: 'PANIC_CLICK',
          panicClicks: 1,
        });
      }
      return recent;
    });
  }, [currentIndex, onLogEvent, sessionId, scenarios]);

  const handleToggleResource = useCallback((resource) => {
    detectPanicClick(Date.now());
    setSelectedResources((prev) =>
      prev.includes(resource)
        ? prev.filter((r) => r !== resource)
        : [...prev, resource]
    );
  }, [detectPanicClick]);

  const getUnavailableResources = (scenario) => {
    if (scenario.resourceLimitation) {
      // Randomly make a resource appear delayed/limited
      if (scenario.id === 'm2_s4') return ['Police Unit'];
    }
    return [];
  };

  const handleSubmit = async () => {
    if (selectedResources.length === 0) {
      message.warning('Select resources NOW!');
      return;
    }

    const scenario = scenarios[currentIndex];
    const reactionTime = Date.now() - scenarioLoadTime.current;
    const availableRequired = scenario.requiredResources.filter(
      r => !getUnavailableResources(scenario).includes(r)
    );
    const isCorrect = availableRequired.every(r => selectedResources.includes(r)) &&
      selectedResources.every(r => scenario.requiredResources.includes(r));

    await onLogEvent({
      sessionId,
      module: 2,
      scenarioId: scenario.id,
      eventType: isCorrect ? 'CORRECT_DECISION' : 'WRONG_DECISION',
      reactionTime,
      selectedResource: selectedResources.join(', '),
      correctDecision: isCorrect,
      panicClicks: panicCount,
    });

    setSubmitted(true);

    if (isCorrect) {
      message.success('Resources dispatched! ✅');
    } else {
      message.error(`Suboptimal dispatch. Needed: ${scenario.requiredResources.join(', ')}`);
    }

    setTimeout(() => {
      if (currentIndex < scenarios.length - 1) {
        setCurrentIndex((prev) => prev + 1);
        setSelectedResources([]);
        setSubmitted(false);
        setPanicCount(0);
        setClickTimestamps([]);
        scenarioLoadTime.current = Date.now();
      } else {
        onLogEvent({ sessionId, module: 2, eventType: 'MODULE_COMPLETED' });
        onModuleComplete(2);
      }
    }, 1200);
  };

  const handleTimeout = async () => {
    const scenario = scenarios[currentIndex];
    await onLogEvent({
      sessionId,
      module: 2,
      scenarioId: scenario.id,
      eventType: 'TIMEOUT',
      reactionTime: scenario.timeLimit * 1000,
      panicClicks: panicCount,
    });

    message.error('⏰ TIME OUT! Emergency not handled!');
    setTimeout(() => {
      if (currentIndex < scenarios.length - 1) {
        setCurrentIndex((prev) => prev + 1);
        setSelectedResources([]);
        setSubmitted(false);
        setPanicCount(0);
        setClickTimestamps([]);
        scenarioLoadTime.current = Date.now();
      } else {
        onLogEvent({ sessionId, module: 2, eventType: 'MODULE_COMPLETED' });
        onModuleComplete(2);
      }
    }, 800);
  };

  const scenario = scenarios[currentIndex];
  const alerts = [];
  if (scenario.misinformation) {
    alerts.push({ type: 'misinformation', message: scenario.misinformation });
  }
  if (scenario.resourceLimitation) {
    alerts.push({ type: 'resource-limit', message: scenario.resourceLimitation });
  }

  return (
    <div className="animate-fade-in">
      <div style={{
        background: '#FFEBEE',
        padding: '12px 16px',
        borderRadius: 8,
        marginBottom: 16,
        fontSize: 13,
        color: '#C62828',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <span>
          ⚡ <strong>Module 2 — Stress Test:</strong> Multiple emergencies! Act fast under pressure.
        </span>
        <span>{currentIndex + 1} / {scenarios.length}</span>
      </div>

      {panicCount > 0 && (
        <div style={{
          background: '#FFF3E0',
          padding: '6px 12px',
          borderRadius: 6,
          marginBottom: 8,
          fontSize: 12,
          display: 'flex',
          alignItems: 'center',
          gap: 6,
        }}>
          <WarningOutlined style={{ color: '#FF9800' }} />
          <span>Rapid clicking detected ({panicCount}x) — Stay calm</span>
        </div>
      )}

      <TimerBar
        key={scenario.id}
        duration={scenario.timeLimit}
        onTimeout={handleTimeout}
        paused={submitted}
      />

      <ScenarioCard scenario={scenario} index={currentIndex} alerts={alerts} />

      <ResourcePanel
        selectedResources={selectedResources}
        onToggle={handleToggleResource}
        unavailableResources={getUnavailableResources(scenario)}
        disabled={submitted}
      />

      <Button
        type="primary"
        size="large"
        icon={<SendOutlined />}
        onClick={handleSubmit}
        disabled={submitted || selectedResources.length === 0}
        block
        danger
        style={{
          height: 48,
          fontSize: 16,
          fontWeight: 600,
          borderRadius: 10,
          border: 'none',
        }}
      >
        {submitted ? 'Dispatching...' : '🚨 DISPATCH NOW'}
      </Button>
    </div>
  );
}
