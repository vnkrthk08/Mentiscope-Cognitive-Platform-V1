import React from 'react';
import { Typography, Row, Col } from 'antd';
import { 
  AimOutlined, 
  SafetyCertificateOutlined, 
  WarningOutlined,
  CheckCircleOutlined,
  AppstoreOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;

export default function HUD({ level, notifications, gameStats, timeRemaining }) {
  // gameStats = { incidentsResolved, livesSaved, livesLost, activeIncidents, resourcesRemaining }
  const stats = gameStats || {
    incidentsResolved: 0,
    livesSaved: 0,
    livesLost: 0,
    activeIncidents: 0,
    resourcesRemaining: 0,
  };

  return (
    <div className="game-hud" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div className="hud-stats" style={{ display: 'flex', width: '100%', gap: '16px', overflowX: 'auto', paddingBottom: '4px' }}>
        <div className="stat-box level-box" style={{ flex: 1, minWidth: 'fit-content' }}>
          <AimOutlined style={{ fontSize: 24 }} />
          <div>
            <Text type="secondary" style={{ color: '#8A99AF', fontSize: 10, whiteSpace: 'nowrap' }}>MODULE</Text>
            <Title level={4} style={{ margin: 0, color: '#FF4D4F' }}>0{level}</Title>
          </div>
        </div>
        <div className="stat-box" style={{ flex: 1, minWidth: 'fit-content' }}>
          <WarningOutlined style={{ fontSize: 24, color: '#FF9800' }} />
          <div>
            <Text type="secondary" style={{ color: '#8A99AF', fontSize: 10, whiteSpace: 'nowrap' }}>INCIDENTS</Text>
            <Title level={4} style={{ margin: 0, color: '#FF9800' }}>{stats.activeIncidents}</Title>
          </div>
        </div>
        <div className="stat-box" style={{ flex: 1, minWidth: 'fit-content' }}>
          <AppstoreOutlined style={{ fontSize: 24, color: '#03A9F4' }} />
          <div>
            <Text type="secondary" style={{ color: '#8A99AF', fontSize: 10, whiteSpace: 'nowrap' }}>RESOURCES</Text>
            <Title level={4} style={{ margin: 0, color: '#03A9F4' }}>{stats.resourcesRemaining}</Title>
          </div>
        </div>
        <div className="stat-box" style={{ flex: 1, minWidth: 'fit-content' }}>
          <CheckCircleOutlined style={{ fontSize: 24, color: '#4CAF50' }} />
          <div>
            <Text type="secondary" style={{ color: '#8A99AF', fontSize: 10, whiteSpace: 'nowrap' }}>RESOLVED</Text>
            <Title level={4} style={{ margin: 0, color: '#4CAF50' }}>{stats.incidentsResolved}</Title>
          </div>
        </div>
        <div className="stat-box" style={{ flex: 1, minWidth: 'fit-content' }}>
          <SafetyCertificateOutlined style={{ fontSize: 24, color: '#00E676' }} />
          <div>
            <Text type="secondary" style={{ color: '#8A99AF', fontSize: 10, whiteSpace: 'nowrap' }}>LIVES SAVED</Text>
            <Title level={4} style={{ margin: 0, color: '#00E676' }}>{stats.livesSaved}</Title>
          </div>
        </div>
        <div className="stat-box" style={{ flex: 1, minWidth: 'fit-content' }}>
          <WarningOutlined style={{ fontSize: 24, color: '#F44336' }} />
          <div>
            <Text type="secondary" style={{ color: '#8A99AF', fontSize: 10, whiteSpace: 'nowrap' }}>LIVES LOST</Text>
            <Title level={4} style={{ margin: 0, color: '#F44336' }}>{stats.livesLost}</Title>
          </div>
        </div>
      </div>
      
      <div className="hud-ticker">
        <div className="ticker-label">LIVE FEED</div>
        <div className="ticker-content" style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
          <span>{notifications[0] || 'Awaiting dispatch instructions...'}</span>
          {timeRemaining !== undefined && (
            <span style={{ color: '#FFC400', fontWeight: 'bold' }}>
              <ClockCircleOutlined style={{ marginRight: 8 }} />
              Module Time: {timeRemaining}s
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
