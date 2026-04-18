import React, { createContext, useContext, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Dashboard from './pages/Dashboard';
import UploadEEG from './pages/UploadEEG';
import VisualizationPage from './pages/VisualizationPage';
import ChatbotPage from './pages/ChatbotPage';
import ReportPage from './pages/ReportPage';
import Navbar from './components/Navbar';

// Auth context
export const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

function ProtectedRoute({ children }) {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" replace />;
}

export default function App() {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('ns_user')) || null; }
    catch { return null; }
  });

  const login = (userData) => {
    setUser(userData);
    localStorage.setItem('ns_user', JSON.stringify(userData));
  };
  const logout = () => {
    setUser(null);
    localStorage.removeItem('ns_user');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/dashboard" element={<ProtectedRoute><Navbar /><Dashboard /></ProtectedRoute>} />
          <Route path="/upload" element={<ProtectedRoute><Navbar /><UploadEEG /></ProtectedRoute>} />
          <Route path="/visualization" element={<ProtectedRoute><Navbar /><VisualizationPage /></ProtectedRoute>} />
          <Route path="/chatbot" element={<ProtectedRoute><Navbar /><ChatbotPage /></ProtectedRoute>} />
          <Route path="/report" element={<ProtectedRoute><Navbar /><ReportPage /></ProtectedRoute>} />
        </Routes>
      </BrowserRouter>
    </AuthContext.Provider>
  );
}
