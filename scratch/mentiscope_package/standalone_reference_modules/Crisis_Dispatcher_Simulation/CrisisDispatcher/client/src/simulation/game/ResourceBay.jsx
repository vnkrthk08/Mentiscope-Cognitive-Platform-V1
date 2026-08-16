import React from 'react';
import { Button, Typography } from 'antd';
import { 
  CarOutlined, 
  FireOutlined, 
  SafetyCertificateOutlined, 
  MedicineBoxOutlined 
} from '@ant-design/icons';

const { Text } = Typography;

const getResourceIcon = (resource) => {
  switch (resource) {
    case 'Ambulance': return <MedicineBoxOutlined />;
    case 'Fire Truck': return <FireOutlined />;
    case 'Police Unit': return <SafetyCertificateOutlined />;
    case 'Rescue Team': return <CarOutlined />;
    default: return <CarOutlined />;
  }
};

const getResourceColor = (resource) => {
  switch (resource) {
    case 'Ambulance': return '#00E676';
    case 'Fire Truck': return '#FF4D4F';
    case 'Police Unit': return '#00B0FF';
    case 'Rescue Team': return '#FFC400';
    default: return '#FFF';
  }
};

export default function ResourceBay({ available, onDispatch, hasSelection }) {
  // Group resources for display if there are duplicates (Level 2 might have duplicates)
  const resourceCounts = available.reduce((acc, curr) => {
    acc[curr] = (acc[curr] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="resource-bay">
      <div className="bay-header">
        <Text strong style={{ color: '#8A99AF' }}>GLOBAL RESOURCE POOL</Text>
        {!hasSelection && (
          <Text type="secondary" style={{ fontSize: 12, marginLeft: 16, color: '#FF4D4F' }}>
            *Select an incident card first to dispatch
          </Text>
        )}
      </div>
      <div className="bay-units">
        {Object.entries(resourceCounts).map(([res, count], idx) => {
          const color = getResourceColor(res);
          return (
            <Button
              key={`${res}-${idx}`}
              className="resource-btn"
              onClick={() => onDispatch(res)}
              disabled={!hasSelection || count === 0}
              style={{
                borderColor: color,
                color: color,
              }}
            >
              <div className="resource-icon">{getResourceIcon(res)}</div>
              <div className="resource-name">{res}</div>
              <div className="resource-count">x{count}</div>
            </Button>
          );
        })}
        {available.length === 0 && (
          <Text type="secondary" style={{ padding: 20 }}>ALL UNITS DEPLOYED</Text>
        )}
      </div>
    </div>
  );
}
