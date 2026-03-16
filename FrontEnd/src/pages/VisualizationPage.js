import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, RadarChart, Radar, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis
} from 'recharts';
import api from '../utils/api';
import './VisualizationPage.css';

const CHART_TABS = ['Brainwave', 'Band Power', 'Radar', 'Channels'];

// Demo data generator
const generateWave = (len = 120, freq = 1, amp = 1, noise = 0.2) =>
  Array.from({ length: len }, (_, i) => ({
    t: i,
    value: Math.sin(i * 0.08 * freq) * amp + (Math.random() - 0.5) * noise +
           Math.sin(i * 0.03 * freq) * amp * 0.4,
  }));

const DEMO_BAND = [
  { band: 'Delta (0-4 Hz)', power: 0.82, fill: '#ff4d6d' },
  { band: 'Theta (4-8 Hz)', power: 0.58, fill: '#f7c948' },
  { band: 'Alpha (8-13 Hz)', power: 0.91, fill: '#6c4ae3' },
  { band: 'Beta (13-30 Hz)', power: 0.64, fill: '#00e5c8' },
  { band: 'Gamma (30+)', power: 0.37, fill: '#9b7ef8' },
];

const DEMO_RADAR = [
  { subject: 'Alpha', A: 85, fullMark: 100 },
  { subject: 'Beta', A: 62, fullMark: 100 },
  { subject: 'Theta', A: 55, fullMark: 100 },
  { subject: 'Delta', A: 78, fullMark: 100 },
  { subject: 'Gamma', A: 33, fullMark: 100 },
];

const CHANNEL_COLORS = ['#6c4ae3', '#00e5c8', '#f7c948', '#ff4d6d', '#9b7ef8', '#3dd6f5', '#f97316'];

