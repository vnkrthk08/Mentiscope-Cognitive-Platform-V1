import { useState, useRef, useCallback, useEffect } from 'react';
import { Button, message } from 'antd';
import { SendOutlined, ThunderboltOutlined } from '@ant-design/icons';
import ScenarioCard from '../components/ScenarioCard';
import ResourcePanel from '../components/ResourcePanel';
import TimerBar from '../components/TimerBar';
import { MODULE_4_SCENARIOS } from '../scenarios/scenarioData';

/**
 * Module 4 — Adaptive Challenge
 * Dynamic emergencies, changing priorities, unexpected events.
 * Measures strategy changes, decision stability, and adaptation rate.
 */
export default function Module4Adaptive({ sessionId, onLogEvent, onModuleComplete }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedResources, setSelectedResources] = useState([]);
  const [submitted, setSubmitted] = useState(false);
  const [dynamicEventShown, setDynamicEventShown] = useState(false);
  const [previousSelection, setPreviousSelection] = useState([]);
  const [strategyChanged, setStrategyChanged] = useState(false);
  const scenarioLoadTime = useRef(Date.now());
  const dynamicEventTimer = useRef(null);
  const scenarios = MODULE_4_SCENARIOS;

  // Show dynamic event partway through
  useEffect(() => {
    const scenario = scenarios[currentIndex];
    if (scenario?.dynamicEvent && !dynamicEventShown && !submitted) {
      dynamicEventTimer.current = setTimeout(() => {
        setDynamicEventShown(true);
        setPreviousSelection([...selectedResources]);

        onLogEvent({
          sessionId,
          module: 4,
          scenarioId: scenario.id,
          eventType: 'SCENARIO_LOADED',
          strategyChange: false,
        });

        message.warning('🔴 Situation has changed! Reassess your resources.');
      }, (scenario.timeLimit * 1000) / 3); // Trigger at 1/3 of time
    }

    return () => clearTimeout(dynamicEventTimer.current);
  }, [currentIndex, dynamicEventShown, submitted]);

  const handleToggleResource = useCallback((resource) => {
    setSelectedResources((prev) => {
      const next = prev.includes(resource)
        ? prev.filter((r) => r !== resource)
        : [...prev, resource];

      // Detect strategy change after dynamic event
      if (dynamicEventShown && previousSelection.length > 0) {
        const changed = JSON.stringify([...next].sort()) !== JSON.stringify([...previousSelection].sort());
        if (changed && !strategyChanged) {
          setStrategyChanged(true);
          onLogEvent({
            sessionId,
            module: 4,
            scenarioId: scenarios[currentIndex]?.id,
            eventType: 'RESOURCE_CHANGED',
            strategyChange: true,
          });
        }
      }

      return next;
    });
  }, [dynamicEventShown, previousSelection, strategyChanged, currentIndex, onLogEvent, sessionId, scenarios]);

  const handleSubmit = async () => {
    if (selectedResources.length === 0) {
      message.warning('Select resources to dispatch');
      return;
    }

    const scenario = scenarios[currentIndex];
    const reactionTime = Date.now() - scenarioLoadTime.current;

    // Check against current requirements (may have changed due to dynamic event)
    const currentRequired = dynamicEventShown && scenario.dynamicEvent
      ? scenario.dynamicEvent.newRequiredResources
      : scenario.requiredResources;

    const isCorrect = currentRequired.every(r => selectedResources.includes(r)) &&
      selectedResources.every(r => currentRequired.includes(r));

    // Calculate adaptation rate
    const adapted = dynamicEventShown && strategyChanged && isCorrect;
    const adaptationRate = dynamicEventShown ? (adapted ? 1 : strategyChanged ? 0.5 : 0) : null;

    // Decision stability: 1 if consistent with needs, lower if erratic
    const decisionStability = isCorrect ? 1 : strategyChanged ? 0.6 : 0.3;

    await onLogEvent({
      sessionId,
      module: 4,
      scenarioId: scenario.id,
      eventType: isCorrect ? 'CORRECT_DECISION' : 'WRONG_DECISION',
      reactionTime,
      selectedResource: selectedResources.join(', '),
      correctDecision: isCorrect,
      strategyChange: strategyChanged,
      adaptationRate,
      decisionStability,
    });

    setSubmitted(true);

    if (isCorrect) {
      message.success(adapted ? 'Excellent adaptation! ✅' : 'Correct dispatch! ✅');
    } else {
      message.error(`Required: ${currentRequired.join(', ')}`);
    }

    setTimeout(() => {
      if (currentIndex < scenarios.length - 1) {
        setCurrentIndex((prev) => prev + 1);
        setSelectedResources([]);
        setSubmitted(false);
        setDynamicEventShown(false);
        setPreviousSelection([]);
        setStrategyChanged(false);
        scenarioLoadTime.current = Date.now();
      } else {
        onLogEvent({ sessionId, module: 4, eventType: 'MODULE_COMPLETED' });
        onModuleComplete(4);
      }
    }, 1500);
  };

  const handleTimeout = async () => {
    const scenario = scenarios[currentIndex];
    await onLogEvent({
      sessionId,
      module: 4,
      scenarioId: scenario.id,
      eventType: 'TIMEOUT',
      reactionTime: scenario.timeLimit * 1000,
      strategyChange: strategyChanged,
      adaptationRate: 0,
    });

    message.error('⏰ Failed to adapt in time!');
    setTimeout(() => {
      if (currentIndex < scenarios.length - 1) {
        setCurrentIndex((prev) => prev + 1);
        setSelectedResources([]);
        setSubmitted(false);
        setDynamicEventShown(false);
        setPreviousSelection([]);
        setStrategyChanged(false);
        scenarioLoadTime.current = Date.now();
      } else {
        onLogEvent({ sessionId, module: 4, eventType: 'MODULE_COMPLETED' });
        onModuleComplete(4);
      }
    }, 800);
  };

  const scenario = scenarios[currentIndex];
  const alerts = [];
  if (dynamicEventShown && scenario.dynamicEvent) {
    alerts.push({ type: 'dynamic', message: scenario.dynamicEvent.message });
  }

  return (
    <div className="animate-fade-in">
      <div style={{
        background: '#E0F7FA',
        padding: '12px 16px',
        borderRadius: 8,
        marginBottom: 16,
        fontSize: 13,
        color: '#00695C',
        display: 'flex',
        justifyContent: 'space-between',
      }}>
        <span>
          🎯 <strong>Module 4 — Adaptive:</strong> Situations evolve dynamically. Adapt your strategy.
        </span>
        <span>{currentIndex + 1} / {scenarios.length}</span>
      </div>

      {strategyChanged && (
        <div style={{
          background: '#E8F5E9',
          padding: '6px 12px',
          borderRadius: 6,
          marginBottom: 8,
          fontSize: 12,
          color: '#2E7D32',
        }}>
          <ThunderboltOutlined /> Strategy change detected — Adapting to new situation
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
        disabled={submitted}
      />

      <Button
        type="primary"
        size="large"
        icon={<SendOutlined />}
        onClick={handleSubmit}
        disabled={submitted || selectedResources.length === 0}
        block
        style={{
          height: 48,
          fontSize: 16,
          fontWeight: 600,
          borderRadius: 10,
          background: submitted ? '#ccc' : 'linear-gradient(135deg, #17A2B8 0%, #20C997 100%)',
          border: 'none',
        }}
      >
        {submitted ? 'Processing...' : dynamicEventShown ? '🎯 Dispatch (Adapted)' : 'Dispatch Resources'}
      </Button>
    </div>
  );
}
