import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { FiUser, FiMail, FiLock, FiEye, FiEyeOff } from 'react-icons/fi'
import { FcGoogle } from 'react-icons/fc'
import { authAPI } from '../services/api.js'
import { useAuthStore } from '../store/index.js'
import { auth, googleProvider } from '../services/firebase.js'
import { signInWithPopup } from 'firebase/auth'

export default function Register() {
  const [username, setUsername]  = useState('')
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [error, setError]       = useState('')
  const [loading, setLoading]   = useState(false)
  const { setAuth }             = useAuthStore()
  const navigate                = useNavigate()

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
      const token  = await result.user.getIdToken()
      const { data } = await authAPI.google(token)
      setAuth(data.user, data.token)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Google signup failed')
      setLoading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="min-h-screen flex"
    >
      {/* ── LEFT: cinematic decorative panel ── */}
      <div className="hidden lg:flex flex-1 relative overflow-hidden" style={{ background: '#030308' }}>

        {/* Liquid blobs */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          <motion.div
            animate={{
              x: [0, 50, -40, 30, 0],
              y: [0, -50, 40, -30, 0],
              scale: [1, 1.1, 0.93, 1.06, 1],
            }}
            transition={{ duration: 24, repeat: Infinity, ease: 'easeInOut' }}
            className="absolute rounded-full"
            style={{
              top: '15%', right: '20%',
              width: '400px', height: '400px',
              background: 'radial-gradient(circle, rgba(124,92,255,0.1) 0%, transparent 65%)',
              filter: 'blur(60px)',
            }}
          />
          <motion.div
            animate={{
              x: [0, -40, 50, 0],
              y: [0, 40, -50, 0],
              scale: [1, 0.95, 1.08, 1],
            }}
            transition={{ duration: 20, repeat: Infinity, ease: 'easeInOut' }}
            className="absolute rounded-full"
            style={{
              bottom: '10%', left: '10%',
              width: '450px', height: '450px',
              background: 'radial-gradient(circle, rgba(0,212,255,0.08) 0%, transparent 65%)',
              filter: 'blur(65px)',
            }}
          />
        </div>

        <div className="scanlines" />
        <div className="vignette" />

        <div className="relative z-10 flex flex-col justify-center px-14 py-12 max-w-lg">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="font-display text-4xl xl:text-5xl font-extrabold text-ink mb-5 leading-[0.95] tracking-tight"
          >
            Your mood.
            <br />
            <span
              style={{
                background: 'linear-gradient(135deg, #7c5cff 0%, #00d4ff 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Your watchlist.
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="text-ink-dim font-body text-sm leading-relaxed max-w-xs"
          >
            Create an account and let our AI build a personalized
            cinema experience around how you feel.
          </motion.p>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7, duration: 0.5 }}
            className="space-y-1.5 mt-12"
          >
            {[0.3, 0.2, 0.1].map((opacity, i) => (
              <div key={i} className="h-px rounded-full"
                style={{
                  background: `linear-gradient(90deg, rgba(124,92,255,${opacity}) 0%, rgba(0,212,255,${opacity * 0.7}) 100%)`,
                  width: `${55 - i * 12}%`,
                }}
              />
            ))}
          </motion.div>
        </div>
      </div>

      {/* ── RIGHT: form panel ── */}
      <div
        className="flex-1 lg:max-w-[440px] flex items-center justify-center px-6 py-12"
        style={{ background: 'rgba(4,4,10,0.97)' }}
      >
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          className="w-full max-w-sm"
        >
          <div className="mb-8">
            <h1 className="font-display text-3xl text-ink font-extrabold tracking-tight mb-2">Join MoodFlix</h1>
            <p className="text-ink-dim font-body text-sm">Create your emotionally intelligent profile</p>
          </div>

          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -8, height: 0 }}
                animate={{ opacity: 1, y: 0, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mb-5 p-3 rounded-xl text-sm font-body overflow-hidden"
                style={{ background: 'rgba(229,9,20,0.1)', border: '1px solid rgba(229,9,20,0.2)', color: '#ff6b6b' }}
              >
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-[10px] text-ink-mute uppercase tracking-widest mb-2 block font-mono">Username</label>
              <div className="relative">
                <FiUser className="absolute left-4 top-1/2 -translate-y-1/2 text-ink-mute" size={15} />
                <input
                  type="text" value={username} onChange={(e) => setUsername(e.target.value)} required minLength={3}
                  placeholder="cinephile42"
                  className="w-full pl-11 pr-4 py-3 text-ink text-sm font-body transition-all focus:outline-none placeholder:text-ink-mute/60"
                  style={{ background: 'rgba(12,12,24,0.8)', border: '1px solid rgba(30,30,58,0.8)', borderRadius: '10px' }}
                  onFocus={e => e.target.style.borderColor = 'rgba(0,212,255,0.4)'}
                  onBlur={e  => e.target.style.borderColor = 'rgba(30,30,58,0.8)'}
                />
              </div>
            </div>

            <div>
              <label className="text-[10px] text-ink-mute uppercase tracking-widest mb-2 block font-mono">Email</label>
              <div className="relative">
                <FiMail className="absolute left-4 top-1/2 -translate-y-1/2 text-ink-mute" size={15} />
                <input
                  type="email" value={email} onChange={(e) => setEmail(e.target.value)} required
                  placeholder="you@example.com"
                  className="w-full pl-11 pr-4 py-3 text-ink text-sm font-body transition-all focus:outline-none placeholder:text-ink-mute/60"
                  style={{ background: 'rgba(12,12,24,0.8)', border: '1px solid rgba(30,30,58,0.8)', borderRadius: '10px' }}
                  onFocus={e => e.target.style.borderColor = 'rgba(0,212,255,0.4)'}
                  onBlur={e  => e.target.style.borderColor = 'rgba(30,30,58,0.8)'}
                />
              </div>
            </div>

            <div>
              <label className="text-[10px] text-ink-mute uppercase tracking-widest mb-2 block font-mono">Password</label>
              <div className="relative">
                <FiLock className="absolute left-4 top-1/2 -translate-y-1/2 text-ink-mute" size={15} />
                <input
                  type={showPass ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6}
                  placeholder="••••••••"
                  className="w-full pl-11 pr-12 py-3 text-ink text-sm font-body transition-all focus:outline-none placeholder:text-ink-mute/60"
                  style={{ background: 'rgba(12,12,24,0.8)', border: '1px solid rgba(30,30,58,0.8)', borderRadius: '10px' }}
                  onFocus={e => e.target.style.borderColor = 'rgba(0,212,255,0.4)'}
                  onBlur={e  => e.target.style.borderColor = 'rgba(30,30,58,0.8)'}
                />
                <button type="button" onClick={() => setShowPass(!showPass)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-ink-mute hover:text-ink transition-colors">
                  {showPass ? <FiEyeOff size={15} /> : <FiEye size={15} />}
                </button>
              </div>
            </div>

            <motion.button
              type="submit" disabled={loading}
              whileHover={{ scale: 1.015 }}
              whileTap={{ scale: 0.985 }}
              className="w-full py-3 text-white rounded-xl font-semibold text-sm transition-all disabled:opacity-50"
              style={{ background: 'linear-gradient(135deg, #e50914, #b8070f)', boxShadow: '0 4px 20px rgba(229,9,20,0.3)' }}
            >
              {loading ? 'Creating account...' : 'Create Account'}
            </motion.button>
          </form>

          <div className="my-5 flex items-center gap-3">
            <div className="flex-1 h-px" style={{ background: 'rgba(30,30,58,0.7)' }} />
            <span className="text-[10px] text-ink-mute uppercase tracking-widest font-mono">or</span>
            <div className="flex-1 h-px" style={{ background: 'rgba(30,30,58,0.7)' }} />
          </div>

          <motion.button
            type="button" onClick={handleGoogleSignup} disabled={loading}
            whileHover={{ scale: 1.015 }}
            whileTap={{ scale: 0.985 }}
            className="w-full py-3 rounded-xl font-semibold text-sm flex items-center justify-center gap-3 disabled:opacity-50 transition-all"
            style={{ background: '#fff', color: '#111' }}
          >
            <FcGoogle size={20} />
            Continue with Google
          </motion.button>

          <p className="text-center text-ink-dim text-sm mt-7 font-body">
            Already have an account?{' '}
            <Link to="/login" className="font-semibold transition-colors" style={{ color: '#00d4ff' }}>
              Sign in
            </Link>
          </p>
        </motion.div>
      </div>
    </motion.div>
  )
}
