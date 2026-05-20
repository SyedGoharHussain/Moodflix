import { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { FiSearch, FiUser, FiLogOut, FiX } from 'react-icons/fi'
import { useAuthStore, useUIStore } from '../store/index.js'
import logo from '../assets/logo.png'

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuthStore()
  const { searchOpen, toggleSearch } = useUIStore()
  const [query, setQuery] = useState('')
  const [menuOpen, setMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const onLanding = location.pathname === '/'

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 16)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const handleSearch = (e) => {
    e.preventDefault()
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query.trim())}`)
      setQuery('')
      if (searchOpen) toggleSearch()
    }
  }

  const handleLogout = () => {
    logout()
    setMenuOpen(false)
    navigate('/')
  }

  const navBg = onLanding && !scrolled
    ? 'bg-transparent'
    : 'bg-bg-base/95 backdrop-blur border-b border-line-subtle'

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-colors duration-300 ${navBg}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2">
            <img src={logo} alt="MoodFlix" className="h-10 w-auto" />
          </Link>

          <div className="hidden md:flex items-center gap-7">
            <Link to="/dashboard" className="text-ink-dim hover:text-ink text-sm font-medium tracking-wide transition-colors">Discover</Link>
            <Link to="/dashboard" className="text-ink-dim hover:text-ink text-sm font-medium tracking-wide transition-colors">Trending</Link>
            {isAuthenticated && (
              <Link to="/profile" className="text-ink-dim hover:text-ink text-sm font-medium tracking-wide transition-colors">My Library</Link>
            )}
          </div>

          <div className="flex items-center gap-3">
            <button onClick={toggleSearch} className="p-2 rounded-full hover:bg-bg-hover text-ink-dim hover:text-ink transition-all" aria-label="Toggle search">
              {searchOpen ? <FiX size={18} /> : <FiSearch size={18} />}
            </button>

            {isAuthenticated ? (
              <div className="relative">
                <button onClick={() => setMenuOpen(!menuOpen)} className="flex items-center gap-2 p-1.5 rounded-full hover:bg-bg-hover transition-all" aria-label="Account menu">
                  <div className="w-8 h-8 rounded-full bg-accent-red flex items-center justify-center">
                    <span className="text-xs font-bold text-white">
                      {user?.username?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}
                    </span>
                  </div>
                </button>
                <AnimatePresence>
                  {menuOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: -8 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -8 }}
                      className="absolute right-0 mt-2 w-48 surface overflow-hidden shadow-2xl"
                    >
                      <Link to="/profile" onClick={() => setMenuOpen(false)} className="flex items-center gap-3 px-4 py-3 text-sm text-ink-dim hover:text-ink hover:bg-bg-hover transition-all">
                        <FiUser size={14} /> Profile
                      </Link>
                      <button onClick={handleLogout} className="w-full flex items-center gap-3 px-4 py-3 text-sm text-ink-dim hover:text-accent-red hover:bg-bg-hover transition-all">
                        <FiLogOut size={14} /> Sign Out
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ) : (
              <Link to="/login" className="px-4 py-2 text-sm font-semibold bg-accent-red text-white rounded-md hover:brightness-110 transition-all">
                Sign In
              </Link>
            )}
          </div>
        </div>

        <AnimatePresence>
          {searchOpen && (
            <motion.form
              onSubmit={handleSearch}
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden pb-4"
            >
              <div className="relative">
                <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-ink-mute" />
                <input
                  autoFocus
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search movies, shows, or moods…"
                  className="w-full pl-12 pr-4 py-3 bg-bg-card border border-line rounded-md text-ink placeholder:text-ink-mute focus:outline-none focus:border-accent-cyan/60 focus:ring-1 focus:ring-accent-cyan/30 font-body text-sm transition-all"
                />
              </div>
            </motion.form>
          )}
        </AnimatePresence>
      </div>
    </nav>
  )
}
