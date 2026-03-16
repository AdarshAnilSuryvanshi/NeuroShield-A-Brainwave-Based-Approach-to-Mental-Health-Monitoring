import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import './Navbar.css';

const NAV_LINKS = [
  { path: '/dashboard', label: 'Dashboard', icon: '⬡' },
  { path: '/upload', label: 'Upload EEG', icon: '↑' },
  { path: '/visualization', label: 'Visualize', icon: '◈' },
  { path: '/chatbot', label: 'AI Chat', icon: '◎' },
  { path: '/report', label: 'Report', icon: '≡' },
];

export default function Navbar() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/dashboard" className="navbar-brand">
          <div className="brand-icon">
            <span className="brand-wave" />
            <span className="brand-wave" />
            <span className="brand-wave" />
          </div>
          <span className="brand-name">NeuroShield</span>
        </Link>

        <div className={`navbar-links ${menuOpen ? 'open' : ''}`}>
          {NAV_LINKS.map(({ path, label, icon }) => (
            <Link
              key={path}
              to={path}
              className={`nav-link ${location.pathname === path ? 'active' : ''}`}
              onClick={() => setMenuOpen(false)}
            >
              <span className="nav-icon">{icon}</span>
              <span>{label}</span>
            </Link>
          ))}
        </div>

        <div className="navbar-right">
          {user && (
            <div className="user-chip">
              <div className="user-avatar">{(user.name || user.email || 'U')[0].toUpperCase()}</div>
              <span className="user-name">{user.name || user.email || 'User'}</span>
            </div>
          )}
          <button className="btn btn-ghost btn-sm" onClick={handleLogout}>Logout</button>
          <button className={`hamburger ${menuOpen ? 'open' : ''}`} onClick={() => setMenuOpen(!menuOpen)}>
            <span /><span /><span />
          </button>
        </div>
      </div>
    </nav>
  );
}
