import React, { useMemo } from 'react';

export default function RadarMap({ incidents }) {
  // Deterministic positions based on ID so they don't jump on re-renders
  const getPosition = (id) => {
    let hash = 0;
    for (let i = 0; i < id.length; i++) {
      hash = id.charCodeAt(i) + ((hash << 5) - hash);
    }
    const x = Math.abs(hash % 80) + 10; // 10% to 90%
    const y = Math.abs((hash * 13) % 80) + 10;
    return { left: `${x}%`, top: `${y}%` };
  };

  const activeIncidents = incidents.filter(i => i.status === 'active');

  return (
    <div className="radar-map-container">
      <div className="radar-grid"></div>
      <div className="radar-sweep"></div>
      
      {activeIncidents.map(inc => {
        const pos = getPosition(inc.id);
        const isCritical = inc.priority === 'critical' || inc.dynamicEventTriggered;
        
        return (
          <div 
            key={inc.id}
            className={`radar-blip ${isCritical ? 'critical' : ''}`}
            style={pos}
          >
            <div className="blip-ping"></div>
            <div className="blip-label">{inc.priority.toUpperCase()}</div>
          </div>
        );
      })}
    </div>
  );
}
