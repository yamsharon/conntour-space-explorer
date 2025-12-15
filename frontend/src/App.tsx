import React from 'react';
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import BrowsePage from './pages/BrowsePage';
import SearchPage from './pages/SearchPage';
import HistoryPage from './pages/HistoryPage';
import Layout from './components/Layout';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-100">
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<BrowsePage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/history" element={<HistoryPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
};

export default App; 