import { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { FiSearch, FiUser, FiLogOut, FiX, FiCompass, FiTrendingUp, FiBookOpen } from 'react-icons/fi'
import { useAuthStore, useUIStore } from '../store/index.js'
import logo from '../assets/logo.png'

const NAV_LINKS = [
  { to: '/dashboard', label: 'Discover',  icon: FiCompass },
  { to: '/dashboard', label: 'Trending',  icon: FiTrendingUp },
]

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuthStore()
  const { searchOpen, toggleSearch } = useUIStore()
  const [query, setQuery]       = useState('')
  const [menuOpen, setMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const location  = useLocation()
  const navigate  = useNavigate()
  const onLanding = location.pathname === '/'

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24)
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

  // Transparent on hero, frosted glass after scroll
  const navBg = onLanding && !scrolled
    ? 'bg-transparent border-transparent'
    : 'border-b'

  const navStyle = (!onLanding || scrolled)
    ? {
        background: 'rgba(8, 8, 16, 0.85)',
        borderColor: 'rgba(30, 30, 58, 0.7)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
      }
    : {}

  return (
    <motion.nav
      initial={{ y: -8, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${navBg}`}
      style={navStyle}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">

          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <motion.img
              src={logo}
              alt="MoodFlix"
              className="h-10 w-auto"
              whileHover={{ scale: 1.05 }}
              transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            />
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-1">
            {NAV_LINKS.map(({ to, label, icon: Icon }) => (
              <Link
                key={label}
                to={to}
                className="nav-pill flex items-center gap-1.5 px-3 py-2 rounded-lg text-ink-dim hover:text-ink text-sm font-medium tracking-wide transition-colors hover:bg-white/5"
              >
                <Icon size={13} />
                {label}
              </Link>
            ))}
            {isAuthenticated && (
              <Link
                to="/profile"
                className="nav-pill flex items-center gap-1.5 px-3 py-2 rounded-lg text-ink-dim hover:text-ink text-sm font-medium tracking-wide transition-colors hover:bg-white/5"
              >
                <FiBookOpen size={13} />
                My Library
              </Link>
            )}
          </div>

          {/* Right controls */}
          <div className="flex items-center gap-2">
            {/* Search button */}
            <motion.button
              onClick={toggleSearch}
              whileHover={{ scale: 1.08 }}
              whileTap={{ scale: 0.93 }}
              className="p-2 rounded-full text-ink-dim hover:text-ink transition-colors"
              style={{ background: searchOpen ? 'rgba(0,212,255,0.1)' : 'transparent',
                       border: searchOpen ? '1px solid rgba(0,212,255,0.3)' : '1px solid transparent' }}
              aria-label="Toggle search"
            >
              <AnimatePresence mode="wait" initial={false}>
                {searchOpen
                  ? <motion.div key="x"  initial={{ rotate: -90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: 90, opacity: 0 }} transition={{ duration: 0.15 }}><FiX size={18} /></motion.div>
                  : <motion.div key="s"  initial={{ rotate: 90,  opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: -90, opacity: 0 }} transition={{ duration: 0.15 }}><FiSearch size={18} /></motion.div>
                }
              </AnimatePresence>
            </motion.button>

            {/* Auth */}
            {isAuthenticated ? (
              <div className="relative">
                <motion.button
                  onClick={() => setMenuOpen(!menuOpen)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex items-center gap-2 p-1 rounded-full transition-all"
                  aria-label="Account menu"
                >
                  <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white"
                       style={{ background: 'linear-gradient(135deg, #e50914, #7c5cff)',
                                boxShadow: '0 0 12px rgba(229,9,20,0.4)' }}>
                    {user?.username?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}
                  </div>
                </motion.button>

                <AnimatePresence>
                  {menuOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: -10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: -10, scale: 0.95 }}
                      transition={{ duration: 0.18 }}
                      className="absolute right-0 mt-2 w-52 overflow-hidden shadow-2xl"
                      style={{
                        background: 'rgba(8,8,16,0.95)',
                        border: '1px solid rgba(30,30,58,0.9)',
                        borderRadius: '12px',
                        backdropFilter: 'blur(20px)',
                      }}
                    >
                      {/* User info header */}
                      <div className="px-4 py-3 border-b" style={{ borderColor: 'rgba(30,30,58,0.7)' }}>
                        <p className="text-xs font-semibold text-ink truncate">
                          {user?.username || user?.email?.split('@')[0]}
                        </p>
                        <p className="text-[10px] text-ink-mute truncate mt-0.5">{user?.email}</p>
                      </div>

                      <Link
                        to="/profile"
                        onClick={() => setMenuOpen(false)}
                        className="flex items-center gap-3 px-4 py-3 text-sm text-ink-dim hover:text-ink hover:bg-white/5 transition-all"
                      >
                        <FiUser size={14} /> Profile
                      </Link>
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-3 px-4 py-3 text-sm text-ink-dim hover:text-accent-red hover:bg-red-500/5 transition-all"
                      >
                        <FiLogOut size={14} /> Sign Out
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ) : (
              <motion.div whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }}>
                <Link
                  to="/login"
                  className="px-4 py-2 text-sm font-semibold text-white rounded-lg transition-all"
                  style={{
                    background: 'linear-gradient(135deg, #e50914, #c20810)',
                    boxShadow: '0 4px 16px rgba(229,9,20,0.35)',
                  }}
                >
                  Sign In
                </Link>
              </motion.div>
            )}
          </div>
        </div>

        {/* Expandable search bar */}
        <AnimatePresence>
          {searchOpen && (
            <motion.form
              onSubmit={handleSearch}
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.22, ease: 'easeOut' }}
              className="overflow-hidden pb-4"
            >
              <div className="relative">
                <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-ink-mute" size={16} />
                <input
                  autoFocus
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search movies, shows, or moods…"
                  className="w-full pl-11 pr-4 py-3 text-ink text-sm font-body transition-all focus:outline-none"
                  style={{
                    background: 'rgba(15,15,26,0.8)',
                    border: '1px solid rgba(0,212,255,0.2)',
                    borderRadius: '10px',
                    backdropFilter: 'blur(10px)',
                  }}
                  onFocus={e => e.target.style.borderColor = 'rgba(0,212,255,0.5)'}
                  onBlur={e => e.target.style.borderColor  = 'rgba(0,212,255,0.2)'}
                />
              </div>
            </motion.form>
          )}
        </AnimatePresence>
      </div>
    </motion.nav>
  )
}
