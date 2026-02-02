import { createContext, useContext, useState, useEffect } from 'react';
import { 
  onAuthStateChanged, 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  signOut as firebaseSignOut,
  GoogleAuthProvider,
  signInWithPopup
} from 'firebase/auth';
import { auth } from './firebase';
import { getCurrentUser } from './api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [firebaseUser, setFirebaseUser] = useState(null);
  const [user, setUser] = useState(null); // Our backend user
  const [loading, setLoading] = useState(true);
  const [needsUsername, setNeedsUsername] = useState(false);
  const [redirectUrl, setRedirectUrl] = useState(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      setFirebaseUser(firebaseUser);
      
      if (firebaseUser) {
        // Try to get user from our backend
        try {
          const backendUser = await getCurrentUser();
          setUser(backendUser);
          setNeedsUsername(false);
        } catch (error) {
          // 404 means user doesn't exist in our DB yet - needs username
          if (error.response?.status === 404) {
            setNeedsUsername(true);
            setUser(null);
          } else {
            console.error('Error fetching user:', error);
            setUser(null);
          }
        }
      } else {
        setUser(null);
        setNeedsUsername(false);
      }
      
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const signUp = async (email, password) => {
    const result = await createUserWithEmailAndPassword(auth, email, password);
    return result.user;
  };

  const signIn = async (email, password) => {
    const result = await signInWithEmailAndPassword(auth, email, password);
    return result.user;
  };

  const signInWithGoogle = async () => {
    const provider = new GoogleAuthProvider();
    const result = await signInWithPopup(auth, provider);
    return result.user;
  };

  const signOut = async () => {
    await firebaseSignOut(auth);
    setUser(null);
  };

  const refreshUser = async () => {
    if (firebaseUser) {
      try {
        const backendUser = await getCurrentUser();
        setUser(backendUser);
      } catch (error) {
        console.error('Error refreshing user:', error);
      }
    }
  };

  const getIdToken = async () => {
    if (firebaseUser) {
      return await firebaseUser.getIdToken();
    }
    return null;
  };

  const value = {
    firebaseUser,
    user,
    loading,
    signUp,
    signIn,
    signInWithGoogle,
    signOut,
    refreshUser,
    getIdToken,
    isAuthenticated: !!user,
    needsUsername,
    setNeedsUsername,
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
