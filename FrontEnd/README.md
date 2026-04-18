# NeuroShield React Frontend

> Brainwave-Based Mental Health Monitoring — React JS UI

## ⚡ Quick Start

```bash
cd frontend
npm install
npm start
```

App runs at **http://localhost:3000**

---

## 📁 Project Structure

```
src/
├── pages/
│   ├── LandingPage.js      # Hero + features showcase
│   ├── LoginPage.js        # Auth with backend /api/login/
│   ├── RegisterPage.js     # Registration /api/register/
│   ├── Dashboard.js        # Stats + recent uploads /api/uploads/
│   ├── UploadEEG.js        # Drag-drop EEG upload → /api/upload/
│   ├── VisualizationPage.js# Recharts: Line, Area, Bar, Radar
│   ├── ChatbotPage.js      # AI Chat → /ml/chat/<id>/
│   └── ReportPage.js       # Full report + charts → /ml/report/<id>/
├── components/
│   └── Navbar.js           # Sticky nav with brand waves
├── utils/
│   └── api.js              # All API calls (configure BASE_URL here)
├── App.js                  # Router + Auth context
└── index.css               # Design system (CSS variables)
```

---

## 🔌 Backend API Endpoints Used

| Endpoint | Method | Page |
|----------|--------|------|
| `/api/register/` | POST | Register |
| `/api/login/` | POST | Login |
| `/api/upload/` | POST multipart | Upload EEG |
| `/api/uploads/` | GET | Dashboard |
| `/ml/report/<id>/` | GET | Report |
| `/ml/visualization/<id>/` | GET | Visualization |
| `/ml/chat/<id>/` | POST | Chatbot |

---

## 🌐 Configure Backend URL

Edit `src/utils/api.js`:

```js
const BASE_URL = 'http://localhost:8000'; // Change this
```

Or set environment variable:

```bash
REACT_APP_API_URL=https://your-backend.com npm start
```

---

## 🎨 Design System

- **Theme**: Dark neural — deep space with purple/teal accents
- **Fonts**: Syne (display) + DM Sans (body)
- **Charts**: Recharts — LineChart, AreaChart, BarChart, RadarChart, RadialBarChart
- **CSS Variables**: All in `src/index.css` `:root`

---

## 📊 Visualization Charts

The visualization page shows **4 chart types**:

1. **Brainwave** — Raw EEG signal as AreaChart
2. **Band Power** — Delta/Theta/Alpha/Beta/Gamma BarChart
3. **Radar** — All bands on RadarChart
4. **Channels** — Multi-channel LineChart

When real `upload_id` data is loaded from `/ml/visualization/<id>/`, it expects:

```json
{
  "band_power": { "delta": 0.82, "theta": 0.58, "alpha": 0.91, "beta": 0.64, "gamma": 0.37 },
  "channels": [{ "name": "Fp1", "values": [0.1, 0.2, ...] }],
  "features_summary": { "mean_alpha": 0.91, ... }
}
```

---

## 🔐 Auth

- Uses `localStorage` for session persistence
- `ProtectedRoute` wraps all authenticated pages
- Demo mode: if backend is offline, login/register still navigates to dashboard

---

## ✅ Compatibility Notes

- Flutter pages → React pages (1:1 mapping)
- All JSON from backend is displayed — tables, charts, raw JSON viewer
- Responsive: works on mobile, tablet, desktop
