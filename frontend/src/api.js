import axios from 'axios'

export const api = axios.create({ baseURL: 'http://localhost:8000' })

export const chat = (question) => api.post('/api/chat', { question }).then(r => r.data)
export const uploadFile = (file) => {
  const fd = new FormData()
  fd.append('file', file)
  return api.post('/api/upload', fd).then(r => r.data)
}
export const getDashboard = () => api.get('/api/dashboard').then(r => r.data)
export const listReports = () => api.get('/api/reports').then(r => r.data)
export const getReport = (rid) => api.get(`/api/report/${rid}`).then(r => r.data)
export const kbSearch = (q) => api.get('/api/kb/search', { params: { q } }).then(r => r.data)
export const getHealth = () => api.get('/api/health').then(r => r.data)

export const riskColor = (level) => ({
  '低': '#22c55e', '关注': '#eab308', '中': '#f97316', '高': '#ef4444', '极高': '#b91c1c', '-': '#64748b',
}[level] || '#64748b')
