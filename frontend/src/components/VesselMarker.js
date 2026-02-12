import React, { useMemo } from 'react';
import { Marker, Popup, Tooltip } from 'react-leaflet';
import L from 'leaflet';

// Custom vessel icon with heading indicator
const createVesselIcon = (color, isSelected, economicSignificance, heading) => {
  const size = isSelected ? 28 : 24;
  const pulseClass = economicSignificance > 80 ? 'pulse-high' : '';
  
  // Calculate rotation transform for heading
  const rotation = heading || 0;
  
  return L.divIcon({
    className: `vessel-custom-marker ${pulseClass}`,
    html: `
      <div style="
        position: relative;
        width: ${size}px;
        height: ${size}px;
      ">
        <!-- Vessel body -->
        <div style="
          position: absolute;
          width: ${size}px;
          height: ${size}px;
          background-color: ${color};
          border: 2px solid white;
          border-radius: 50%;
          box-shadow: 0 0 ${economicSignificance > 80 ? 20 : 10}px ${color};
          cursor: pointer;
          transition: all 0.2s ease;
          transform: rotate(${rotation}deg);
        ">
          <!-- Direction arrow -->
          <div style="
            position: absolute;
            top: -6px;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-bottom: 8px solid white;
          "></div>
        </div>
        ${economicSignificance > 80 ? `
        <!-- Pulse ring for high impact vessels -->
        <div style="
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          width: ${size * 1.5}px;
          height: ${size * 1.5}px;
          border: 2px solid ${color};
          border-radius: 50%;
          opacity: 0.5;
          animation: pulse-ring 2s ease-out infinite;
        "></div>
        ` : ''}
      </div>
    `,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2]
  });
};

function VesselMarker({ ship, color, onSelect, isSelected }) {
  const { vessel, economic_significance, carrying_commodity, market_events, heading, route_progress } = ship;
  
  const handleClick = () => {
    onSelect(ship);
  };
  
  const formatSpeed = (speed) => `${speed.toFixed(1)} kn`;
  
  const formatEta = (eta) => {
    const date = new Date(eta);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  const getImpactColor = (score) => {
    if (score >= 80) return '#ef4444';
    if (score >= 60) return '#f59e0b';
    if (score >= 40) return '#22c55e';
    return '#6366f1';
  };
  
  const impactColor = useMemo(() => getImpactColor(economic_significance), [economic_significance]);
  
  const icon = useMemo(() => 
    createVesselIcon(color, isSelected, economic_significance, heading),
    [color, isSelected, economic_significance, heading, color]
  );
  
  // Get impact label
  const getImpactLabel = (score) => {
    if (score >= 80) return 'Critical';
    if (score >= 60) return 'High';
    if (score >= 40) return 'Medium';
    return 'Low';
  };
  
  return (
    <Marker
      position={[vessel.latitude, vessel.longitude]}
      icon={icon}
      eventHandlers={{
        click: handleClick
      }}
    >
      <Tooltip
        direction="top"
        offset={[0, -12]}
        opacity={0.95}
        className="vessel-tooltip"
      >
        <div className="vessel-tooltip-content">
          <div className="tooltip-header">
            <strong>{vessel.vessel_name}</strong>
            <span 
              className="impact-badge"
              style={{ backgroundColor: impactColor }}
            >
              {getImpactLabel(economic_significance)}
            </span>
          </div>
          <div className="tooltip-body">
            <div className="tooltip-row">
              <span style={{ color: impactColor }}>
                Impact: {economic_significance.toFixed(0)}%
              </span>
            </div>
            <div className="tooltip-row">
              <span>{vessel.vessel_type.replace('_', ' ')}</span>
            </div>
            <div className="tooltip-row">
              <span>{carrying_commodity}</span>
            </div>
            {heading && (
              <div className="tooltip-row">
                <span>Heading: {heading.toFixed(0)}°</span>
              </div>
            )}
          </div>
        </div>
      </Tooltip>
      
      <Popup>
        <div className="vessel-popup">
          <div className="vessel-popup-header">
            <span 
              className="vessel-type-badge"
              style={{ 
                backgroundColor: color,
                color: 'white'
              }}
            >
              {vessel.vessel_type.replace('_', ' ')}
            </span>
            <span className="vessel-popup-name">{vessel.vessel_name}</span>
          </div>
          
          <div className="vessel-popup-details">
            <div className="detail-grid">
              <div className="detail-item">
                <span className="detail-label">MMSI</span>
                <span className="detail-value">{vessel.mmsi}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Status</span>
                <span className="detail-value" style={{ textTransform: 'capitalize' }}>{vessel.status}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Speed</span>
                <span className="detail-value">{formatSpeed(vessel.speed)}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">ETA</span>
                <span className="detail-value">{formatEta(vessel.eta)}</span>
              </div>
            </div>
            <div className="detail-full">
              <span className="detail-label">Destination</span>
              <span className="detail-value">{vessel.destination}</span>
            </div>
            <div className="detail-full">
              <span className="detail-label">Cargo</span>
              <span className="detail-value">{carrying_commodity}</span>
            </div>
            {route_progress !== undefined && (
              <div className="detail-full">
                <span className="detail-label">Route Progress</span>
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ 
                      width: `${route_progress * 100}%`,
                      backgroundColor: color
                    }}
                  ></div>
                </div>
                <span className="progress-text">{(route_progress * 100).toFixed(1)}%</span>
              </div>
            )}
          </div>
          
          <div className="vessel-popup-impact">
            <div className="impact-header">
              <span>Economic Impact</span>
              <span style={{ color: impactColor, fontWeight: '600' }}>
                {economic_significance.toFixed(0)}%
              </span>
            </div>
            <div className="impact-bar-large">
              <div 
                className="impact-fill-large"
                style={{ 
                  width: `${economic_significance}%`,
                  backgroundColor: impactColor
                }}
              ></div>
            </div>
            <div className="impact-labels">
              <span>Low</span>
              <span>Critical</span>
            </div>
          </div>
          
          {market_events && market_events.length > 0 && (
            <div className="vessel-events">
              <div className="events-header">
                <span>Active Events</span>
                <span className="event-count">{market_events.length}</span>
              </div>
              <div className="events-list">
                {market_events.map((event, idx) => (
                  <span 
                    key={idx}
                    className="event-tag"
                  >
                    {event}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          <button 
            className="view-details-btn"
            onClick={handleClick}
          >
            View Full Analysis
          </button>
        </div>
        
        <style>{`
          @keyframes pulse-ring {
            0% {
              transform: translate(-50%, -50%) scale(0.8);
              opacity: 0.8;
            }
            100% {
              transform: translate(-50%, -50%) scale(1.5);
              opacity: 0;
            }
          }
        `}</style>
      </Popup>
    </Marker>
  );
}

export default VesselMarker;

