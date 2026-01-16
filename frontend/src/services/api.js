import axios from 'axios';

const API_BASE_URL = 'https://ayna-dashboard.fly.dev';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Bus Analytics APIs
export const busAPI = {
  getRegistrations: (params = {}) => 
    api.get('/api/bus/registrations', { params }),
  
  getVolume: (params = {}) => 
    api.get('/api/bus/volume', { params }),
  
  getStats: () => 
    api.get('/api/bus/stats'),
  
  getRoutes: () => 
    api.get('/api/bus/routes'),
  
  getOperators: () => 
    api.get('/api/bus/operators'),
  
  getHourlyTrend: (params = {}) => 
    api.get('/api/bus/hourly-trend', { params }),
};

// Demographics APIs
export const demographicsAPI = {
  getData: (regionType, metric = 'both') => 
    api.get(`/api/demographics/${regionType}`, { params: { metric } }),
  
  getStats: (regionType) => 
    api.get(`/api/demographics/stats/${regionType}`),
};

// Routes APIs
export const routesAPI = {
  getLive: () => 
    api.get('/api/routes/live'),
  
  getCached: () => 
    api.get('/api/routes/cached'),
};

// Utility APIs
export const utilAPI = {
  health: () => 
    api.get('/health'),
  
  dateRange: () => 
    api.get('/api/date-range'),
  
  reloadData: () => 
    api.post('/api/reload-data'),
};

export default api;