export default function VisualizationPage() {
  const [uploadId, setUploadId] = useState('');
  const [activeTab, setActiveTab] = useState('Brainwave');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [vizData, setVizData] = useState(null);
  const [waveData] = useState(() => generateWave(200, 1.2, 1, 0.3));

  const fetchViz = async () => {
    if (!uploadId) { setError('Enter an upload ID'); return; }
    setLoading(true); setError('');
    try {
      const data = await api.getVisualization(uploadId);
      setVizData(data);
    } catch {
      setError('Could not fetch visualization data.');
    } finally { setLoading(false); }
  };

  // Parse backend data into chart-friendly formats
  const bandData = vizData?.band_power
    ? Object.entries(vizData.band_power).map(([band, power]) => ({ band, power: parseFloat(power) }))
    : DEMO_BAND;

  const channelData = vizData?.channels
    ? vizData.channels[0]?.values?.map((v, i) => {
        const pt = { t: i };
        vizData.channels.forEach((ch, ci) => { pt[ch.name || `CH${ci+1}`] = ch.values[i]; });
        return pt;
      })
    : Array.from({ length: 120 }, (_, i) => ({
        t: i,
        ...Object.fromEntries(CHANNEL_COLORS.slice(0,4).map((_, ci) =>
          [`CH${ci+1}`, Math.sin(i * 0.07 * (ci+1)) * (1 - ci*0.15) + (Math.random()-0.5)*0.2]
        ))
      }));

  const radarData = vizData?.radar || DEMO_RADAR;

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload?.length) {
      return (
        <div className="chart-tooltip">
          <p className="tt-label">t = {label}</p>
          {payload.map((p, i) => (
            <p key={i} style={{ color: p.color }}>{p.name}: {typeof p.value === 'number' ? p.value.toFixed(4) : p.value}</p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="viz-page page-container">
      {/* Header + ID input */}
      <div className="viz-header animate-fadeUp">
        <div>
          <h2>EEG Visualization</h2>
          <p className="viz-sub">Interactive brainwave charts from your EEG analysis</p>
        </div>
        <div className="viz-id-row">
          <input
            className="input"
            placeholder="Upload ID (optional)"
            value={uploadId}
            onChange={e => setUploadId(e.target.value)}
            style={{ width: 180 }}
          />
          <button className="btn btn-primary" onClick={fetchViz} disabled={loading}>
            {loading ? <div className="spinner" /> : 'Load Data'}
          </button>
        </div>
      </div>

      {!vizData && (
        <div className="alert alert-info animate-fadeUp" style={{ animationDelay: '0.05s' }}>
          Showing demo data. Enter an Upload ID and click "Load Data" to visualize real EEG results.
        </div>
      )}
      {error && <div className="alert alert-error">{error}</div>}

      {/* Tabs */}
      <div className="chart-tabs animate-fadeUp" style={{ animationDelay: '0.1s' }}>
        {CHART_TABS.map(tab => (
          <button key={tab} className={`chart-tab ${activeTab === tab ? 'active' : ''}`} onClick={() => setActiveTab(tab)}>
            {tab}
          </button>
        ))}
      </div>

      {/* Chart area */}
      <div className="chart-card card animate-fadeUp" style={{ animationDelay: '0.15s' }}>
        {activeTab === 'Brainwave' && (
          <div className="chart-wrap">
            <div className="chart-title">Raw EEG Signal — Channel 1</div>
            <ResponsiveContainer width="100%" height={320}>
              <AreaChart data={waveData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="waveGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6c4ae3" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6c4ae3" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="t" tick={{ fontSize: 11, fill: '#4a4f66' }} />
                <YAxis tick={{ fontSize: 11, fill: '#4a4f66' }} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="value" stroke="#6c4ae3" strokeWidth={1.5}
                  fill="url(#waveGrad)" dot={false} name="μV" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}

        {activeTab === 'Band Power' && (
          <div className="chart-wrap">
            <div className="chart-title">Frequency Band Power Distribution</div>
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={bandData} margin={{ top: 10, right: 10, left: -10, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
                <XAxis dataKey="band" tick={{ fontSize: 11, fill: '#8a8faa' }} angle={-20} textAnchor="end" />
                <YAxis tick={{ fontSize: 11, fill: '#4a4f66' }} domain={[0, 1]} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="power" name="Power (norm.)" radius={[4, 4, 0, 0]}>
                  {bandData.map((entry, i) => (
                    <rect key={i} fill={entry.fill || CHANNEL_COLORS[i % CHANNEL_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            {/* Band legend */}
            <div className="band-legend">
              {bandData.map((b, i) => (
                <div key={b.band} className="band-item">
                  <div className="band-dot" style={{ background: b.fill || CHANNEL_COLORS[i] }} />
                  <div>
                    <div className="band-name">{b.band}</div>
                    <div className="band-val">{(b.power * 100).toFixed(1)}%</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'Radar' && (
          <div className="chart-wrap">
            <div className="chart-title">Brain Activity Radar — All Bands</div>
            <ResponsiveContainer width="100%" height={340}>
              <RadarChart data={radarData} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
                <PolarGrid stroke="rgba(255,255,255,0.08)" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#8a8faa', fontSize: 13 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#4a4f66', fontSize: 10 }} />
                <Radar name="Power %" dataKey="A" stroke="#6c4ae3" fill="#6c4ae3" fillOpacity={0.2} strokeWidth={2} />
                <Radar name="Max" dataKey="fullMark" stroke="rgba(0,229,200,0.2)" fill="none" strokeDasharray="3 3" />
                <Legend wrapperStyle={{ color: '#8a8faa', fontSize: 12 }} />
                <Tooltip content={<CustomTooltip />} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        )}

        {activeTab === 'Channels' && (
          <div className="chart-wrap">
            <div className="chart-title">Multi-Channel EEG Overview</div>
            <ResponsiveContainer width="100%" height={340}>
              <LineChart data={channelData.slice(0, 100)} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="t" tick={{ fontSize: 11, fill: '#4a4f66' }} />
                <YAxis tick={{ fontSize: 11, fill: '#4a4f66' }} />
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ color: '#8a8faa', fontSize: 12 }} />
                {Object.keys(channelData[0] || {}).filter(k => k !== 't').map((ch, i) => (
                  <Line key={ch} type="monotone" dataKey={ch} stroke={CHANNEL_COLORS[i % CHANNEL_COLORS.length]}
                    strokeWidth={1.5} dot={false} />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Feature summary cards if data exists */}
      {vizData?.features_summary && (
        <div className="animate-fadeUp" style={{ animationDelay: '0.2s' }}>
          <h3 className="section-title">Extracted Features</h3>
          <div className="features-summary-grid">
            {Object.entries(vizData.features_summary).map(([key, val]) => (
              <div key={key} className="feature-chip">
                <span className="feature-chip-key">{key.replace(/_/g, ' ')}</span>
                <span className="feature-chip-val">{typeof val === 'number' ? val.toFixed(4) : String(val)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
