import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';

// TODO: Replace with your actual Firebase config from the Firebase Console!
const firebaseConfig = {
  apiKey: "AIzaSyAk-pkmjJ4TnV4qflurBrSaI2be1ZW4Nc0",
  authDomain: "moodflix-189ab.firebaseapp.com",
  projectId: "moodflix-189ab",
  storageBucket: "moodflix-189ab.firebasestorage.app",
  messagingSenderId: "810290867571",
  appId: "1:810290867571:web:06ac1b3b7a19dd080be906",
  measurementId: "G-VPRX17BTV6"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
