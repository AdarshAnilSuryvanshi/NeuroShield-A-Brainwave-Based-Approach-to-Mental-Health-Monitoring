import React, { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import './LandingPage.css';

const FEATURES = [
  { icon: '⬡', title: 'EEG Upload', desc: 'Upload EDF/CSV brainwave files and instantly trigger ML analysis pipeline.' },
  { icon: '◈', title: 'Live Visualization', desc: 'View multi-channel brainwave signals as interactive charts with band analysis.' },
  { icon: '◎', title: 'AI Chat Agent', desc: 'Conversational AI grounded in your EEG data — ask anything, get clinical context.' },
  { icon: '≡', title: 'Full Reports', desc: 'PDF-ready mental health reports with predictions, probabilities, and feature summaries.' },
];

export default function LandingPage() {
  const waveRef = useRef(null);

  useEffect(() => {
    const canvas = waveRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    let t = 0;
    let animId;

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const channels = [
        { color: 'rgba(108,74,227,0.6)', freq: 0.015, amp: 30, offset: 0 },
        { color: 'rgba(0,229,200,0.4)', freq: 0.023, amp: 20, offset: 50 },
        { color: 'rgba(155,126,248,0.3)', freq: 0.011, amp: 40, offset: 100 },
      ];
      channels.forEach(({ color, freq, amp, offset }) => {
        ctx.beginPath();
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        for (let x = 0; x < canvas.width; x++) {
          const y = canvas.height / 2 + offset - 60 +
            Math.sin(x * freq + t) * amp +
            Math.sin(x * freq * 1.7 + t * 1.3) * (amp * 0.4) +
            Math.sin(x * freq * 0.5 + t * 0.7) * (amp * 0.6);
          x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
        }
        ctx.stroke();
      });
      t += 0.04;
      animId = requestAnimationFrame(draw);
    };
    draw();
    const resize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };
    window.addEventListener('resize', resize);
    return () => { cancelAnimationFrame(animId); window.removeEventListener('resize', resize); };
  }, []);

  return (
    <div className="landing">
      {/* Hero */}
      <section className="hero">
        <div className="hero-bg-wave">
          <canvas ref={waveRef} className="wave-canvas" />
        </div>

        <div className="hero-content page-container">
          <div className="hero-badge animate-fadeUp">
            <div className="pulse-dot" />
            <span>Brainwave · Mental Health · AI</span>
          </div>

          <h1 className="hero-title animate-fadeUp" style={{ animationDelay: '0.1s' }}>
            Monitor Your Mind<br />
            <span className="glow-text">With Brainwaves</span>
          </h1>

          <p className="hero-desc animate-fadeUp" style={{ animationDelay: '0.2s' }}>
            NeuroShield analyzes EEG signals using deep learning to detect mental health patterns,
            visualize brain activity, and generate clinical-grade reports — all in your browser.
          </p>

          <div className="hero-actions animate-fadeUp" style={{ animationDelay: '0.3s' }}>
            <Link to="/register" className="btn btn-primary hero-cta">
              Get Started Free
            </Link>
            <Link to="/login" className="btn btn-ghost hero-cta">
              Sign In
            </Link>
          </div>

          <div className="hero-stats animate-fadeUp" style={{ animationDelay: '0.4s' }}>
            {[['EEG Analysis', 'Real-time'], ['ML Model', 'Active'], ['Stage', '5 · Beta']].map(([label, val]) => (
              <div key={label} className="stat-chip">
                <span className="stat-val">{val}</span>
                <span className="stat-label">{label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="features-section page-container">
        <div className="section-label">Core Features</div>
        <h2>Everything your brain data needs</h2>
        <div className="features-grid">
          {FEATURES.map(({ icon, title, desc }, i) => (
            <div
              key={title}
              className="feature-card animate-fadeUp"
              style={{ animationDelay: `${0.1 * i}s`, animationFillMode: 'both' }}
            >
              <div className="feature-icon">{icon}</div>
              <h3>{title}</h3>
              <p>{desc}</p>
              <div className="feature-line" />
            </div>
          ))}
        </div>
      </section>

      {/* CTA bottom */}
      <section className="bottom-cta page-container">
        <div className="cta-card">
          <h2>Ready to decode your brain?</h2>
          <p>Upload your first EEG file and get a mental health analysis in under 60 seconds.</p>
          <Link to="/register" className="btn btn-accent">Start Now →</Link>
        </div>
      </section>

      <footer className="landing-footer">
        <span>© 2025 NeuroShield · Brainwave-Based Mental Health Monitoring</span>
      </footer>
    </div>
  );
}
