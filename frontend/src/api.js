import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const createCombat = async (handle) => {
  const response = await api.post('/api/combats', { handle });
  return response.data;
};

export const acceptCombat = async (code, handle) => {
  const response = await api.post(`/api/combats/${code}/accept`, { handle });
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

export default api;
