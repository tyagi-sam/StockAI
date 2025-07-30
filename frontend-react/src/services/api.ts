import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE = `${API_URL}/api/v1`;

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const auth = {
  login: (email: string, password: string) => 
    api.post('/auth/login', new URLSearchParams({ username: email, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }),
  register: (email: string, password: string, name: string) => 
    api.post('/auth/register', { email, password, name }),
  verifyEmail: (email: string, otp: string) => 
    api.post('/auth/verify-email', { email, otp }),
  resendOtp: (email: string) => 
    api.post('/auth/resend-otp', { email }),
  getGoogleLoginUrl: () => api.get('/auth/login/google'),
  handleGoogleCallback: (code: string, state: string) => 
    api.post('/auth/callback/google', { code, state }),
  refreshToken: () => api.post('/auth/refresh'),
  getMe: () => api.get('/auth/me'),
};

// Stock Analysis API
export const stockAnalysis = {
  analyze: (symbol: string, analysis_type: 'technical' | 'ai' | 'both' = 'technical') => 
    api.post('/search/analyze', { symbol, analysis_type }),
  getHealth: () => api.get('/search/health'),
  getSearchStatus: () => api.get('/search/search-status'),
  getTodaysSearches: () => api.get('/search/todays-searches'),
  getTodaysSearchDetail: (symbol: string, analysis_type: string = 'technical') => api.get(`/search/todays-searches/${symbol}?analysis_type=${analysis_type}`),
};

export default api; 