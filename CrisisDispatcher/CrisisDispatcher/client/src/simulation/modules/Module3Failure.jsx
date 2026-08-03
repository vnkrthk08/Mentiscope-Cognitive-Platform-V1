import { useState, useRef, useCallback } from 'react';
import { Button, message } from 'antd';
import { SendOutlined, ReloadOutlined } from '@ant-design/icons';
import ScenarioCard from '../components/ScenarioCard';
import ResourcePanel from '../components/ResourcePanel';
import TimerBar from '../components/TimerBar';
import { MODULE_3_SCENARIOS } from '../scenarios/scenarioData';

/**
 * Module 3 — Failure & Recovery
 * Forced wrong outcomes, equipment failures, ambulance shortages, time penalties.
 * Measures recovery latency, persistence, and retry attempts.
 */
export default function Module3Failure({ sessionId, onLogEvent, onModuleComplete }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedResources, setSelectedResources] = useState([]);
  const [submitted, setSubmitted] = useState(false);
  const [failureShown, setFailureShown] = useState(false);
  const [retryMode, setRetryMode] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const scenarioLoadTime = useRef(Date.now());
  const failureTime = useRef(null);
  const scenarios = MODULE_3_SCENARIOS;

  const handleToggleResource = useCallback((resource) => {
    setSelectedResources((prev) =>
      prev.includes(resource)
        ? prev.filter((r) => r !== resource)
        : [...prev, resource]
    );
  }, []);

  const handleSubmit = async () => {
    if (selectedResources.length === 0) {
      message.warning('Select resources to dispatch');
      return;
    }

    const scenario = scenarios[currentIndex];
    const reactionTime = Date.now() - scenarioLoadTime.current;

    // First attempt always triggers forced failure
    if (!failureShown && scenario.forcedFailure) {
      setFailureShown(true);
      failureTime.current = Date.now();
      setSubmitted(false);
      setSelectedResources([]);

      await onLogEvent({
        sessionId,
        module: 3,
        scenarioId: scenario.id,
        eventType: 'WRONG_DECISION',
        reactionTime,
        selectedResource: selectedResources.join(', '),
        correctDecision: false,
      });

      message.error('❌ Dispatch failed! See alert below.');
      return;
    }

    // Retry attempt
    const recoveryLatency = failureTime.current ? Date.now() - failureTime.current : 0;
    const isCorrect = scenario.requiredResources.every(r => selectedResources.includes(r)) &&
      selectedResources.every(r => scenario.requiredResources.includes(r));

    await onLogEvent({
      sessionId,
      module: 3,
      scenarioId: scenario.id,
      eventType: isCorrect ? 'CORRECT_DECISION' : 'WRONG_DECISION',
      reactionTime: Date.now() - scenarioLoadTime.current,
      selectedResource: selectedResources.join(', '),
      correctDecision: isCorrect,
      retryCount: retryCount + 1,
      recoveryLatency,
    });

    setSubmitted(true);

    if (isCorrect) {
      message.success('Recovery successful! ✅');
    } else {
      if (scenario.retryAllowed && retryCount < 2) {
        message.warning('Still incorrect. Try again!');
        setRetryCount((p) => p + 1);
        setSubmitted(false);
        setSelectedResources([]);
        return;
      }
      message.error(`Required: ${scenario.requiredResources.join(', ')}`);
    }

    // Advance to next scenario
    setTimeout(() => {
      if (currentIndex < scenarios.length - 1) {
        setCurrentIndex((prev) => prev + 1);
        setSelectedResources([]);
        setSubmitted(false);
        setFailureShown(false);
        setRetryMode(false);
        setRetryCount(0);
        scenarioLoadTime.current = Date.now();
        failureTime.current = null;
      } else {
        onLogEvent({ sessionId, module: 3, eventType: 'MODULE_COMPLETED' });
        onModuleComplete(3);
      }
    }, 1500);
  };

  const handleTimeout = async () => {
    const scenario = scenarios[currentIndex];
    await onLogEvent({
      sessionId,
      module: 3,
      scenarioId: scenario.id,
      eventType: 'TIMEOUT',
      reactionTime: (scenario.timeLimit + (scenario.timePenalty || 0)) * 1000,
      retryCount,
    });

    message.error('⏰ Time expired during recovery!');
    setTimeout(() => {
      if (currentIndex < scenarios.length - 1) {
        setCurrentIndex((prev) => prev + 1);
        setSelectedResources([]);
        setSubmitted(false);
        setFailureShown(false);
        setRetryMode(false);
        setRetryCount(0);
        scenarioLoadTime.current = Date.now();
        failureTime.current = null;
      } else {
        onLogEvent({ sessionId, module: 3, eventType: 'MODULE_COMPLETED' });
        onModuleComplete(3);
      }
    }, 800);
  };

  const scenario = scenarios[currentIndex];
  const effectiveTimeLimit = scenario.timeLimit - (failureShown ? (scenario.timePenalty || 0) : 0);

  const alerts = [];
  if (failureShown && scenario.forcedFailure) {
    alerts.push({ type: 'failure', message: scenario.forcedFailure });
  }

  return (
    <div className="animate-fade-in">
      <div style={{
        background: '#FFF8E1',
        padding: '12px 16px',
        borderRadius: 8,
        marginBottom: 16,
        fontSize: 13,
        color: '#F57F17',
        display: 'flex',
        justifyContent: 'space-between',
      }}>
        <span>
          🔄 <strong>Module 3 — Recovery:</strong> Handle setbacks and equipment failures. Adapt and retry.
        </span>
        <span>{currentIndex + 1} / {scenarios.length}</span>
      </div>

      {retryCount > 0 && (
        <div style={{
          background: '#E3F2FD',
          padding: '6px 12px',
          borderRadius: 6,
          marginBottom: 8,
          fontSize: 12,
          color: '#1565C0',
        }}>
          <ReloadOutlined /> Retry attempt {retryCount + 1} — Reassess and redispatch
        </div>
      )}

      <TimerBar
        key={`${scenario.id}-${failureShown}`}
        duration={Math.max(5, effectiveTimeLimit)}
        onTimeout={handleTimeout}
        paused={submitted}
      />

      <ScenarioCard scenario={scenario} index={currentIndex} alerts={alerts} />

      <ResourcePanel
        selectedResources={selectedResources}
        onToggle={handleToggleResource}
        disabled={submitted}
      />

      <Button
        type="primary"
        size="large"
        icon={failureShown ? <ReloadOutlined /> : <SendOutlined />}
        onClick={handleSubmit}
        disabled={submitted || selectedResources.length === 0}
        block
        style={{
          height: 48,
          fontSize: 16,
          fontWeight: 600,
          borderRadius: 10,
          background: submitted ? '#ccc' : failureShown
            ? 'linear-gradient(135deg, #FFC107 0%, #FF9800 100%)'
            : 'linear-gradient(135deg, #1B3A5C 0%, #2D5F8A 100%)',
          border: 'none',
          color: failureShown ? '#000' : '#fff',
        }}
      >
        {submitted ? 'Processing...' : failureShown ? '🔄 Retry Dispatch' : 'Dispatch Resources'}
      </Button>
    </div>
  );
}
