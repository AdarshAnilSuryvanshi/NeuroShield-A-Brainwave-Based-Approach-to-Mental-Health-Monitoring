import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../App';
import api from '../utils/api';
import './Dashboard.css';

const QUICK_ACTIONS = [
  { to: '/upload', icon: '↑', label: 'Upload EEG', desc: 'Analyze a new EDF file', color: 'primary' },
  { to: '/visualization', icon: '◈', label: 'Visualize', desc: 'View brainwave signals', color: 'accent' },
  { to: '/chatbot', icon: '◎', label: 'AI Chat', desc: 'Ask about your EEG data', color: 'warn' },
  { to: '/report', icon: '≡', label: 'Report', desc: 'Mental health summary', color: 'primary' },
]; 

export default function Dashboard() {
  const { user } = useAuth();
  const [uploads, setUploads] = useState([]);
  const [loading, setLoading] = useState(true);
  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';

  useEffect(() => {
    api.getUserUploads()
      .then(data => setUploads(Array.isArray(data) ? data : data.results || []))
      .catch(() => setUploads([]))
      .finally(() => setLoading(false));
  }, []);

  const lastUpload = uploads[uploads.length - 1];

  return (
    <div className="dashboard-page page-container">
      {/* Header */}
      <div className="dash-header animate-fadeUp">
        <div>
          <p className="dash-greeting">{greeting},</p>
          <h1>{user?.name || user?.email || 'Researcher'} 👋</h1>
          <p className="dash-sub">Here's your NeuroShield overview</p>
        </div>
        <div className="dash-status">
          <div className="pulse-dot" />
          <span>System Active</span>
        </div>
      </div>

      {/* Stats row */}
      <div className="dash-stats animate-fadeUp" style={{ animationDelay: '0.1s' }}>
        {[
          { label: 'Total Uploads', value: loading ? '…' : uploads.length, icon: '↑', unit: 'files' },
          { label: 'Analyses Done', value: loading ? '…' : uploads.filter(u => u.status === 'completed').length, icon: '⬡', unit: 'results' },
          { label: 'Latest Prediction', value: lastUpload?.predicted_label ?? '—', icon: '◎', unit: lastUpload ? 'result' : '' },
          { label: 'Confidence', value: lastUpload?.probability ? `${(lastUpload.probability * 100).toFixed(1)}%` : '—', icon: '◈', unit: '' },
        ].map(({ label, value, icon, unit }) => (
          <div key={label} className="stat-card">
            <div className="stat-card-icon">{icon}</div>
            <div className="stat-card-body">
              <div className="stat-card-val">{value} <span className="stat-card-unit">{unit}</span></div>
              <div className="stat-card-label">{label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick actions */}
      <div className="animate-fadeUp" style={{ animationDelay: '0.2s' }}>
        <h3 className="section-title">Quick Actions</h3>
        <div className="quick-actions">
          {QUICK_ACTIONS.map(({ to, icon, label, desc, color }) => (
            <Link key={to} to={to} className={`action-card action-card--${color}`}>
              <div className="action-icon">{icon}</div>
              <div>
                <div className="action-label">{label}</div>
                <div className="action-desc">{desc}</div>
              </div>
              <span className="action-arrow">→</span>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent uploads */}
      <div className="animate-fadeUp" style={{ animationDelay: '0.3s' }}>
        <h3 className="section-title">Recent EEG Uploads</h3>
        <div className="card">
          {loading ? (
            <div className="dash-loading"><div className="spinner" /> Loading uploads…</div>
          ) : uploads.length === 0 ? (
            <div className="dash-empty">
              <div className="empty-icon">◈</div>
              <p>No EEG uploads yet.</p>
              <Link to="/upload" className="btn btn-primary" style={{ marginTop: 8 }}>Upload your first EEG →</Link>
            </div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>File</th>
                  <th>Status</th>
                  <th>Prediction</th>
                  <th>Confidence</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {[...uploads].reverse().slice(0, 8).map((u, i) => (
                  <tr key={u.id || i}>
                    <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{u.file_name || u.edf_file || `Upload #${u.id}`}</td>
                    <td>
                      <span className={`badge ${u.status === 'completed' ? 'badge-success' : u.status === 'failed' ? 'badge-danger' : 'badge-warning'}`}>
                        {u.status || 'pending'}
                      </span>
                    </td>
                    <td>{u.predicted_label ?? '—'}</td>
                    <td>{u.probability ? `${(u.probability * 100).toFixed(1)}%` : '—'}</td>
                    <td>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <Link to="/visualization" className="btn btn-ghost" style={{ padding: '4px 10px', fontSize: 12 }}>View</Link>
                        <Link to="/report" className="btn btn-ghost" style={{ padding: '4px 10px', fontSize: 12 }}>Report</Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
