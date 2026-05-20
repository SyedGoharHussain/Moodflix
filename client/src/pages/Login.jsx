import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FiMail, FiLock, FiFilm } from 'react-icons/fi'
import { FcGoogle } from 'react-icons/fc'
import { authAPI } from '../services/api.js'
import { useAuthStore } from '../store/index.js'
import logo from '../assets/logo.png'

export default function Login() {
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
      const { data } = await authAPI.login({ email, password })
      setAuth(data.user, data.token)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="min-h-screen flex items-center justify-center px-4 pt-16">
      <motion.div initial={{ opacity: 0, y: 30, scale: 0.95 }} animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5 }} className="w-full max-w-md">
        <div className="text-center mb-8">
          <img src={logo} alt="MoodFlix" className="h-20 w-auto mx-auto mb-4" />
          <h1 className="font-display text-4xl text-parchment mb-2">Welcome Back</h1>
          <p className="text-ash font-body text-sm">Sign in to your MoodFlix account</p>
        </div>

        <div className="glass rounded-2xl p-8">
          {error && (
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
              className="mb-4 p-3 rounded-xl bg-rust-deep/20 border border-rust/30 text-rust-pale text-sm font-body">
              {error}
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="text-xs text-ash uppercase tracking-widest mb-2 block">Email</label>
              <div className="relative">
                <FiMail className="absolute left-4 top-1/2 -translate-y-1/2 text-stone-light" size={16} />
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required
                  className="w-full pl-12 pr-4 py-3 bg-stone-mid border border-stone-light/20 rounded-xl text-parchment font-body text-sm focus:outline-none focus:border-rust/50 transition-all"
                  placeholder="you@example.com" />
              </div>
            </div>
            <div>
              <label className="text-xs text-ash uppercase tracking-widest mb-2 block">Password</label>
              <div className="relative">
                <FiLock className="absolute left-4 top-1/2 -translate-y-1/2 text-stone-light" size={16} />
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required
                  className="w-full pl-12 pr-4 py-3 bg-stone-mid border border-stone-light/20 rounded-xl text-parchment font-body text-sm focus:outline-none focus:border-rust/50 transition-all"
                  placeholder="••••••••" />
              </div>
            </div>
            <button type="submit" disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-rust to-rust-deep text-parchment rounded-xl font-body text-sm hover:from-rust-pale hover:to-rust transition-all shadow-lg shadow-rust/20 disabled:opacity-50">
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 flex items-center gap-3">
            <div className="flex-1 h-px bg-stone-light/20"></div>
            <span className="text-xs text-ash uppercase font-body tracking-wider">Or</span>
            <div className="flex-1 h-px bg-stone-light/20"></div>
          </div>

          <button type="button" className="mt-6 w-full py-3 bg-stone-mid border border-stone-light/20 rounded-xl font-body text-sm text-parchment hover:bg-stone-light/10 transition-all flex items-center justify-center gap-3">
            <FcGoogle size={20} />
            Continue with Google
          </button>

          <p className="text-center text-ash text-sm mt-6 font-body">
            Don't have an account?{' '}
            <Link to="/register" className="text-rust-pale hover:text-rust transition-colors">Create one</Link>
          </p>
        </div>
      </motion.div>
    </motion.div>
  )
}
