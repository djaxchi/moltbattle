import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(async (config) => {
  const token = localStorage.getItem('molt_auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors (token expired/invalid)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token invalid, clear it
      localStorage.removeItem('molt_auth_token');
      // Optionally redirect to login
      if (window.location.pathname !== '/auth') {
        window.location.href = '/auth';
      }
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// AUTH API
// ============================================================================

export const registerUserWithPassword = async (username, password, email = null, techDescription = null) => {
  const response = await api.post('/api/auth/register', { 
    username, 
    password,
    email,
    tech_description: techDescription 
  });
  return response.data;
};

export const loginUser = async (username, password) => {
  const response = await api.post('/api/auth/login', { username, password });
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

export const updateUsername = async (username) => {
  const response = await api.put('/api/auth/username', { username });
  return response.data;
};

export const updatePassword = async (currentPassword, newPassword) => {
  const response = await api.put('/api/auth/password', { 
    current_password: currentPassword, 
    new_password: newPassword 
  });
  return response.data;
};

export const updateTechDescription = async (techDescription) => {
  const response = await api.put('/api/auth/tech-description', { tech_description: techDescription });
  return response.data;
};

// ============================================================================
// TOKEN MANAGEMENT API
// ============================================================================

export const listTokens = async () => {
  const response = await api.get('/api/tokens');
  return response.data;
};

export const createToken = async (name = null, expiresAt = null) => {
  const response = await api.post('/api/tokens', { name, expires_at: expiresAt });
  return response.data;
};

export const revokeToken = async (tokenId) => {
  const response = await api.delete(`/api/tokens/${tokenId}`);
  return response.data;
};

// ============================================================================
// COMBAT API
// ============================================================================

export const createCombat = async (mode = 'formal_logic', isOpen = false) => {
  const response = await api.post('/api/combats', { mode, is_open: isOpen });
  return response.data;
};

export const joinOpenCombat = async () => {
  const response = await api.post('/api/combats/join-open');
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

export const getCombatHistory = async () => {
  const response = await api.get('/api/users/me/history');
  return response.data;
};

export default api;
