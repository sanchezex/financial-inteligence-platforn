import React, { useState, useEffect } from 'react';
import axios from 'axios';

function MarketImpactPanel({ selectedVessel, commodityImpact, forexImpact, portCongestion, onClose }) {
  const [vesselDetail, setVesselDetail] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1/shipping';

  useEffect(() => {
    if (selectedVessel) {
      fetchVesselDetail();
    }
  }, [selectedVessel]);

  const fetchVesselDetail = async () => {
    if (!selectedVessel) return;
    
    try {
      setIsLoading(true);
      const response = await axios.get(
        `${API_BASE}/tracking/vessel/${selectedVessel.vessel.mmsi}/impact`
      );
      setVesselDetail(response.data);
    } catch (error) {
      console.error('Error fetching vessel detail:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!selectedVessel && !commodityImpact && !forexImpact && !portCongestion) {
    return (
      <div className="market-impact-panel">
        <div className="no-selection">
          <div className="no-selection-icon"></div>
          <h4>No Data Available</h4>
          <p>Loading market impact data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="market-impact-panel">
      <div className="panel-header">
        <h3>Market Impact Analysis</h3>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>

      <div className="panel-content">
        {/* Selected Vessel Details */}
        {selectedVessel && (
          <>
            <div className="panel-section">
              <h4>Vessel Information</h4>
              <div className="price-card">
                <div className="price-header">
                  <span className="price-symbol">{selectedVessel.vessel.vessel_name}</span>
                  <span 
                    className="price-change"
                    style={{
                      backgroundColor: selectedVessel.economic_significance > 70 
                        ? 'rgba(239, 68, 68, 0.2)' 
                        : 'rgba(34, 197, 94, 0.2)',
                      color: selectedVessel.economic_significance > 70 
                        ? '#ef4444' 
                        : '#22c55e'
                    }}
                  >
                    {selectedVessel.economic_significance > 70 ? 'High Impact' : 'Medium Impact'}
                  </span>
                </div>
                
                <div className="quick-stats-grid">
                  <div className="quick-stat">
                    <div className="quick-stat-label">Type</div>
                    <div className="quick-stat-value" style={{ textTransform: 'capitalize' }}>
                      {selectedVessel.vessel.vessel_type.replace('_', ' ')}
                    </div>
                  </div>
                  <div className="quick-stat">
                    <div className="quick-stat-label">Speed</div>
                    <div className="quick-stat-value">
                      {selectedVessel.vessel.speed.toFixed(1)} kn
                    </div>
                  </div>
                  <div className="quick-stat">
                    <div className="quick-stat-label">Destination</div>
                    <div className="quick-stat-value">
                      {selectedVessel.vessel.destination}
                    </div>
                  </div>
                  <div className="quick-stat">
                    <div className="quick-stat-label">Cargo</div>
                    <div className="quick-stat-value">
                      {selectedVessel.carrying_commodity}
                    </div>
                  </div>
                  {selectedVessel.heading && (
                    <div className="quick-stat">
                      <div className="quick-stat-label">Heading</div>
                      <div className="quick-stat-value">
                        {selectedVessel.heading.toFixed(0)}°
                      </div>
                    </div>
                  )}
                  {selectedVessel.route_name && (
                    <div className="quick-stat">
                      <div className="quick-stat-label">Route</div>
                      <div className="quick-stat-value" style={{ fontSize: '14px' }}>
                        {selectedVessel.route_name.replace(/_/g, ' ')}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Risk Assessment */}
            {vesselDetail && (
              <div className="panel-section">
                <h4>Risk Assessment</h4>
                <div className="risk-card">
                  <div className="risk-header">
                    <span className="risk-title">Overall Risk Score</span>
                    <span 
                      className={`risk-score ${
                        vesselDetail.risk_assessment.overall_risk_score > 60 
                          ? 'high' 
                          : vesselDetail.risk_assessment.overall_risk_score > 40 
                            ? 'medium' 
                            : 'low'
                      }`}
                    >
                      {vesselDetail.risk_assessment.overall_risk_score.toFixed(0)}/100
                    </span>
                  </div>
                  
                  <div className="risk-factors">
                    <div className="risk-factor">
                      <span className="factor-label">Geopolitical Risk</span>
                      <span className="factor-value">
                        {vesselDetail.risk_assessment.geopolitical_risk.toFixed(0)}/100
                      </span>
                    </div>
                    <div className="risk-factor">
                      <span className="factor-label">Weather Risk</span>
                      <span className="factor-value">
                        {vesselDetail.risk_assessment.weather_risk.toFixed(0)}/100
                      </span>
                    </div>
                    <div className="risk-factor">
                      <span className="factor-label">Regulatory Risk</span>
                      <span className="factor-value">
                        {vesselDetail.risk_assessment.regulatory_risk.toFixed(0)}/100
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Active Events */}
            {selectedVessel.market_events && selectedVessel.market_events.length > 0 && (
              <div className="panel-section">
                <h4>Active Market Events</h4>
                <div className="events-list">
                  {selectedVessel.market_events.map((event, idx) => (
                    <div key={idx} className="event-item">
                      <span className="event-icon"></span>
                      <div className="event-content">
                        <div className="event-title">{event}</div>
                        <div className="event-time">Active - May affect prices</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Commodity Impact */}
            {selectedVessel.commodity_impact && (
              <div className="panel-section">
                <h4>Commodity Impact</h4>
                <div className="price-card">
                  <div className="price-header">
                    <span className="price-symbol">{selectedVessel.commodity_impact.commodity}</span>
                    <span 
                      className={`price-change ${selectedVessel.commodity_impact.price_change_24h >= 0 ? 'positive' : 'negative'}`}
                    >
                      {selectedVessel.commodity_impact.price_change_24h >= 0 ? '+' : ''}
                      {selectedVessel.commodity_impact.price_change_24h.toFixed(2)}%
                    </span>
                  </div>
                  <div className="price-value">
                    ${selectedVessel.commodity_impact.current_price.toFixed(2)}
                  </div>
                  <div className="price-meta">
                    <span className="meta-tag">
                      Shipping Impact: {selectedVessel.commodity_impact.shipping_impact_score.toFixed(0)}%
                    </span>
                    <span className="meta-tag">
                      {selectedVessel.commodity_impact.supply_demand_balance}
                    </span>
                    <span className="meta-tag">
                      {selectedVessel.commodity_impact.market_sentiment}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Forex Impact */}
            {selectedVessel.forex_impact && (
              <div className="panel-section">
                <h4>Forex Impact</h4>
                <div className="forex-card">
                  <div className="forex-pair">{selectedVessel.forex_impact.currency_pair}</div>
                  <div className="forex-rate">{selectedVessel.forex_impact.current_rate.toFixed(4)}</div>
                  <div 
                    className={`price-change ${selectedVessel.forex_impact.change_24h >= 0 ? 'positive' : 'negative'}`}
                    style={{ marginBottom: '12px', display: 'inline-block' }}
                  >
                    {selectedVessel.forex_impact.change_24h >= 0 ? '+' : ''}
                    {selectedVessel.forex_impact.change_24h.toFixed(4)}%
                  </div>
                  <div className="forex-details">
                    <div className="detail-item">
                      <span className="detail-label">Shipping Impact</span>
                      <span className="detail-value">{selectedVessel.forex_impact.shipping_impact_score.toFixed(0)}%</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Trade Volume</span>
                      <span className="detail-value">{selectedVessel.forex_impact.trade_volume_impact}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Central Bank</span>
                      <span className="detail-value">{selectedVessel.forex_impact.central_bank_factor}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}

        {/* Port Congestion Summary */}
        {portCongestion && portCongestion.length > 0 && !selectedVessel && (
          <div className="panel-section">
            <h4>Port Congestion Monitor</h4>
            {portCongestion.slice(0, 5).map((port, idx) => (
              <div key={idx} className="congestion-card">
                <div className="congestion-header">
                  <span className="congestion-port">{port.name}</span>
                  <span className={`congestion-status ${port.status}`}>{port.status}</span>
                </div>
                <div className="congestion-stats">
                  <div className="congestion-stat">
                    <div className="congestion-stat-value">{port.vessels_in_port}</div>
                    <div className="congestion-stat-label">In Port</div>
                  </div>
                  <div className="congestion-stat">
                    <div className="congestion-stat-value">{port.vessels_anchored}</div>
                    <div className="congestion-stat-label">Anchored</div>
                  </div>
                  <div className="congestion-stat">
                    <div className="congestion-stat-value">{port.avg_wait_hours}h</div>
                    <div className="congestion-stat-label">Avg Wait</div>
                  </div>
                </div>
                <div style={{ 
                  fontSize: '11px', 
                  color: 'var(--text-muted)',
                  textAlign: 'center'
                }}>
                  Utilization: {port.utilization}% | {port.country}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Commodity Impact Summary */}
        {commodityImpact && (
          <div className="panel-section">
            <h4>Commodity Price Watch</h4>
            {commodityImpact.commodities?.map((commodity, idx) => (
              <div key={idx} className="price-card">
                <div className="price-header">
                  <span className="price-symbol">{commodity.name}</span>
                  <span 
                    className={`price-change ${commodity.change_24h >= 0 ? 'positive' : 'negative'}`}
                  >
                    {commodity.change_24h >= 0 ? '+' : ''}{commodity.change_24h.toFixed(2)}%
                  </span>
                </div>
                <div className="price-value" style={{ marginBottom: '8px' }}>
                  ${typeof commodity.price === 'number' ? commodity.price.toFixed(2) : commodity.price}
                </div>
                <div className="price-meta">
                  <span className="meta-tag">
                    Activity: {commodity.shipping_activity_index?.toFixed(0)}%
                  </span>
                  <span className="meta-tag">
                    Freight: {commodity.freight_cost_impact}
                  </span>
                  <span className="meta-tag">
                    Risk: {commodity.supply_disruption_risk}
                  </span>
                </div>
                {commodity.key_routes && (
                  <div className="key-routes">
                    <h5>Key Routes</h5>
                    {commodity.key_routes.map((route, rIdx) => (
                      <div key={rIdx} className="route-item">→ {route}</div>
                    ))}
                  </div>
                )}
                <div style={{ marginTop: '8px', fontSize: '11px', color: 'var(--text-muted)' }}>
                  Vessels en route: {commodity.vessels_en_route}
                </div>
              </div>
            ))}

            {/* Market Wide Impact */}
            {commodityImpact.market_wide_impact && (
              <div style={{ 
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '16px',
                marginTop: '12px'
              }}>
                <div style={{ fontSize: '13px', fontWeight: '600', marginBottom: '12px' }}>
                  Market Overview
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Avg Freight Change</span>
                    <span style={{ 
                      color: parseFloat(commodityImpact.market_wide_impact.avg_freight_cost_change) >= 0 ? 'var(--success)' : 'var(--danger)'
                    }}>
                      {commodityImpact.market_wide_impact.avg_freight_cost_change}
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Supply Chain Stress</span>
                    <span style={{ fontWeight: '600' }}>
                      {commodityImpact.market_wide_impact.supply_chain_stress_index}/100
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Market Sentiment</span>
                    <span style={{ 
                      fontWeight: '600',
                      color: commodityImpact.market_wide_impact.overall_market_sentiment === 'bullish' 
                        ? 'var(--success)' 
                        : commodityImpact.market_wide_impact.overall_market_sentiment === 'bearish'
                          ? 'var(--danger)'
                          : 'var(--warning)'
                    }}>
                      {commodityImpact.market_wide_impact.overall_market_sentiment}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Forex Impact Summary */}
        {forexImpact && (
          <div className="panel-section">
            <h4>Forex Correlation</h4>
            {forexImpact.currency_pairs?.slice(0, 4).map((pair, idx) => (
              <div key={idx} className="forex-card">
                <div className="forex-pair">{pair.pair}</div>
                <div className="forex-rate">{pair.rate.toFixed(4)}</div>
                <div 
                  className={`price-change ${pair.change_24h >= 0 ? 'positive' : 'negative'}`}
                  style={{ marginBottom: '8px', display: 'inline-block' }}
                >
                  {pair.change_24h >= 0 ? '+' : ''}{pair.change_24h.toFixed(4)}%
                </div>
                <div className="forex-details">
                  <div className="detail-item">
                    <span className="detail-label">Shipping Impact</span>
                    <span className="detail-value">{pair.shipping_impact_score.toFixed(0)}%</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Commodity Exp.</span>
                    <span className="detail-value">{pair.commodity_exposure}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Volume (USD)</span>
                    <span className="detail-value">
                      ${(pair.trade_volume_usd / 1000000000).toFixed(1)}B
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Volatility</span>
                    <span className="detail-value">{pair.volatility_forecast.toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            ))}

            {/* Correlation Insights */}
            {forexImpact.correlation_insights && forexImpact.correlation_insights.length > 0 && (
              <div style={{ 
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '16px'
              }}>
                <div style={{ 
                  fontSize: '13px', 
                  fontWeight: '600', 
                  marginBottom: '12px',
                  color: 'var(--text-primary)'
                }}>
                  Correlation Insights
                </div>
                {forexImpact.correlation_insights.map((insight, idx) => (
                  <div 
                    key={idx}
                    style={{
                      padding: '8px 0',
                      borderBottom: idx < forexImpact.correlation_insights.length - 1 
                        ? '1px solid var(--border-color)' 
                        : 'none',
                      fontSize: '12px',
                      color: 'var(--text-secondary)'
                    }}
                  >
                    {insight}
                  </div>
                ))}
              </div>
            )}

            {/* Regional Analysis */}
            {forexImpact.regional_analysis && (
              <div style={{ 
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '16px',
                marginTop: '12px'
              }}>
                <div style={{ 
                  fontSize: '13px', 
                  fontWeight: '600', 
                  marginBottom: '12px',
                  color: 'var(--text-primary)'
                }}>
                  Regional Shipping Impact
                </div>
                {Object.entries(forexImpact.regional_analysis).map(([region, data]) => (
                  <div 
                    key={region}
                    style={{
                      padding: '10px',
                      background: 'var(--bg-tertiary)',
                      borderRadius: '6px',
                      marginBottom: '8px'
                    }}
                  >
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: '8px'
                    }}>
                      <span style={{ fontWeight: '600', textTransform: 'capitalize' }}>{region}</span>
                      <span style={{ 
                        fontSize: '12px',
                        fontWeight: '600',
                        color: data.avg_shipping_impact > 60 ? 'var(--warning)' : 'var(--success)'
                      }}>
                        {data.avg_shipping_impact.toFixed(0)}% Impact
                      </span>
                    </div>
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                        Currencies: {data.key_currencies.join(', ')}
                      </span>
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                        Trade Index: {data.trade_volume_index.toFixed(0)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            padding: '40px',
            color: 'var(--text-muted)'
          }}>
            <div className="loading-spinner" style={{ width: '32px', height: '32px' }}></div>
          </div>
        )}
      </div>
    </div>
  );
}

export default MarketImpactPanel;

