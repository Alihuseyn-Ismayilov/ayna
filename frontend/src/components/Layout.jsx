import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Map, BarChart3, Radio, Activity } from 'lucide-react';
import { utilAPI } from '../services/api';
import './Layout.css';

const Layout = ({ children }) => {
  const location = useLocation();
  const [healthStatus, setHealthStatus] = useState(null);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    try {
      const response = await utilAPI.health();
      setHealthStatus(response.data);
    } catch (error) {
      setHealthStatus({ status: 'error' });
    }
  };

  const navItems = [
    { path: '/', label: 'Demographics', icon: Map },
    { path: '/bus-analytics', label: 'Bus Analytics', icon: BarChart3 },
    { path: '/live-routes', label: 'Live Routes', icon: Radio },
  ];

  return (
    <div className="layout">
      <nav className="sidebar">
        <div className="sidebar-header">
          <div className="logo">
            <Activity size={32} strokeWidth={2} />
            <div>
              <h1>Transit</h1>
              <span>Analytics Hub</span>
            </div>
          </div>
          <div className="health-indicator">
            <div className={`status-dot ${healthStatus?.status === 'healthy' ? 'active' : 'error'}`} />
            <span>{healthStatus?.status === 'healthy' ? 'Online' : 'Offline'}</span>
          </div>
        </div>

        <div className="nav-items">
          {navItems.map((item, index) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-item ${isActive ? 'active' : ''}`}
              >
                <motion.div
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="nav-item-content"
                >
                  <Icon size={20} />
                  <span>{item.label}</span>
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="active-indicator"
                      transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    />
                  )}
                </motion.div>
              </Link>
            );
          })}
        </div>

        <div className="sidebar-footer">
          <div className="footer-info">
            <p>Transportation Analytics</p>
            <p className="version">v1.0.0</p>
          </div>
        </div>
      </nav>

      <main className="main-content">
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
          className="page-motion-wrapper"
        >
          {children}
        </motion.div>
      </main>
    </div>
  );
};

export default Layout;
