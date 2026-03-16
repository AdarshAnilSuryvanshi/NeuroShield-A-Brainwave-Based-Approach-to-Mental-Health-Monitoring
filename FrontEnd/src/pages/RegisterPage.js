import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import api from '../utils/api';
import './AuthPages.css';

export default function RegisterPage() {
  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const set = (key) => (e) => setForm(f => ({ ...f, [key]: e.target.value }));

  const validate = () => {
    if (!form.name) return 'Name is required.';
    if (!form.email.includes('@')) return 'Enter a valid email.';
    if (form.password.length < 6) return 'Password must be at least 6 characters.';
    if (form.password !== form.confirm) return 'Passwords do not match.';
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const err = validate();
    if (err) { setError(err); return; }
    setLoading(true);
    setError('');
    try {
      const data = await api.register({ name: form.name, email: form.email, password: form.password });
      if (data.token || data.user || data.email) {
        login(data.user || { email: form.email, name: form.name, token: data.token });
        navigate('/dashboard');
      } else {
        setError(data.error || data.detail || 'Registration failed.');
      }
    } catch {
      // Demo mode
      login({ email: form.email, name: form.name });
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card animate-fadeUp" style={{ maxWidth: 440 }}>
        <div className="auth-brand">
          <div className="auth-brand-icon"><span /><span /><span /></div>
          <span>NeuroShield</span>
        </div>

        <h2>Create account</h2>
        <p className="auth-subtitle">Start monitoring your brain health today</p>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label className="input-label">Full Name</label>
            <input className="input" type="text" placeholder="Adarsh Suryvanshi" value={form.name} onChange={set('name')} />
          </div>
          <div className="form-group">
            <label className="input-label">Email</label>
            <input className="input" type="email" placeholder="you@example.com" value={form.email} onChange={set('email')} />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label className="input-label">Password</label>
              <input className="input" type="password" placeholder="Min 6 chars" value={form.password} onChange={set('password')} />
            </div>
            <div className="form-group">
              <label className="input-label">Confirm</label>
              <input className="input" type="password" placeholder="Repeat password" value={form.confirm} onChange={set('confirm')} />
            </div>
          </div>

          <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: '100%', marginTop: 8 }}>
            {loading ? <><div className="spinner" /> Creating…</> : 'Create Account'}
          </button>
        </form>

        <div className="divider" />
        <p className="auth-link">Already have an account? <Link to="/login">Sign in</Link></p>
        <p className="auth-link"><Link to="/">← Back to Home</Link></p>
      </div>
    </div>
  );
}
