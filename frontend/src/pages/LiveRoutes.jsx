import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Polyline, Marker, Tooltip } from 'react-leaflet';
import { motion } from 'framer-motion';
import { Search, RefreshCw, Star } from 'lucide-react';
import L from 'leaflet';
import './LiveRoutes.css';

// Fix Leaflet default icon
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Create star icon for shared stops
const createStarIcon = (color) => {
  return L.divIcon({
    className: 'star-marker',
    html: `<div style="color: ${color}; font-size: 24px; text-shadow: 0 0 3px white;">★</div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12]
  });
};

const LiveRoutes = () => {
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [data, setData] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedBuses, setSelectedBuses] = useState([]);
  const [showPOIs, setShowPOIs] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/routes/live');
      const result = await response.json();
      setData(result);
    } catch (error) {
      console.error('Error loading routes:', error);
      alert('No data found. Please click "Refresh Live Data" to fetch from API.');
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    try {
      setRefreshing(true);
      await fetch('http://localhost:8000/api/routes/refresh', { method: 'POST' });
      await loadData();
      alert('Data refreshed successfully!');
    } catch (error) {
      console.error('Error refreshing data:', error);
      alert('Error refreshing data. Check console for details.');
    } finally {
      setRefreshing(false);
    }
  };

  const toggleBusSelection = (busId) => {
    if (selectedBuses.includes(busId)) {
      setSelectedBuses(selectedBuses.filter(id => id !== busId));
    } else {
      if (selectedBuses.length >= 2) {
        alert('Maximum 2 buses can be compared!');
        return;
      }
      setSelectedBuses([...selectedBuses, busId]);
    }
  };

  const clearComparison = () => {
    setSelectedBuses([]);
  };

  const getBusColor = (index) => {
    const colors = ['#2196F3', '#FF5722'];
    return colors[index] || '#9E9E9E';
  };

  const getSharedStops = () => {
    if (selectedBuses.length !== 2 || !data) return [];
    
    const stops1 = data.stops.filter(s => s.bus_id === selectedBuses[0]);
    const stops2 = data.stops.filter(s => s.bus_id === selectedBuses[1]);
    
    const shared = [];
    stops1.forEach(stop1 => {
      const matchingStop = stops2.find(s => s.stop_name === stop1.stop_name);
      if (matchingStop) {
        shared.push({
          name: stop1.stop_name,
          lat: stop1.lat,
          lon: stop1.lon
        });
      }
    });
    
    return shared;
  };

  const getComparisonMetrics = () => {
    if (selectedBuses.length === 0 || !data) return null;
    
    const sharedStops = getSharedStops();
    
    const metrics = selectedBuses.map(busId => {
      const bus = data.buses.find(b => b.id === busId);
      const stops = data.stops.filter(s => s.bus_id === busId);
      
      return {
        busId,
        number: bus?.number || '',
        route: `${bus?.firstPoint || ''} → ${bus?.lastPoint || ''}`,
        stops: stops.length,
        duration: bus?.duration || 0,
        minPerStop: bus?.duration && stops.length > 0 
          ? (bus.duration / stops.length).toFixed(2) 
          : 0
      };
    });
    
    return {
      buses: metrics,
      sharedStops: sharedStops.length
    };
  };

  const filteredBuses = data?.buses.filter(bus => {
    const term = searchTerm.toLowerCase();
    return (
      bus.number?.toLowerCase().includes(term) ||
      bus.firstPoint?.toLowerCase().includes(term) ||
      bus.lastPoint?.toLowerCase().includes(term)
    );
  }) || [];

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner" />
        <p>Loading live routes...</p>
      </div>
    );
  }

  const sharedStops = getSharedStops();
  const comparison = getComparisonMetrics();

  return (
    <div className="live-routes-layout">
      <motion.div
        className="page-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div>
          <h1>🚌 Live Bus Routes</h1>
          <p>Select up to 2 buses to compare routes and stops</p>
        </div>
        <button 
          onClick={refreshData} 
          disabled={refreshing}
          className="refresh-button"
        >
          <RefreshCw size={18} className={refreshing ? 'spinning' : ''} />
          {refreshing ? 'Refreshing...' : 'Refresh Live Data'}
        </button>
      </motion.div>

      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-number">{data?.pois?.length || 0}</div>
          <div className="stat-label">📍 POIs</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{data?.buses?.length || 0}</div>
          <div className="stat-label">🚌 Routes</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{data?.stops?.length || 0}</div>
          <div className="stat-label">🚏 Stops</div>
        </div>
      </div>

      {comparison && comparison.buses.length > 0 && (
        <motion.div 
          className="comparison-panel"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="comparison-header">
            <h3>📊 Route Comparison</h3>
            <button onClick={clearComparison} className="clear-btn">Clear</button>
          </div>
          
          <div className="comparison-grid">
            {comparison.buses.map((bus, index) => (
              <div key={bus.busId} className={`bus-comparison-card bus${index + 1}`}>
                <div className="bus-badge" style={{ background: getBusColor(index) }}>
                  Bus {bus.number}
                </div>
                <div className="bus-route-name">{bus.route}</div>
                <div className="metrics-list">
                  <div className="metric-item">
                    <span>Stops:</span>
                    <strong>{bus.stops}</strong>
                  </div>
                  <div className="metric-item">
                    <span>Duration:</span>
                    <strong>{bus.duration} min</strong>
                  </div>
                  <div className="metric-item">
                    <span>Min/Stop:</span>
                    <strong>{bus.minPerStop}</strong>
                  </div>
                </div>
              </div>
            ))}
            
            {comparison.buses.length === 2 && (
              <div className="shared-stops-card">
                <Star size={24} color="#FFC107" />
                <div>
                  <div className="shared-number">{comparison.sharedStops}</div>
                  <div className="shared-label">Shared Stops</div>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      )}

      <div className="main-content">
        <div className="sidebar-panel">
          <div className="sidebar-header">
            <h3>Bus Routes ({filteredBuses.length})</h3>
          </div>

          <div className="sidebar-search">
            <Search size={18} color="#333" />
            <input
              type="text"
              placeholder="Search buses..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="bus-scroll-list">
            {filteredBuses.map((bus) => {
              const isSelected = selectedBuses.includes(bus.id);
              const selectionIndex = selectedBuses.indexOf(bus.id);
              
              return (
                <div
                  key={bus.id}
                  className={`bus-list-item ${isSelected ? `selected selected-${selectionIndex + 1}` : ''}`}
                  onClick={() => toggleBusSelection(bus.id)}
                >
                  <div className="bus-list-checkbox">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      readOnly
                    />
                  </div>
                  <div 
                    className="bus-list-number"
                    style={isSelected ? { background: getBusColor(selectionIndex), color: '#fff' } : {}}
                  >
                    {bus.number}
                  </div>
                  <div className="bus-list-info">
                    <div className="bus-list-route">{bus.firstPoint} → {bus.lastPoint}</div>
                    <div className="bus-list-details">
                      {bus.stops_count} stops • {bus.duration} min
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="sidebar-footer">
            <label>
              <input 
                type="checkbox" 
                checked={showPOIs} 
                onChange={(e) => setShowPOIs(e.target.checked)}
              />
              <span>Show POIs</span>
            </label>
          </div>
        </div>

        <div className="map-panel">
          <MapContainer
            center={[40.4093, 49.8671]}
            zoom={11}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; OpenStreetMap'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {showPOIs && data?.pois?.map((poi, index) => (
              <Marker
                key={`poi-${index}`}
                position={[poi.lat, poi.lon]}
                icon={L.icon({
                  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                  iconSize: [25, 41],
                  iconAnchor: [12, 41],
                  popupAnchor: [1, -34],
                  shadowSize: [41, 41]
                })}
              >
                <Tooltip>{poi.title}</Tooltip>
              </Marker>
            ))}

            {selectedBuses.map((busId, index) => {
              const busStops = data?.stops?.filter(s => s.bus_id === busId) || [];
              const color = getBusColor(index);
              
              const stopCoords = busStops.map(s => [s.lat, s.lon]);
              
              return (
                <React.Fragment key={`bus-${busId}`}>
                  {stopCoords.length > 1 && (
                    <Polyline
                      positions={stopCoords}
                      pathOptions={{
                        color: color,
                        weight: 5,
                        opacity: 0.8,
                        smoothFactor: 1
                      }}
                    />
                  )}

                  {busStops.map((stop, stopIndex) => {
                    const isShared = sharedStops.some(s => s.name === stop.stop_name);
                    
                    if (isShared) {
                      return (
                        <Marker
                          key={`stop-${busId}-${stopIndex}`}
                          position={[stop.lat, stop.lon]}
                          icon={createStarIcon('#FFC107')}
                        >
                          <Tooltip>
                            <strong>⭐ {stop.stop_name}</strong>
                            <br />
                            <span style={{ color: '#FFC107' }}>Shared Stop</span>
                          </Tooltip>
                        </Marker>
                      );
                    } else {
                      return (
                        <CircleMarker
                          key={`stop-${busId}-${stopIndex}`}
                          center={[stop.lat, stop.lon]}
                          radius={7}
                          pathOptions={{
                            fillColor: color,
                            color: '#fff',
                            weight: 2,
                            opacity: 1,
                            fillOpacity: 0.9
                          }}
                        >
                          <Tooltip>
                            <strong>{stop.stop_name}</strong>
                            <br />
                            <small>Bus {stop.bus_number}</small>
                          </Tooltip>
                        </CircleMarker>
                      );
                    }
                  })}
                </React.Fragment>
              );
            })}
          </MapContainer>

          {selectedBuses.length > 0 && (
            <div className="map-legend">
              <h4>Legend</h4>
              {selectedBuses.map((busId, index) => {
                const bus = data?.buses?.find(b => b.id === busId);
                const color = getBusColor(index);
                return (
                  <div key={busId} className="legend-item">
                    <div className="legend-line" style={{ background: color }}></div>
                    <span>Bus {bus?.number}</span>
                  </div>
                );
              })}
              <div className="legend-item">
                <Star size={16} color="#FFC107" fill="#FFC107" />
                <span>Shared Stops</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LiveRoutes;
