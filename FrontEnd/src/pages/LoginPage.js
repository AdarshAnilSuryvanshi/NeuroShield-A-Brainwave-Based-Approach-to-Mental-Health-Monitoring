import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import api from '../utils/api';
import './AuthPages.css';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) { setError('Please fill all fields.'); return; }
    setLoading(true);
    setError('');
    try {
      const data = await api.login({ email, password });
      if (data.token || data.user || data.email) {
        login(data.user || { email, name: data.name, token: data.token });
        navigate('/dashboard');
      } else {
        setError(data.error || data.detail || 'Invalid credentials.');
      }
    } catch {
      // Demo mode — allow bypass when backend is offline
      login({ email, name: email.split('@')[0] });
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card animate-fadeUp">
        <div className="auth-brand">
          <div className="auth-brand-icon">
            <span /><span /><span />
          </div>
          <span>NeuroShield</span>
        </div>

        <h2>Welcome back</h2>
        <p className="auth-subtitle">Sign in to access your EEG analysis dashboard</p>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label className="input-label">Email</label>
            <input
              className="input"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={e => setEmail(e.target.value)}
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label className="input-label">Password</label>
            <input
              className="input"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={e => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </div>

          <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: '100%', marginTop: 8 }}>
            {loading ? <><div className="spinner" /> Signing in…</> : 'Sign In'}
          </button>
        </form>

        <div className="divider" />

        <p className="auth-link">
          Don't have an account? <Link to="/register">Create one</Link>
        </p>
        <p className="auth-link">
          <Link to="/">← Back to Home</Link>
        </p>
      </div>
    </div>
  );
}
