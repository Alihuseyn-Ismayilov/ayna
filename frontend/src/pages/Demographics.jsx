import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import { motion } from 'framer-motion';
import { Users, Briefcase, Layers } from 'lucide-react';
import { demographicsAPI } from '../services/api';
import './Demographics.css';

const Demographics = () => {
  const [regionType, setRegionType] = useState('micro');
  const [colorMode, setColorMode] = useState('population'); // 'population' or 'jobs'
  const [geoData, setGeoData] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [geoJsonKey, setGeoJsonKey] = useState(0); // Force re-render on color change

  useEffect(() => {
    loadData();
  }, [regionType]);

  useEffect(() => {
    // Force GeoJSON to re-render when color mode changes
    setGeoJsonKey(prev => prev + 1);
  }, [colorMode]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [geoResponse, statsResponse] = await Promise.all([
        demographicsAPI.getData(regionType),
        demographicsAPI.getStats(regionType)
      ]);
      setGeoData(geoResponse.data);
      setStats(statsResponse.data);
    } catch (error) {
      console.error('Error loading demographics:', error);
    } finally {
      setLoading(false);
    }
  };

  // Get color based on value and mode
  const getColor = (value, maxValue) => {
    if (!value || !maxValue) return 'rgba(255, 255, 255, 0.1)';
    
    const ratio = value / maxValue;
    
    if (colorMode === 'population') {
      // Cyan to dark blue gradient
      const hue = 190 - (ratio * 60); // 190 (cyan) to 130 (dark blue)
      const lightness = 70 - (ratio * 40); // 70% to 30%
      return `hsl(${hue}, 100%, ${lightness}%)`;
    } else {
      // Light orange to dark red gradient
      const hue = 35 - (ratio * 20); // 35 (orange) to 15 (red)
      const lightness = 65 - (ratio * 35); // 65% to 30%
      return `hsl(${hue}, 100%, ${lightness}%)`;
    }
  };

  // Style each feature
  const styleFeature = (feature) => {
    if (!stats) return { fillColor: 'rgba(255, 255, 255, 0.1)', weight: 1 };

    const props = feature.properties;
    const value = colorMode === 'population' ? props.population : props.tot_jobs;
    const maxValue = colorMode === 'population' ? stats.population?.max : stats.jobs?.max;
    
    const fillColor = getColor(value, maxValue);

    return {
      fillColor,
      weight: 2,
      opacity: 1,
      color: 'rgba(255, 255, 255, 0.3)',
      fillOpacity: 0.7,
    };
  };

  // Handle feature interactions
  const onEachFeature = (feature, layer) => {
    const props = feature.properties;
    
    // Popup content
    let popupContent = '<div style="color: #1a1f2e; font-family: Archivo; padding: 5px;">';
    popupContent += `<h3 style="color: #00f5ff; margin: 0 0 10px 0; font-size: 1.2em;">${props.region_name}</h3>`;
    popupContent += `<div style="font-size: 0.95em;">`;
    popupContent += `<div style="margin-bottom: 5px;"><strong>Population:</strong> ${Math.round(props.population).toLocaleString()}</div>`;
    popupContent += `<div><strong>Jobs:</strong> ${Math.round(props.tot_jobs).toLocaleString()}</div>`;
    popupContent += `</div></div>`;
    
    layer.bindPopup(popupContent);
    
    // Hover effects
    layer.on({
      mouseover: (e) => {
        const layer = e.target;
        layer.setStyle({
          weight: 4,
          color: colorMode === 'population' ? '#00f5ff' : '#ff6b35',
          fillOpacity: 0.9,
        });
        
        // Show tooltip
        layer.bindTooltip(`<strong>${props.region_name}</strong><br/>${colorMode === 'population' ? 'Population' : 'Jobs'}: ${Math.round(colorMode === 'population' ? props.population : props.tot_jobs).toLocaleString()}`, {
          permanent: false,
          sticky: true
        }).openTooltip();
      },
      mouseout: (e) => {
        const layer = e.target;
        layer.setStyle(styleFeature(feature));
        layer.closeTooltip();
      },
    });
  };

  const StatCard = ({ icon: Icon, label, value, sublabel, color }) => (
    <motion.div
      className="stat-card"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
    >
      <div className="stat-icon" style={{ background: color }}>
        <Icon size={24} />
      </div>
      <div className="stat-content">
        <p className="stat-label">{label}</p>
        <h3 className="stat-value">{value}</h3>
        {sublabel && <p className="stat-sublabel">{sublabel}</p>}
      </div>
    </motion.div>
  );

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner" />
        <p>Loading demographics data...</p>
      </div>
    );
  }

  const currentStats = colorMode === 'population' ? stats?.population : stats?.jobs;
  const currentLabel = colorMode === 'population' ? 'Population' : 'Jobs';
  const currentColor = colorMode === 'population' ? 'rgba(0, 245, 255, 0.2)' : 'rgba(255, 107, 53, 0.2)';

  return (
    <div className="demographics-page">
      <motion.div
        className="page-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div>
          <h1>Regional Demographics</h1>
          <p>Population and employment data visualization by region</p>
        </div>

        <div className="controls">
          <div className="control-group">
            <label>Region Level</label>
            <div className="button-group">
              {['micro', 'meso', 'macro'].map((type) => (
                <button
                  key={type}
                  className={`control-button ${regionType === type ? 'active' : ''}`}
                  onClick={() => setRegionType(type)}
                >
                  <Layers size={16} />
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
            </div>
          </div>

          <div className="control-group">
            <label>Color By</label>
            <div className="button-group">
              <button
                className={`control-button ${colorMode === 'population' ? 'active' : ''} mode-population`}
                onClick={() => setColorMode('population')}
              >
                <Users size={16} />
                Population
              </button>
              <button
                className={`control-button ${colorMode === 'jobs' ? 'active' : ''} mode-jobs`}
                onClick={() => setColorMode('jobs')}
              >
                <Briefcase size={16} />
                Jobs
              </button>
            </div>
          </div>
        </div>
      </motion.div>

      {stats && (
        <div className="stats-grid">
          <StatCard
            icon={Layers}
            label="Total Regions"
            value={stats.total_zones?.toLocaleString()}
            sublabel={`${regionType} level`}
            color="rgba(168, 85, 247, 0.2)"
          />
          <StatCard
            icon={colorMode === 'population' ? Users : Briefcase}
            label={`Total ${currentLabel}`}
            value={currentStats?.total?.toLocaleString()}
            sublabel={`Avg: ${Math.round(currentStats?.mean).toLocaleString()}`}
            color={currentColor}
          />
          <StatCard
            icon={colorMode === 'population' ? Users : Briefcase}
            label={`Max ${currentLabel}`}
            value={Math.round(currentStats?.max).toLocaleString()}
            sublabel={`Min: ${Math.round(currentStats?.min).toLocaleString()}`}
            color={currentColor}
          />
        </div>
      )}

      <motion.div
        className="map-container"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
      >
        {geoData && geoData.features ? (
          <MapContainer
            center={[40.4093, 49.8671]}
            zoom={10}
            style={{ height: '100%', width: '100%', borderRadius: '12px' }}
          >
            <TileLayer
              attribution='&copy; OpenStreetMap'
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />
            <GeoJSON
              key={geoJsonKey}
              data={geoData}
              style={styleFeature}
              onEachFeature={onEachFeature}
            />
          </MapContainer>
        ) : (
          <div className="error-state">
            <p>No demographic data available</p>
            <button className="reload-button" onClick={loadData}>
              Retry
            </button>
          </div>
        )}
      </motion.div>

      <div className="legend">
        <h4>Legend: {currentLabel}</h4>
        <div className="legend-items">
          <div className="legend-item">
            <div className={`legend-gradient-bar ${colorMode === 'population' ? 'population-gradient' : 'jobs-gradient'}`}></div>
            <div className="legend-labels">
              <span>Low</span>
              <span>High</span>
            </div>
          </div>
          {currentStats && (
            <div className="legend-values">
              <span>Min: {Math.round(currentStats.min).toLocaleString()}</span>
              <span>Max: {Math.round(currentStats.max).toLocaleString()}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Demographics;
