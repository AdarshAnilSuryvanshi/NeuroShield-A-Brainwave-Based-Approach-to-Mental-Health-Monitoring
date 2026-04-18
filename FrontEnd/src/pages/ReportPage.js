import React, { useState } from 'react';
import {
  RadialBarChart, RadialBar, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell
} from 'recharts';
import api from '../utils/api';
import './ReportPage.css';

const COLORS = ['#6c4ae3', '#00e5c8', '#f7c948', '#ff4d6d', '#9b7ef8'];

export default function ReportPage() {
  const [uploadId, setUploadId] = useState('');
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchReport = async () => {
    if (!uploadId.trim()) { setError('Enter an upload ID'); return; }
    setLoading(true); setError(''); setReport(null);
    try {
      const data = await api.getReport(uploadId);
      if (data.error || data.detail) {
        setError(data.error || data.detail);
      } else {
        setReport(data);
      }
    } catch {
      setError('Could not fetch report. Make sure the backend is running.');
    } finally { setLoading(false); }
  };

  const labelColor = (label) => {
    if (!label) return 'badge-primary';
    const l = String(label).toLowerCase();
    if (l.includes('normal') || l.includes('healthy')) return 'badge-success';
    if (l.includes('mild') || l.includes('moderate')) return 'badge-warning';
    return 'badge-danger';
  };

  const prob = report?.probability ? parseFloat(report.probability) : null;
  const confidence = prob ? Math.round(prob * 100) : null;

  // Build chart data from features_summary
  const featureChartData = report?.features_summary && typeof report.features_summary === 'object'
    ? Object.entries(report.features_summary)
        .filter(([, v]) => typeof v === 'number' || !isNaN(parseFloat(v)))
        .slice(0, 8)
        .map(([key, val]) => ({ name: key.replace(/_/g, ' '), value: parseFloat(val) }))
    : [];

  const radialData = confidence ? [{ name: 'Confidence', value: confidence, fill: '#6c4ae3' }] : [];

  return (
    <div className="report-page page-container">
      {/* Header */}
      <div className="report-header animate-fadeUp">
        <div>
          <h2>Mental Health Report</h2>
          <p className="report-sub">Detailed analysis of your EEG scan</p>
        </div>
        <div className="report-fetch-row">
          <input
            className="input"
            placeholder="Upload ID"
            value={uploadId}
            onChange={e => setUploadId(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && fetchReport()}
            style={{ width: 180 }}
          />
          <button className="btn btn-primary" onClick={fetchReport} disabled={loading}>
            {loading ? <><div className="spinner" /> Loading…</> : 'Load Report'}
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error animate-fadeUp">{error}</div>}

      {!report && !loading && !error && (
        <div className="report-empty animate-fadeUp">
          <div className="empty-big-icon">≡</div>
          <h3>No report loaded</h3>
          <p>Enter your Upload ID and press "Load Report" to see the full mental health analysis.</p>
        </div>
      )}

      {report && (
        <div className="report-body animate-fadeUp">
          {/* Summary banner */}
          <div className="report-banner">
            <div className="banner-left">
              <div className="banner-label">File Analyzed</div>
              <div className="banner-file">{report.file_name || report.edf_file || `Upload #${uploadId}`}</div>
              <div className="banner-meta">
                <span className={`badge ${report.status === 'completed' ? 'badge-success' : 'badge-warning'}`}>
                  {report.status || 'completed'}
                </span>
                {report.created_at && <span className="banner-date">{new Date(report.created_at).toLocaleString()}</span>}
              </div>
            </div>
            <div className="banner-right">
              <div className="banner-label">Prediction</div>
              <div className={`badge ${labelColor(report.predicted_label)} banner-prediction`}>
                {report.predicted_label ?? 'N/A'}
              </div>
            </div>
          </div>

          {/* Key metrics */}
          <div className="report-metrics">
            {/* Confidence radial */}
            {confidence !== null && (
              <div className="card metric-card">
                <div className="metric-label">Model Confidence</div>
                <div className="radial-wrap">
                  <ResponsiveContainer width="100%" height={160}>
                    <RadialBarChart cx="50%" cy="50%" innerRadius="60%" outerRadius="90%"
                      barSize={14} data={[{ value: confidence, fill: '#6c4ae3' }]} startAngle={90} endAngle={-270}>
                      <RadialBar background={{ fill: 'rgba(255,255,255,0.04)' }} dataKey="value" cornerRadius={8} />
                    </RadialBarChart>
                  </ResponsiveContainer>
                  <div className="radial-center">
                    <span className="radial-val">{confidence}%</span>
                    <span className="radial-sub">confidence</span>
                  </div>
                </div>
              </div>
            )}

            {/* Probability breakdown */}
            {report.class_probabilities && typeof report.class_probabilities === 'object' && (
              <div className="card metric-card metric-card--wide">
                <div className="metric-label">Class Probabilities</div>
                <ResponsiveContainer width="100%" height={160}>
                  <BarChart data={Object.entries(report.class_probabilities).map(([k, v]) => ({ name: k, prob: parseFloat(v) }))}
                    margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
                    <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#8a8faa' }} />
                    <YAxis domain={[0, 1]} tick={{ fontSize: 10, fill: '#4a4f66' }} />
                    <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', fontSize: 12 }} />
                    <Bar dataKey="prob" radius={[4, 4, 0, 0]}>
                      {Object.keys(report.class_probabilities).map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {/* Feature chart */}
          {featureChartData.length > 0 && (
            <div className="card">
              <div className="report-section-title">Extracted EEG Features</div>
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={featureChartData} margin={{ top: 10, right: 10, left: 0, bottom: 50 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
                  <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#8a8faa' }} angle={-30} textAnchor="end" />
                  <YAxis tick={{ fontSize: 10, fill: '#4a4f66' }} />
                  <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', fontSize: 12 }} />
                  <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                    {featureChartData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Features table */}
          {report.features_summary && (
            <div className="card">
              <div className="report-section-title">Feature Summary</div>
              <table className="data-table">
                <thead><tr><th>Feature</th><th>Value</th></tr></thead>
                <tbody>
                  {typeof report.features_summary === 'object'
                    ? Object.entries(report.features_summary).map(([k, v]) => (
                        <tr key={k}>
                          <td style={{ color: 'var(--text-primary)', textTransform: 'capitalize' }}>{k.replace(/_/g, ' ')}</td>
                          <td style={{ color: 'var(--accent)', fontWeight: 500 }}>
                            {typeof v === 'number' ? v.toFixed(6) : String(v)}
                          </td>
                        </tr>
                      ))
                    : <tr><td colSpan={2}>{String(report.features_summary)}</td></tr>
                  }
                </tbody>
              </table>
            </div>
          )}

          {/* Recommendations */}
          {report.recommendations && (
            <div className="card report-recs">
              <div className="report-section-title">Recommendations</div>
              <div className="recs-body">
                {Array.isArray(report.recommendations)
                  ? report.recommendations.map((r, i) => (
                      <div key={i} className="rec-item">
                        <div className="rec-num">{i + 1}</div>
                        <p>{r}</p>
                      </div>
                    ))
                  : <p style={{ color: 'var(--text-secondary)' }}>{String(report.recommendations)}</p>
                }
              </div>
            </div>
          )}

          {/* All raw fields */}
          <div className="card">
            <div className="report-section-title">Full JSON Response</div>
            <pre className="json-view">{JSON.stringify(report, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
