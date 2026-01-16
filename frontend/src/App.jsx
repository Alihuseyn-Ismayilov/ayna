import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Demographics from './pages/Demographics';
import BusAnalytics from './pages/BusAnalytics';
import LiveRoutes from './pages/LiveRoutes';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Demographics />} />
          <Route path="/bus-analytics" element={<BusAnalytics />} />
          <Route path="/live-routes" element={<LiveRoutes />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
