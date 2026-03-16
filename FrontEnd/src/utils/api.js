// All backend API endpoints mapped from Django views
// const BASE_URL = process.env.REACT_APP_API_URL || 'https://orange-umbrella-vp9w79g67whpgvx-8000.app.github.dev';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = {
  // Auth
  register: (data) => fetch(`${BASE_URL}/api/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }).then(r => r.json()),

  login: (data) => fetch(`${BASE_URL}/api/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }).then(r => r.json()),

  // EEG Upload
  uploadEEG: (formData) => fetch(`${BASE_URL}/api/upload/`, {
    method: 'POST',
    body: formData,
  }).then(r => r.json()),

  // ML endpoints
  getReport: (uploadId) => fetch(`${BASE_URL}/ml/report/${uploadId}/`).then(r => r.json()),

  getVisualization: (uploadId) => fetch(`${BASE_URL}/ml/visualization/${uploadId}/`).then(r => r.json()),

  chat: (uploadId, question) => fetch(`${BASE_URL}/ml/chat/${uploadId}/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  }).then(r => r.json()),

  getDashboard: (userId) => fetch(`${BASE_URL}/api/dashboard/${userId || ''}`).then(r => r.json()),

  getUserUploads: () => fetch(`${BASE_URL}/api/uploads/`).then(r => r.json()),
};

export default api;
