import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, Polyline, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import './ShippingMap.css';
import VesselMarker from './VesselMarker';
import MarketImpactPanel from './MarketImpactPanel';
import axios from 'axios';

// Fix for default marker icons in Leaflet with React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Vessel type icons configuration
const vesselTypeColors = {
  container: '#3b82f6',
  bulk: '#f59e0b',
  tanker: '#ef4444',
  gas_carrier: '#10b981',
  cruise: '#8b5cf6'
};

// Shipping route waypoints for visualization
const SHIPPING_ROUTES = {
  asia_europe: [
    [31.2304, 121.4737], [30.5, 125.0], [25.0, 120.0], [15.0, 110.0], [3.0, 100.0],
    [0.0, 80.0], [-10.0, 60.0], [15.0, 40.0], [29.9, 32.5], [30.5852, 32.2650],
    [32.0, 30.0], [35.0, 20.0], [36.0, 5.0], [45.0, -5.0], [51.0, 2.0], [51.9244, 4.4777]
  ],
  asia_west_coast: [
    [31.2304, 121.4737], [30.0, 140.0], [25.0, 150.0], [20.0, -160.0],
    [25.0, -170.0], [30.0, -140.0], [33.0, -130.0], [33.7405, -118.2786]
  ],
  asia_east_coast: [
    [31.2304, 121.4737], [25.0, 130.0], [15.0, -100.0], [9.0, -79.5], [8.5, -80.0],
    [10.0, -70.0], [20.0, -75.0], [30.0, -80.0], [40.7128, -74.0060]
  ],
  middle_east_asia: [
    [26.65, 50.15], [25.0, 55.0], [25.0, 60.0], [22.0, 67.0], [15.0, 70.0],
    [10.0, 80.0], [5.0, 95.0], [1.3521, 103.8198], [3.0, 100.0], [5.0, 110.0], [22.0, 114.0], [22.5431, 114.0579]
  ],
  europe_usa: [
    [51.9244, 4.4777], [51.0, 0.0], [45.0, -5.0], [40.0, -30.0], [35.0, -60.0], [38.0, -70.0], [40.0, -75.0], [40.7128, -74.0060]
  ]
};

// Major shipping chokepoints
const CHOKEPOINTS = [
  { name: 'Suez Canal', coords: [30.5852, 32.2650], risk: 'high' },
  { name: 'Panama Canal', coords: [9.0, -79.5], risk: 'medium' },
  { name: 'Malacca Strait', coords: [2.5, 101.5], risk: 'high' },
  { name: 'Gibraltar', coords: [35.9, -5.5], risk: 'low' },
  { name: 'Bosporus', coords: [41.0, 29.0], risk: 'medium' }
];

// Major ports
const MAJOR_PORTS = [
  { name: 'Shanghai', coords: [31.2304, 121.4737] },
  { name: 'Singapore', coords: [1.3521, 103.8198] },
  { name: 'Rotterdam', coords: [51.9244, 4.4777] },
  { name: 'Los Angeles', coords: [33.7405, -118.2786] },
  { name: 'New York', coords: [40.7128, -74.0060] },
  { name: 'Dubai', coords: [25.2048, 55.2708] },
  { name: 'Hamburg', coords: [53.5511, 9.9937] },
  { name: 'Antwerp', coords: [51.2194, 4.4025] },
  { name: 'Busan', coords: [35.1796, 129.0756] },
  { name: 'Tokyo', coords: [35.6762, 139.6503] },
  { name: 'Ningbo', coords: [29.8683, 121.5440] },
  { name: 'Shenzhen', coords: [22.5431, 114.0579] },
  { name: 'Hong Kong', coords: [22.3193, 114.1694] },
  { name: 'Santos', coords: [-23.9608, -46.3331] },
  { name: 'Ras Tanura', coords: [26.65, 50.15] }
];

// Component to handle map centering on vessel selection
function MapController({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.flyTo(center, zoom || 5, { duration: 1 });
    }
  }, [center, zoom, map]);
  return null;
}

