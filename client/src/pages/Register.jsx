import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FiUser, FiMail, FiLock } from 'react-icons/fi'
import { FcGoogle } from 'react-icons/fc'
import { authAPI } from '../services/api.js'
import { useAuthStore } from '../store/index.js'
import { auth, googleProvider } from '../services/firebase.js'
import { signInWithPopup } from 'firebase/auth'
import logo from '../assets/logo.png'

export default function Register() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { data } = await authAPI.register({ username, email, password })
      setAuth(data.user, data.token)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed')
      setLoading(false)
    }
  }

  const handleGoogleSignup = async () => {
    try {
      setError('')
      setLoading(true)
      const result = await signInWithPopup(auth, googleProvider)
      const token = await result.user.getIdToken()
      const { data } = await authAPI.google(token)
      setAuth(data.user, data.token)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Google signup failed')
      setLoading(false)
    }
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="min-h-screen flex items-center justify-center px-4 pt-16 bg-bg-base">
      <motion.div initial={{ opacity: 0, y: 24, scale: 0.97 }} animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.45 }} className="w-full max-w-md">
        <div className="text-center mb-8">
          <img src={logo} alt="MoodFlix" className="h-16 w-auto mx-auto mb-4" />
          <h1 className="font-display text-3xl text-ink font-extrabold tracking-tight mb-1">Join MoodFlix</h1>
          <p className="text-ink-dim font-body text-sm">Create your emotionally intelligent profile</p>
        </div>

        <div className="surface p-7">
          {error && (
            <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
              className="mb-4 p-3 rounded-md bg-accent-red/15 border border-accent-red/30 text-accent-red text-sm font-body">
              {error}
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-[10px] text-ink-mute uppercase tracking-widest mb-1.5 block">Username</label>
              <div className="relative">
                <FiUser className="absolute left-4 top-1/2 -translate-y-1/2 text-ink-mute" size={16} />
                <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required minLength={3}
                  className="w-full pl-11 pr-4 py-3 bg-bg-elevated border border-line rounded-md text-ink font-body text-sm focus:outline-none focus:border-accent-cyan/60 focus:ring-1 focus:ring-accent-cyan/30 transition-all"
                  placeholder="cinephile42" />
              </div>
            </div>
            <div>
              <label className="text-[10px] text-ink-mute uppercase tracking-widest mb-1.5 block">Email</label>
              <div className="relative">
                <FiMail className="absolute left-4 top-1/2 -translate-y-1/2 text-ink-mute" size={16} />
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required
                  className="w-full pl-11 pr-4 py-3 bg-bg-elevated border border-line rounded-md text-ink font-body text-sm focus:outline-none focus:border-accent-cyan/60 focus:ring-1 focus:ring-accent-cyan/30 transition-all"
                  placeholder="you@example.com" />
              </div>
            </div>
            <div>
              <label className="text-[10px] text-ink-mute uppercase tracking-widest mb-1.5 block">Password</label>
              <div className="relative">
                <FiLock className="absolute left-4 top-1/2 -translate-y-1/2 text-ink-mute" size={16} />
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6}
                  className="w-full pl-11 pr-4 py-3 bg-bg-elevated border border-line rounded-md text-ink font-body text-sm focus:outline-none focus:border-accent-cyan/60 focus:ring-1 focus:ring-accent-cyan/30 transition-all"
                  placeholder="••••••••" />
              </div>
            </div>
            <button type="submit" disabled={loading}
              className="w-full py-3 bg-accent-red text-white rounded-md font-semibold text-sm hover:brightness-110 transition-all disabled:opacity-50">
              {loading ? 'Creating account…' : 'Create Account'}
            </button>
          </form>

          <div className="my-5 flex items-center gap-3">
            <div className="flex-1 h-px bg-line" />
            <span className="text-[10px] text-ink-mute uppercase tracking-widest">Or</span>
            <div className="flex-1 h-px bg-line" />
          </div>

          <button type="button" onClick={handleGoogleSignup} disabled={loading}
            className="w-full py-3 bg-white text-black rounded-md font-semibold text-sm hover:bg-white/90 transition-all flex items-center justify-center gap-3 disabled:opacity-50">
            <FcGoogle size={20} />
            Continue with Google
          </button>

          <p className="text-center text-ink-dim text-sm mt-6 font-body">
            Already have an account?{' '}
            <Link to="/login" className="text-accent-cyan hover:brightness-110 transition-colors">Sign in</Link>
          </p>
        </div>
      </motion.div>
    </motion.div>
  )
}
