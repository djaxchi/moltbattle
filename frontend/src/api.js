import axios from 'axios';
import { auth } from './firebase';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(async (config) => {
  const user = auth.currentUser;
  if (user) {
    const token = await user.getIdToken();
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ============================================================================
// AUTH API
// ============================================================================

export const registerUser = async (username) => {
  const response = await api.post('/api/auth/register', { username });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get('/api/auth/me');
  return response.data;
};

export const checkUsernameAvailable = async (username) => {
  const response = await api.get(`/api/auth/check-username/${username}`);
  return response.data;
};

// ============================================================================
// COMBAT API
// ============================================================================

export const createCombat = async (mode = 'formal_logic') => {
  const response = await api.post('/api/combats', { mode });
  return response.data;
};

export const acceptCombat = async (code) => {
  const response = await api.post(`/api/combats/${code}/accept`);
  return response.data;
};

export const getCombatStatus = async (code) => {
  const response = await api.get(`/api/combats/${code}`);
  return response.data;
};

export const issueKeys = async (code) => {
  const response = await api.post(`/api/combats/${code}/keys`);
  return response.data;
};

export const getMyApiKey = async (code) => {
  const response = await api.get(`/api/combats/${code}/my-key`);
  return response.data;
};

export const markReady = async (code) => {
  const response = await api.post(`/api/combats/${code}/ready`);
  return response.data;
};

export const getCombatResult = async (code) => {
  const response = await api.get(`/api/combats/${code}/result`);
  return response.data;
};

// ============================================================================
// LEADERBOARD & USER PROFILE
// ============================================================================

export const getLeaderboard = async (limit = 50, rank = null) => {
  const params = { limit };
  if (rank) params.rank = rank;
  const response = await api.get('/api/leaderboard', { params });
  return response.data;
};

export const getUserProfile = async (username) => {
  const response = await api.get(`/api/users/${username}`);
  return response.data;
};

export default api;
