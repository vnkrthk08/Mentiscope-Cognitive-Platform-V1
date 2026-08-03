import { Card, Tag, Typography } from 'antd';
import { PRIORITIES } from '../scenarios/scenarioData';

const { Text, Paragraph } = Typography;

/**
 * ScenarioCard — Emergency scenario display card
 */
export default function ScenarioCard({ scenario, index, alerts = [] }) {
  const priority = PRIORITIES[scenario.priority] || PRIORITIES.medium;

  return (
    <Card
      className="animate-fade-in-up"
      style={{
        marginBottom: 16,
        borderRadius: 12,
        border: scenario.priority === 'critical'
          ? '2px solid #DC3545'
          : '1px solid #e8e8e8',
        boxShadow: scenario.priority === 'critical'
          ? '0 0 12px rgba(220, 53, 69, 0.15)'
          : '0 2px 8px rgba(0, 0, 0, 0.06)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
        <div>
          <Text strong style={{ fontSize: 18 }}>
            {scenario.title}
          </Text>
          {index !== undefined && (
            <Text type="secondary" style={{ marginLeft: 8, fontSize: 12 }}>
              Scenario {index + 1}
            </Text>
          )}
        </div>
        <Tag color={priority.color} className={scenario.priority === 'critical' ? 'animate-pulse' : ''}>
          {priority.label} Priority
        </Tag>
      </div>

      <Paragraph style={{ color: '#555', fontSize: 14, marginBottom: 12 }}>
        {scenario.description}
      </Paragraph>

      {/* Alerts (misinformation, failures, dynamic events) */}
      {alerts.map((alert, i) => (
        <div key={i} className={`scenario-alert ${alert.type}`}>
          <Text style={{ fontSize: 13 }}>{alert.message}</Text>
        </div>
      ))}
    </Card>
  );
}
