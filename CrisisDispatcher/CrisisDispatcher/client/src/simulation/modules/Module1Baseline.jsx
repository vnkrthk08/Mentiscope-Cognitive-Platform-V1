import { useState, useRef, useCallback } from 'react';
import { Button, message } from 'antd';
import { SendOutlined } from '@ant-design/icons';
import ScenarioCard from '../components/ScenarioCard';
import ResourcePanel from '../components/ResourcePanel';
import TimerBar from '../components/TimerBar';
import { MODULE_1_SCENARIOS, ALL_RESOURCES } from '../scenarios/scenarioData';

/**
 * Module 1 — Baseline Assessment
 * Simple scenarios, one at a time, generous time limits.
 * Measures normal decision-making under low stress.
 */
export default function Module1Baseline({ sessionId, onLogEvent, onModuleComplete }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedResources, setSelectedResources] = useState([]);
  const [submitted, setSubmitted] = useState(false);
  const scenarioLoadTime = useRef(Date.now());
  const scenarios = MODULE_1_SCENARIOS;

  const handleToggleResource = useCallback((resource) => {
    setSelectedResources((prev) =>
      prev.includes(resource)
        ? prev.filter((r) => r !== resource)
        : [...prev, resource]
    );
  }, []);

  const handleSubmit = async () => {
    if (selectedResources.length === 0) {
      message.warning('Please select at least one resource');
      return;
    }

    const scenario = scenarios[currentIndex];
    const reactionTime = Date.now() - scenarioLoadTime.current;
    const isCorrect = scenario.requiredResources.every(r => selectedResources.includes(r)) &&
      selectedResources.length === scenario.requiredResources.length;

    // Log decision event
    await onLogEvent({
      sessionId,
      module: 1,
      scenarioId: scenario.id,
      eventType: isCorrect ? 'CORRECT_DECISION' : 'WRONG_DECISION',
      reactionTime,
      selectedResource: selectedResources.join(', '),
      correctDecision: isCorrect,
      decisionStability: 1, // Baseline — no pressure
    });

    setSubmitted(true);

    if (isCorrect) {
      message.success('Correct dispatch! ✅');
    } else {
      message.error(`Incorrect. Required: ${scenario.requiredResources.join(', ')}`);
    }

    // Move to next scenario after brief delay
    setTimeout(() => {
      if (currentIndex < scenarios.length - 1) {
        setCurrentIndex((prev) => prev + 1);
        setSelectedResources([]);
        setSubmitted(false);
        scenarioLoadTime.current = Date.now();

        // Log next scenario loaded
        onLogEvent({
          sessionId,
          module: 1,
          scenarioId: scenarios[currentIndex + 1].id,
          eventType: 'SCENARIO_LOADED',
        });
      } else {
        // Module complete
        onLogEvent({
          sessionId,
          module: 1,
          eventType: 'MODULE_COMPLETED',
        });
        onModuleComplete(1);
      }
    }, 1500);
  };

  const handleTimeout = async () => {
    const scenario = scenarios[currentIndex];
    await onLogEvent({
      sessionId,
      module: 1,
      scenarioId: scenario.id,
      eventType: 'TIMEOUT',
      reactionTime: scenario.timeLimit * 1000,
    });

    message.error('⏰ Time\'s up! Moving to next scenario.');
    setTimeout(() => {
      if (currentIndex < scenarios.length - 1) {
        setCurrentIndex((prev) => prev + 1);
        setSelectedResources([]);
        setSubmitted(false);
        scenarioLoadTime.current = Date.now();
      } else {
        onLogEvent({ sessionId, module: 1, eventType: 'MODULE_COMPLETED' });
        onModuleComplete(1);
      }
    }, 1000);
  };

  const scenario = scenarios[currentIndex];

  return (
    <div className="animate-fade-in">
      <div style={{
        background: '#E8F5E9',
        padding: '12px 16px',
        borderRadius: 8,
        marginBottom: 16,
        fontSize: 13,
        color: '#2E7D32',
      }}>
        📋 <strong>Module 1 — Baseline:</strong> Dispatch the correct resources for each emergency.
        Take your time and make thoughtful decisions.
        <span style={{ float: 'right' }}>{currentIndex + 1} / {scenarios.length}</span>
      </div>

      <TimerBar
        key={scenario.id}
        duration={scenario.timeLimit}
        onTimeout={handleTimeout}
        paused={submitted}
      />

      <ScenarioCard scenario={scenario} index={currentIndex} />

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
          background: submitted ? '#ccc' : 'linear-gradient(135deg, #1B3A5C 0%, #2D5F8A 100%)',
          border: 'none',
        }}
      >
        {submitted ? 'Processing...' : 'Dispatch Resources'}
      </Button>
    </div>
  );
}
