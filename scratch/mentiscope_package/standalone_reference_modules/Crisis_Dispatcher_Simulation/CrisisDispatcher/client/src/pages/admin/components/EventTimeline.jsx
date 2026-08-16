import React, { useState, useEffect } from 'react';
import { Timeline, Spin, Typography, Card, Tag } from 'antd';
import { adminService } from '../../../api/services';
import dayjs from 'dayjs';

const { Text } = Typography;

export default function EventTimeline({ sessionId }) {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (sessionId) {
      loadEvents();
    }
  }, [sessionId]);

  const loadEvents = async () => {
    setLoading(true);
    try {
      const res = await adminService.getEvents({ sessionId });
      setEvents(res.data.data);
    } catch (error) {
      console.error('Failed to load events:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Spin style={{ display: 'block', margin: '40px auto' }} />;
  if (!events.length) return <Text type="secondary">No events logged for this session.</Text>;

  return (
    <Card title="Behavioural Timeline" bordered={false} style={{ background: '#f8f9fa' }}>
      <Timeline mode="left">
        {events.map(event => (
          <Timeline.Item 
            key={event.id}
            color={
              event.eventType === 'CORRECT_DECISION' || event.eventType === 'SCENARIO_COMPLETED' ? 'green' : 
              event.eventType === 'WRONG_DECISION' || event.eventType === 'TIMEOUT' || event.eventType === 'FAILURE_OCCURRED' ? 'red' : 
              event.eventType === 'ADAPTATION_EVENT' ? 'orange' :
              'blue'
            }
          >
            <div style={{ marginBottom: 4 }}>
              <Text strong>{dayjs(event.timestamp).format('HH:mm:ss')}</Text>
              <Tag color="blue" style={{ marginLeft: 12 }}>Module {event.module}</Tag>
              <Text type="secondary">{event.eventType}</Text>
            </div>
            
            {event.reactionTime && (
              <div style={{ fontSize: 12, color: '#666' }}>
                Reaction Time: {(event.reactionTime / 1000).toFixed(1)}s
              </div>
            )}
            {event.decisionTime && (
              <div style={{ fontSize: 12, color: '#666' }}>
                Decision Time: {(event.decisionTime / 1000).toFixed(1)}s
              </div>
            )}
            
            {event.selectedResource && (
              <div style={{ fontSize: 12, marginTop: 4 }}>
                <Text type="secondary">Selected: </Text>
                {event.selectedResource}
              </div>
            )}

            {event.dispatchedUnits && event.dispatchedUnits.length > 0 && (
              <div style={{ fontSize: 12, marginTop: 4 }}>
                <Text type="secondary">Dispatched: </Text>
                {event.dispatchedUnits.join(', ')}
              </div>
            )}
            
            {event.strategyChange && (
              <Tag color="purple" style={{ marginTop: 4, fontSize: 10 }}>Strategy Adapted</Tag>
            )}
          </Timeline.Item>
        ))}
      </Timeline>
    </Card>
  );
}
