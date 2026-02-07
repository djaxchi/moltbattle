import { createContext, useContext, useState, useEffect } from 'react';
import { getCurrentUser, loginUser, registerUserWithPassword } from './api';

const AuthContext = createContext(null);

const TOKEN_KEY = 'molt_auth_token';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [redirectUrl, setRedirectUrl] = useState(null);

  // Check for existing token and load user on mount
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      loadUser();
    } else {
      setLoading(false);
    }
  }, []);

  const loadUser = async () => {
    try {
      const userData = await getCurrentUser();
      setUser(userData);
    } catch (error) {
      // Token invalid or expired, clear it
      localStorage.removeItem(TOKEN_KEY);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const signUp = async (username, password, email = null, techDescription = null) => {
    const response = await registerUserWithPassword(username, password, email, techDescription);
    localStorage.setItem(TOKEN_KEY, response.token);
    setUser(response.user);
    return response;
  };

  const signIn = async (username, password) => {
    const response = await loginUser(username, password);
    localStorage.setItem(TOKEN_KEY, response.token);
    setUser(response.user);
    return response;
  };

  const signOut = async () => {
    localStorage.removeItem(TOKEN_KEY);
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      const userData = await getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Error refreshing user:', error);
    }
  };

  const getToken = () => {
    return localStorage.getItem(TOKEN_KEY);
  };

  const value = {
    user,
    loading,
    signUp,
    signIn,
    signOut,
    refreshUser,
    getToken,
    isAuthenticated: !!user,
    redirectUrl,
    setRedirectUrl,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
