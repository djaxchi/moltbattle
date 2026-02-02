/**
 * Firebase Configuration
 * 
 * Setup Instructions:
 * 1. Go to Firebase Console (https://console.firebase.google.com)
 * 2. Create a new project or use existing
 * 3. Go to Project Settings > General > Your apps > Add app (Web)
 * 4. Copy the firebaseConfig values to frontend/.env file
 * 5. Enable Email/Password authentication in Firebase Console > Authentication > Sign-in method
 * 6. Enable Google Sign-in in Firebase Console > Authentication > Sign-in method
 */

import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

// Check if Firebase config is provided
const apiKey = import.meta.env.VITE_FIREBASE_API_KEY;
const authDomain = import.meta.env.VITE_FIREBASE_AUTH_DOMAIN;
const projectId = import.meta.env.VITE_FIREBASE_PROJECT_ID;

if (!apiKey || apiKey.includes('YOUR_') || apiKey === 'your_api_key_here') {
  console.error(`
╔════════════════════════════════════════════════════════════════╗
║                  FIREBASE NOT CONFIGURED                       ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Create a .env file in the frontend folder with:              ║
║                                                                ║
║  1. Copy .env.example to .env                                 ║
║  2. Get Firebase config from:                                 ║
║     https://console.firebase.google.com                       ║
║     → Project Settings → General → Your apps → Web            ║
║  3. Fill in the values in .env                                ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
  `);
}

const firebaseConfig = {
  apiKey: apiKey || "MISSING_API_KEY",
  authDomain: authDomain || "MISSING_AUTH_DOMAIN",
  projectId: projectId || "MISSING_PROJECT_ID",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "MISSING_STORAGE_BUCKET",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "MISSING_SENDER_ID",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "MISSING_APP_ID"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication
export const auth = getAuth(app);

export default app;
