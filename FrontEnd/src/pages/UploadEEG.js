import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import './UploadEEG.css';

export default function UploadEEG() {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const inputRef = useRef();
  const navigate = useNavigate();

  const handleFile = (f) => {
    setFile(f);
    setResult(null);
    setError('');
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const uploadFile = async () => {
    if (!file) return;
    setUploading(true);
    setError('');
    setProgress(0);

    // Simulate progress
    const interval = setInterval(() => setProgress(p => Math.min(p + Math.random() * 12, 88)), 300);

    try {
      const formData = new FormData();
      formData.append('edf_file', file);
      const data = await api.uploadEEG(formData);
      clearInterval(interval);
      setProgress(100);

      if (data.result || data.label || data.predicted_label) {
        setResult(data.result || data);
      } else if (data.error) {
        setError(data.error);
      } else {
        setResult(data); // show whatever backend returns
      }
    } catch (e) {
      clearInterval(interval);
      setError('Upload failed. Check if backend is running on port 8000.');
    } finally {
      setUploading(false);
    }
  };

  const labelColor = (label) => {
    if (!label) return '';
    const l = label.toLowerCase();
    if (l.includes('normal') || l.includes('healthy')) return 'badge-success';
    if (l.includes('mild') || l.includes('moderate')) return 'badge-warning';
    return 'badge-danger';
  };

  return (
    <div className="upload-page page-container">
      <div className="upload-header animate-fadeUp">
        <div>
          <h2>Upload EEG Data</h2>
          <p className="upload-sub">Supports EDF, CSV, and BDF brainwave files</p>
        </div>
      </div>

      <div className="upload-layout">
        {/* Drop zone */}
        <div
          className={`drop-zone animate-fadeUp ${dragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`}
          style={{ animationDelay: '0.1s' }}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          onClick={() => !file && inputRef.current.click()}
        >
          <input ref={inputRef} type="file" accept=".edf,.csv,.bdf,.txt" hidden onChange={e => handleFile(e.target.files[0])} />

          {!file ? (
            <>
              <div className="drop-icon">
                <div className="drop-icon-inner">↑</div>
                <div className="drop-ring" />
              </div>
              <div className="drop-text">
                <strong>Drop your EEG file here</strong>
                <p>or click to browse</p>
              </div>
              <div className="drop-formats">
                <span className="badge badge-primary">EDF</span>
                <span className="badge badge-primary">CSV</span>
                <span className="badge badge-primary">BDF</span>
              </div>
            </>
          ) : (
            <div className="file-selected">
              <div className="file-icon">◈</div>
              <div className="file-info">
                <strong>{file.name}</strong>
                <span>{(file.size / 1024).toFixed(1)} KB</span>
              </div>
              <button className="btn btn-ghost" style={{ padding: '6px 12px', fontSize: 12 }}
                onClick={e => { e.stopPropagation(); setFile(null); }}>✕ Remove</button>
            </div>
          )}
        </div>

        {/* Actions + result panel */}
        <div className="upload-side animate-fadeUp" style={{ animationDelay: '0.2s' }}>
          <div className="card">
            <h3 style={{ marginBottom: 16 }}>Analysis</h3>

            {error && <div className="alert alert-error" style={{ marginBottom: 12 }}>{error}</div>}

            {uploading && (
              <div className="progress-wrap">
                <div className="progress-bar-bg">
                  <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
                </div>
                <div className="progress-labels">
                  <span>Analyzing EEG…</span>
                  <span>{Math.round(progress)}%</span>
                </div>
                <div className="upload-steps">
                  {['Parsing signals', 'Extracting features', 'Running ML model', 'Generating result'].map((step, i) => (
                    <div key={step} className={`upload-step ${progress > i * 25 ? 'done' : ''}`}>
                      <div className="step-dot" /> {step}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result && !uploading && (
              <div className="result-panel">
                <div className="result-header">
                  <span className="result-title">Analysis Complete</span>
                  <div className="pulse-dot" />
                </div>
                <div className="result-grid">
                  {result.label !== undefined && (
                    <div className="result-item">
                      <span className="result-key">Prediction</span>
                      <span className={`badge ${labelColor(result.label)}`}>{result.label}</span>
                    </div>
                  )}
                  {result.predicted_label !== undefined && (
                    <div className="result-item">
                      <span className="result-key">Label</span>
                      <span className={`badge ${labelColor(result.predicted_label)}`}>{result.predicted_label}</span>
                    </div>
                  )}
                  {result.probability !== undefined && (
                    <div className="result-item">
                      <span className="result-key">Confidence</span>
                      <span className="result-val accent">{(result.probability * 100).toFixed(2)}%</span>
                    </div>
                  )}
                  {result.upload_id !== undefined && (
                    <div className="result-item">
                      <span className="result-key">Upload ID</span>
                      <span className="result-val">{result.upload_id}</span>
                    </div>
                  )}
                  {/* Show any additional JSON fields */}
                  {Object.entries(result).filter(([k]) => !['label','predicted_label','probability','upload_id'].includes(k)).map(([k, v]) => (
                    typeof v !== 'object' && (
                      <div key={k} className="result-item">
                        <span className="result-key">{k.replace(/_/g,' ')}</span>
                        <span className="result-val">{String(v)}</span>
                      </div>
                    )
                  ))}
                </div>
                <div style={{ display: 'flex', gap: 8, marginTop: 16, flexWrap: 'wrap' }}>
                  <button className="btn btn-ghost" style={{ flex: 1, fontSize: 13 }} onClick={() => navigate('/visualization')}>View Charts</button>
                  <button className="btn btn-ghost" style={{ flex: 1, fontSize: 13 }} onClick={() => navigate('/report')}>Full Report</button>
                </div>
              </div>
            )}

            {!result && !uploading && (
              <div className="upload-info">
                <p>The ML pipeline will:</p>
                <ul>
                  <li>Parse your EEG channels</li>
                  <li>Extract frequency features (Alpha, Beta, Theta, Delta)</li>
                  <li>Run the classification model</li>
                  <li>Return a mental health prediction with confidence</li>
                </ul>
              </div>
            )}

            <button
              className="btn btn-primary"
              disabled={!file || uploading}
              onClick={uploadFile}
              style={{ width: '100%', marginTop: 16 }}
            >
              {uploading ? <><div className="spinner" /> Analyzing…</> : '⚡ Analyze EEG'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
