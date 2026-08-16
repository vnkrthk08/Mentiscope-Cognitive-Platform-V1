import React from 'react';
import { Card, Typography, Progress, Badge, Tag } from 'antd';
import { ClockCircleOutlined, WarningOutlined } from '@ant-design/icons';

const { Text } = Typography;

export default function IncidentFeed({ incidents, selectedId, onSelect }) {
  const activeIncidents = incidents.filter(i => i.status === 'active' || i.status === 'dispatching');

  if (activeIncidents.length === 0) {
    return (
      <div className="incident-feed empty">
        <Text type="secondary">No active emergencies</Text>
      </div>
    );
  }

  return (
    <div className="incident-feed">
      {activeIncidents.map(inc => {
        const isActive = inc.status === 'active';
        const isDispatching = inc.status === 'dispatching';
        const progressPercent = (inc.timeLeft / inc.timeLimit) * 100;
        let progressColor = '#00E676'; // green
        if (progressPercent < 50) progressColor = '#FFC400'; // yellow
        if (progressPercent < 20) progressColor = '#FF1744'; // red

        return (
          <Card 
            key={inc.id}
            className={`incident-card priority-${inc.priority} ${selectedId === inc.id ? 'selected' : ''}`}
            onClick={() => isActive && onSelect(inc.id)}
            style={{ opacity: isActive || isDispatching ? 1 : 0.5 }}
          >
            <div className="incident-header">
              <Text strong className="incident-title">{inc.title}</Text>
              {isActive && (
                <Tag color={inc.timeLeft < 10 ? 'red' : 'orange'} className="timer-tag">
                  <ClockCircleOutlined /> {inc.timeLeft}s
                </Tag>
              )}
              {isDispatching && (
                <Tag color="cyan" className="timer-tag">
                  <ClockCircleOutlined /> ETA: {inc.eta}s
                </Tag>
              )}
            </div>
            
            {isActive && (
              <Progress 
                percent={progressPercent} 
                showInfo={false} 
                strokeColor={progressColor} 
                trailColor="rgba(255,255,255,0.1)"
                size="small"
                className="incident-progress"
              />
            )}

            <div className="incident-needs">
              <Text type="secondary" style={{ fontSize: 11, display: 'block', marginBottom: 4 }}>REQUIRED:</Text>
              <div className="tags-container">
                {inc.requiredResources.map((res, idx) => {
                  const isMet = inc.dispatched.includes(res);
                  return (
                    <Tag key={idx} color={isMet ? 'success' : 'default'} className={isMet ? 'met-tag' : 'unmet-tag'}>
                      {res}
                    </Tag>
                  );
                })}
              </div>
            </div>
            
            {inc.dispatched.length > 0 && (
              <div className="incident-dispatched">
                <Text type="secondary" style={{ fontSize: 11 }}>ON SCENE: {inc.dispatched.join(', ')}</Text>
              </div>
            )}
          </Card>
        );
      })}
    </div>
  );
}
