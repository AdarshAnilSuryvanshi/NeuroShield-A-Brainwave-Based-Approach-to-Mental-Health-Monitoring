const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = {
  register: (data) =>
    fetch(`${BASE_URL}/api/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then(r => r.json()),

  login: (data) =>
    fetch(`${BASE_URL}/api/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then(r => r.json()),

  uploadEEG: (formData) =>
    fetch(`${BASE_URL}/api/upload/`, {
      method: 'POST',
      body: formData,
    }).then(r => r.json()),

  getReport: (uploadId) =>
    fetch(`${BASE_URL}/ml/stage5/report/${uploadId}/`).then(r => r.json()),

  getVisualization: (uploadId) =>
    fetch(`${BASE_URL}/ml/stage5/analyze/${uploadId}/`, {
      method: "POST",
    }).then(r => r.json()),

  chat: (uploadId, question) =>
    fetch(`${BASE_URL}/ml/stage5/chat/${uploadId}/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    }).then(r => r.json()),

  getCompare: (uploadId) =>
    fetch(`${BASE_URL}/ml/stage5/compare/${uploadId}/`).then(r => r.json()),

  getDashboard: (userId) =>
    fetch(`${BASE_URL}/api/dashboard/${userId || ''}`).then(r => r.json()),

  getUserUploads: () =>
    fetch(`${BASE_URL}/api/uploads/`).then(r => r.json()),
};

console.log("API LOADED:", api);
console.log("getUserUploads type:", typeof api.getUserUploads);

export default api;