function ShippingMap() {
  const [vessels, setVessels] = useState([]);
  const [selectedVessel, setSelectedVessel] = useState(null);
  const [filters, setFilters] = useState({
    vesselType: 'all',
    showHighImpact: false,
    showRoutes: true,
    showChokepoints: true,
    showPorts: true
  });
  const [commodityImpact, setCommodityImpact] = useState(null);
  const [forexImpact, setForexImpact] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [activeChokepoints, setActiveChokepoints] = useState([]);
  const [portCongestion, setPortCongestion] = useState([]);
  const [mapCenter, setMapCenter] = useState([20, 0]);

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1/shipping';

  // Fetch all shipping data
  const fetchVesselData = useCallback(async () => {
    try {
      setIsLoading(true);
      const params = {};
      if (filters.vesselType !== 'all') {
        params.vessel_type = filters.vesselType;
      }
      
      const [vesselsRes, commodityRes, forexRes] = await Promise.all([
        axios.get(`${API_BASE}/tracking/live`, { params }),
        axios.get(`${API_BASE}/tracking/commodity-impact`),
        axios.get(`${API_BASE}/tracking/forex-impact`)
      ]);

      setVessels(vesselsRes.data.vessels || []);
      setActiveChokepoints(vesselsRes.data.active_chokepoints || []);
      setPortCongestion(vesselsRes.data.port_congestion || []);
      setCommodityImpact(commodityRes.data);
      setForexImpact(forexRes.data);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Error fetching shipping data:', error);
    } finally {
      setIsLoading(false);
    }
  }, [filters.vesselType, API_BASE]);

  useEffect(() => {
    fetchVesselData();
    const interval = setInterval(fetchVesselData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, [fetchVesselData]);

  // Filter vessels based on settings
  const filteredVessels = useMemo(() => {
    return vessels.filter(vessel => {
      if (filters.showHighImpact && vessel.economic_significance <= 80) {
        return false;
      }
      return true;
    });
  }, [vessels, filters.showHighImpact]);

  // Calculate vessel counts
  const vesselCounts = useMemo(() => {
    return vessels.reduce((acc, v) => {
      const type = v.vessel.vessel_type;
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {});
  }, [vessels]);

  // Calculate global trade index
  const globalTradeIndex = useMemo(() => {
    if (vessels.length > 0) {
      return vessels[0]?.global_trade_index || 102.5;
    }
    return 102.5;
  }, [vessels]);

  // Handle vessel selection with map centering
  const handleVesselSelect = useCallback((ship) => {
    setSelectedVessel(ship);
    if (ship?.vessel) {
      setMapCenter([ship.vessel.latitude, ship.vessel.longitude]);
    }
  }, []);

  // Get port congestion color
  const getCongestionColor = (status) => {
    switch (status) {
      case 'congested': return '#ef4444';
      case 'moderate': return '#f59e0b';
      default: return '#22c55e';
    }
  };

  // Get chokepoint color
  const getChokepointColor = (risk) => {
    switch (risk) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      default: return '#22c55e';
    }
  };

  return (
    <div className="shipping-map-container">
      {/* Header Stats Bar */}
      <div className="shipping-stats-bar">
        <div className="stat-item">
          <span className="stat-label">Total Vessels</span>
          <span className="stat-value">{vessels.length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Global Trade Index</span>
          <span className="stat-value">{globalTradeIndex.toFixed(1)}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Active Chokepoints</span>
          <span className="stat-value">{activeChokepoints.filter(c => c.status !== 'normal').length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Last Update</span>
          <span className="stat-value">
            {lastUpdate ? lastUpdate.toLocaleTimeString() : 'Never'}
          </span>
        </div>
        <div className="vessel-type-legend">
          {Object.entries(vesselTypeColors).map(([type, color]) => (
            <div key={type} className="legend-item">
              <span className="legend-dot" style={{ backgroundColor: color }}></span>
              <span className="legend-count">{vesselCounts[type] || 0}</span>
              <span className="legend-label">{type.replace('_', ' ')}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Filter Controls */}
      <div className="shipping-filters">
        <select 
          value={filters.vesselType}
          onChange={(e) => setFilters({...filters, vesselType: e.target.value})}
          className="filter-select"
        >
          <option value="all">All Vessel Types</option>
          <option value="container">Container Ships</option>
          <option value="bulk">Bulk Carriers</option>
          <option value="tanker">Tankers</option>
          <option value="gas_carrier">Gas Carriers</option>
          <option value="cruise">Cruise Ships</option>
        </select>
        
        <label className="filter-checkbox">
          <input
            type="checkbox"
            checked={filters.showHighImpact}
            onChange={(e) => setFilters({...filters, showHighImpact: e.target.checked})}
          />
          High Impact Only
        </label>

        <label className="filter-checkbox">
          <input
            type="checkbox"
            checked={filters.showRoutes}
            onChange={(e) => setFilters({...filters, showRoutes: e.target.checked})}
          />
          Show Routes
        </label>

        <label className="filter-checkbox">
          <input
            type="checkbox"
            checked={filters.showChokepoints}
            onChange={(e) => setFilters({...filters, showChokepoints: e.target.checked})}
          />
          Chokepoints
        </label>

        <label className="filter-checkbox">
          <input
            type="checkbox"
            checked={filters.showPorts}
            onChange={(e) => setFilters({...filters, showPorts: e.target.checked})}
          />
          Ports
        </label>
        
        <button 
          className="refresh-btn"
          onClick={fetchVesselData}
          disabled={isLoading}
        >
          {isLoading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      {/* Main Map */}
      <div className="map-content">
        <div className="map-wrapper">
          <MapContainer
            center={[20, 0]}
            zoom={2}
            className="shipping-leaflet-map"
            worldCopyJump={true}
            minZoom={2}
            maxZoom={10}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />
            
            <MapController center={mapCenter} />

            {/* Shipping Routes */}
            {filters.showRoutes && Object.entries(SHIPPING_ROUTES).map(([routeName, waypoints]) => (
              <Polyline
                key={routeName}
                positions={waypoints}
                pathOptions={{
                  color: '#6366f1',
                  weight: 2,
                  opacity: 0.4,
                  dashArray: '5, 10'
                }}
              />
            ))}

            {/* Major Ports */}
            {filters.showPorts && MAJOR_PORTS.map(port => {
              const congestion = portCongestion.find(c => c.name === port.name);
              const color = congestion ? getCongestionColor(congestion.status) : '#6366f1';
              return (
                <Circle
                  key={port.name}
                  center={port.coords}
                  radius={40000}
                  pathOptions={{
                    color: color,
                    fillColor: color,
                    fillOpacity: 0.2,
                    weight: 2
                  }}
                >
                  <Popup>
                    <div className="port-popup">
                      <strong>{port.name}</strong>
                      {congestion && (
                        <>
                          <p>Vessels: {congestion.vessels_in_port}</p>
                          <p>Wait: {congestion.avg_wait_hours}h</p>
                          <p>Status: {congestion.status}</p>
                        </>
                      )}
                    </div>
                  </Popup>
                </Circle>
              );
            })}

            {/* Shipping Chokepoints */}
            {filters.showChokepoints && CHOKEPOINTS.map(chokepoint => {
              const activeData = activeChokepoints.find(c => c.name === chokepoint.name);
              const color = getChokepointColor(chokepoint.risk);
              return (
                <Circle
                  key={chokepoint.name}
                  center={chokepoint.coords}
                  radius={100000}
                  pathOptions={{
                    color: color,
                    fillColor: color,
                    fillOpacity: 0.15,
                    weight: 2,
                    dashArray: activeData?.status !== 'normal' ? '5, 5' : undefined
                  }}
                >
                  <Popup>
                    <div className="chokepoint-popup">
                      <strong>{chokepoint.name}</strong>
                      <p>Risk Level: {chokepoint.risk}</p>
                      {activeData && (
                        <>
                          <p>Vessels Transiting: {activeData.vessels_transiting}</p>
                          <p>Avg Delay: {activeData.avg_delay_hours}h</p>
                          <p>Status: {activeData.status}</p>
                        </>
                      )}
                    </div>
                  </Popup>
                </Circle>
              );
            })}

            {/* Vessel Markers */}
            {filteredVessels.map((ship) => (
              <VesselMarker
                key={ship.vessel.mmsi}
                ship={ship}
                color={vesselTypeColors[ship.vessel.vessel_type] || '#6366f1'}
                onSelect={handleVesselSelect}
                isSelected={selectedVessel?.vessel.mmsi === ship.vessel.mmsi}
              />
            ))}
          </MapContainer>

          {/* Chokepoints Overview Panel */}
          <div className="chokepoints-panel">
            <h4>Shipping Chokepoints</h4>
            {activeChokepoints.length > 0 ? (
              activeChokepoints.map(cp => (
                <div 
                  key={cp.id} 
                  className={`chokepoint-item ${cp.status !== 'normal' ? 'alert' : ''}`}
                  onClick={() => setMapCenter([cp.position.lat, cp.position.lon])}
                >
                  <div className="chokepoint-info">
                    <span className="chokepoint-name">{cp.name}</span>
                    <span className={`chokepoint-status ${cp.status}`}>{cp.status}</span>
                  </div>
                  <div className="chokepoint-details">
                    <span>Vessels: {cp.vessels_transiting}</span>
                    <span>Delay: {cp.avg_delay_hours}h</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="no-data">Loading chokepoint data...</p>
            )}
          </div>
        </div>

        {/* Market Impact Panel */}
        <MarketImpactPanel
          selectedVessel={selectedVessel}
          commodityImpact={commodityImpact}
          forexImpact={forexImpact}
          portCongestion={portCongestion}
          onClose={() => setSelectedVessel(null)}
        />
      </div>

      {/* Loading Overlay */}
      {isLoading && vessels.length === 0 && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <p>Loading vessel positions...</p>
        </div>
      )}
    </div>
  );
}

export default ShippingMap;

