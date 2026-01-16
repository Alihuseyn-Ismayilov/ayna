import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { ArrowUpDown, ArrowUp, ArrowDown, Download } from 'lucide-react';
import './BusAnalytics.css';

const BusAnalytics = () => {
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState(null);
  const [tableData, setTableData] = useState([]);
  const [filteredTableData, setFilteredTableData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  
  const [filters, setFilters] = useState({
    dateStart: '',
    dateEnd: '',
    hourStart: '',
    hourEnd: '',
    company: '',
    route: ''
  });

  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  useEffect(() => {
    loadAnalytics();
    loadTableData();
  }, [filters]);

  useEffect(() => {
    filterAndSortTable();
  }, [tableData, searchTerm, sortConfig]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      
      const params = new URLSearchParams();
      if (filters.dateStart) params.append('start_date', filters.dateStart);
      if (filters.dateEnd) params.append('end_date', filters.dateEnd);
      if (filters.hourStart) params.append('hour_start', filters.hourStart);
      if (filters.hourEnd) params.append('hour_end', filters.hourEnd);
      if (filters.company) params.append('companies', filters.company);
      if (filters.route) params.append('routes', filters.route);
      
      const response = await fetch(`http://localhost:8000/api/bus/analytics?${params}`);
      const data = await response.json();
      setAnalytics(data);
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTableData = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.company) params.append('operator', filters.company);
      if (filters.route) params.append('route', filters.route);
      if (filters.dateStart) params.append('start_date', filters.dateStart);
      if (filters.dateEnd) params.append('end_date', filters.dateEnd);
      
      const response = await fetch(`http://localhost:8000/api/bus/registrations?limit=10000&${params}`);
      const data = await response.json();
      setTableData(data.data || []);
    } catch (error) {
      console.error('Error loading table data:', error);
    }
  };

  const filterAndSortTable = () => {
    let filtered = [...tableData];

    if (filters.hourStart) {
      filtered = filtered.filter(row => row.Hour >= parseInt(filters.hourStart));
    }
    if (filters.hourEnd) {
      filtered = filtered.filter(row => row.Hour <= parseInt(filters.hourEnd));
    }

    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(row => 
        row.Route?.toString().toLowerCase().includes(term) ||
        row.Operator?.toLowerCase().includes(term)
      );
    }

    if (sortConfig.key) {
      filtered.sort((a, b) => {
        let aVal = a[sortConfig.key];
        let bVal = b[sortConfig.key];

        if (sortConfig.key === 'pass_per_bus') {
          aVal = a['Total Count'] / a['Number Of Busses'];
          bVal = b['Total Count'] / b['Number Of Busses'];
        }

        if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }

    setFilteredTableData(filtered);
  };

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const SortIcon = ({ columnKey }) => {
    if (sortConfig.key !== columnKey) {
      return <ArrowUpDown size={14} className="sort-icon" />;
    }
    return sortConfig.direction === 'asc' ? 
      <ArrowUp size={14} className="sort-icon active" /> : 
      <ArrowDown size={14} className="sort-icon active" />;
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const resetFilters = () => {
    setFilters({
      dateStart: '',
      dateEnd: '',
      hourStart: '',
      hourEnd: '',
      company: '',
      route: ''
    });
  };

  const exportData = () => {
    const csv = [
      ['Date', 'Hour', 'Route', 'Passengers', 'SmartCard', 'QR', 'Buses', 'Company', 'Pass/Bus'],
      ...filteredTableData.map(row => [
        row.Date?.split('T')[0],
        row.Hour,
        row.Route,
        row['Total Count'],
        row['By SmartCard'],
        row['By QR'],
        row['Number Of Busses'],
        row.Operator,
        (row['Total Count'] / row['Number Of Busses']).toFixed(1)
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'bus_analytics.csv';
    a.click();
  };

  if (loading || !analytics) {
    return (
      <div className="loading-container">
        <div className="spinner" />
        <p>Loading bus analytics...</p>
      </div>
    );
  }

  const { kpis, by_company, by_hour, top_routes, bottom_routes, dropdowns } = analytics;
  const COLORS = ['#00f5ff', '#ff6b35', '#00ff9f', '#ffd93d', '#ff495c', '#a855f7'];

  // Calculate top companies by pass/bus
  const topCompaniesByEfficiency = [...by_company]
    .sort((a, b) => b.pass_per_bus - a.pass_per_bus)
    .slice(0, 10);

  // Calculate top companies by QR usage percentage
  const topCompaniesByQR = [...by_company]
    .map(c => ({
      ...c,
      qr_percentage: (c['By QR'] / c['Total Count'] * 100).toFixed(1)
    }))
    .sort((a, b) => b.qr_percentage - a.qr_percentage)
    .slice(0, 10);

  return (
    <div className="bus-analytics-page">
      <motion.div
        className="page-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div>
          <h1>BUS ANALYTICS</h1>
          <p>Comprehensive analysis of bus operations and passenger data</p>
        </div>
        <button onClick={exportData} className="export-button">
          <Download size={18} />
          Export Data
        </button>
      </motion.div>

      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-value">{kpis.total_passengers.toLocaleString()}</div>
          <div className="kpi-label">TOTAL PASSENGERS</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-value">{kpis.total_buses.toLocaleString()}</div>
          <div className="kpi-label">TOTAL BUSES</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-value">{kpis.avg_pass_per_bus}</div>
          <div className="kpi-label">AVG PASS/BUS</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-value">{kpis.peak_hour}:00</div>
          <div className="kpi-label">PEAK HOUR</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-value">{kpis.most_efficient_company}</div>
          <div className="kpi-label">MOST EFFICIENT</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-value">{kpis.payment_leader}</div>
          <div className="kpi-label">PAYMENT LEADER</div>
        </div>
      </div>

      <div className="section-card filters-section">
        <h2>🔍 GLOBAL FILTERS</h2>
        <div className="filters-grid">
          <div className="filter-group">
            <label>Date Start</label>
            <select value={filters.dateStart} onChange={(e) => handleFilterChange('dateStart', e.target.value)}>
              <option value="">All Dates</option>
              {dropdowns.dates.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
          <div className="filter-group">
            <label>Date End</label>
            <select value={filters.dateEnd} onChange={(e) => handleFilterChange('dateEnd', e.target.value)}>
              <option value="">All Dates</option>
              {dropdowns.dates.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
          <div className="filter-group">
            <label>Hour Start</label>
            <select value={filters.hourStart} onChange={(e) => handleFilterChange('hourStart', e.target.value)}>
              <option value="">All Hours</option>
              {dropdowns.hours.map(h => <option key={h} value={h}>{h}:00</option>)}
            </select>
          </div>
          <div className="filter-group">
            <label>Hour End</label>
            <select value={filters.hourEnd} onChange={(e) => handleFilterChange('hourEnd', e.target.value)}>
              <option value="">All Hours</option>
              {dropdowns.hours.map(h => <option key={h} value={h}>{h}:00</option>)}
            </select>
          </div>
          <div className="filter-group">
            <label>Company</label>
            <select value={filters.company} onChange={(e) => handleFilterChange('company', e.target.value)}>
              <option value="">All Companies</option>
              {dropdowns.companies.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div className="filter-group">
            <label>Route</label>
            <select value={filters.route} onChange={(e) => handleFilterChange('route', e.target.value)}>
              <option value="">All Routes</option>
              {dropdowns.routes.map(r => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
        </div>
        <button onClick={resetFilters} className="reset-button">Reset All Filters</button>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>📊 Top 10 Companies by Efficiency (Pass/Bus)</h3>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={topCompaniesByEfficiency} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis type="number" stroke="#a8b2d1" />
              <YAxis type="category" dataKey="Operator" stroke="#a8b2d1" width={100} />
              <Tooltip 
                contentStyle={{ background: '#1a1f2e', border: '1px solid #00f5ff' }}
                labelStyle={{ color: '#00f5ff' }}
              />
              <Bar dataKey="pass_per_bus" fill="#00f5ff" name="Pass/Bus" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>📱 Top 10 Companies by QR Usage (%)</h3>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={topCompaniesByQR} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis type="number" stroke="#a8b2d1" />
              <YAxis type="category" dataKey="Operator" stroke="#a8b2d1" width={100} />
              <Tooltip 
                contentStyle={{ background: '#1a1f2e', border: '1px solid #00f5ff' }}
                labelStyle={{ color: '#00f5ff' }}
              />
              <Bar dataKey="qr_percentage" fill="#ffd93d" name="QR Usage %" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card chart-wide">
          <h3>📈 Hourly Passenger Count</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={by_hour}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="Hour" stroke="#a8b2d1" label={{ value: 'Hour of Day', position: 'insideBottom', offset: -5 }} />
              <YAxis stroke="#a8b2d1" width={80} />
              <Tooltip 
                contentStyle={{ background: '#1a1f2e', border: '1px solid #00f5ff' }}
                labelStyle={{ color: '#00f5ff' }}
              />
              <Legend />
              <Line type="monotone" dataKey="Total Count" stroke="#00f5ff" strokeWidth={3} name="Total Passengers" dot={{ fill: '#00f5ff', r: 4 }} />
              <Line type="monotone" dataKey="By SmartCard" stroke="#00ff9f" strokeWidth={2} name="SmartCard" />
              <Line type="monotone" dataKey="By QR" stroke="#ffd93d" strokeWidth={2} name="QR" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card chart-wide">
          <h3>🚌 Hourly Passengers per Bus</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={by_hour}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="Hour" stroke="#a8b2d1" label={{ value: 'Hour of Day', position: 'insideBottom', offset: -5 }} />
              <YAxis stroke="#a8b2d1" width={80} />
              <Tooltip 
                contentStyle={{ background: '#1a1f2e', border: '1px solid #00f5ff' }}
                labelStyle={{ color: '#00f5ff' }}
              />
              <Line type="monotone" dataKey="pass_per_bus" stroke="#ff6b35" strokeWidth={3} name="Pass/Bus" dot={{ fill: '#ff6b35', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>🏆 Top 15 Routes by Ridership</h3>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={top_routes} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis type="number" stroke="#a8b2d1" />
              <YAxis type="category" dataKey="Route" stroke="#a8b2d1" width={60} />
              <Tooltip 
                contentStyle={{ background: '#1a1f2e', border: '1px solid #00f5ff' }}
                labelStyle={{ color: '#00f5ff' }}
              />
              <Bar dataKey="Total Count" fill="#00ff9f" name="Passengers" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>💳 Payment Methods Distribution</h3>
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={[
                  { name: 'SmartCard', value: by_company.reduce((sum, c) => sum + c['By SmartCard'], 0) },
                  { name: 'QR', value: by_company.reduce((sum, c) => sum + c['By QR'], 0) }
                ]}
                cx="50%"
                cy="50%"
                labelLine={true}
                label={(entry) => `${entry.name}: ${entry.value.toLocaleString()}`}
                outerRadius={120}
                dataKey="value"
              >
                {[0, 1].map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ background: '#1a1f2e', border: '1px solid #00f5ff' }}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="section-card">
        <h2>📋 DETAILED DATA TABLE</h2>
        
        <div className="table-filters">
          <input
            type="text"
            placeholder="Search by route or company..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <div className="table-info">
            Showing {filteredTableData.length.toLocaleString()} records
          </div>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th onClick={() => handleSort('Date')}>
                  <div className="th-content">Date <SortIcon columnKey="Date" /></div>
                </th>
                <th onClick={() => handleSort('Hour')}>
                  <div className="th-content">Hour <SortIcon columnKey="Hour" /></div>
                </th>
                <th onClick={() => handleSort('Route')}>
                  <div className="th-content">Route <SortIcon columnKey="Route" /></div>
                </th>
                <th onClick={() => handleSort('Total Count')}>
                  <div className="th-content">Passengers <SortIcon columnKey="Total Count" /></div>
                </th>
                <th onClick={() => handleSort('By SmartCard')}>
                  <div className="th-content">SmartCard <SortIcon columnKey="By SmartCard" /></div>
                </th>
                <th onClick={() => handleSort('By QR')}>
                  <div className="th-content">QR <SortIcon columnKey="By QR" /></div>
                </th>
                <th onClick={() => handleSort('Number Of Busses')}>
                  <div className="th-content">Buses <SortIcon columnKey="Number Of Busses" /></div>
                </th>
                <th onClick={() => handleSort('Operator')}>
                  <div className="th-content">Company <SortIcon columnKey="Operator" /></div>
                </th>
                <th onClick={() => handleSort('pass_per_bus')}>
                  <div className="th-content">Pass/Bus <SortIcon columnKey="pass_per_bus" /></div>
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredTableData.slice(0, 100).map((row, idx) => {
                const passPerBus = row['Total Count'] / row['Number Of Busses'];
                return (
                  <tr key={idx}>
                    <td>{row.Date?.split('T')[0]}</td>
                    <td>{row.Hour}:00</td>
                    <td>{row.Route}</td>
                    <td>{row['Total Count'].toLocaleString()}</td>
                    <td>{row['By SmartCard'].toLocaleString()}</td>
                    <td>{row['By QR'].toLocaleString()}</td>
                    <td>{row['Number Of Busses']}</td>
                    <td>{row.Operator}</td>
                    <td>{passPerBus.toFixed(1)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div className="section-card">
        <h2>⚠️ BOTTOM 5 UNDERUTILIZED ROUTES</h2>
        <p className="section-description">Routes with lowest passengers per bus - optimization opportunities</p>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Route</th>
                <th>Current Buses</th>
                <th>Total Passengers</th>
                <th>Pass/Bus Ratio</th>
                <th>Suggested Reduction</th>
                <th>New Pass/Bus</th>
              </tr>
            </thead>
            <tbody>
              {bottom_routes.map((route) => {
                const reduction = Math.ceil(route['Number Of Busses'] * 0.3);
                const newBuses = route['Number Of Busses'] - reduction;
                const newRatio = newBuses > 0 ? route['Total Count'] / newBuses : 0;
                return (
                  <tr key={route.Route}>
                    <td><strong>{route.Route}</strong></td>
                    <td>{route['Number Of Busses']}</td>
                    <td>{route['Total Count'].toLocaleString()}</td>
                    <td>{route.pass_per_bus.toFixed(1)}</td>
                    <td className="highlight-warning">{reduction} buses (-30%)</td>
                    <td className="highlight-success">{newRatio.toFixed(1)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default BusAnalytics;
