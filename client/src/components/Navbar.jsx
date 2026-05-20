import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { FiSearch, FiUser, FiMenu, FiX, FiLogOut } from 'react-icons/fi'
import { useAuthStore, useUIStore } from '../store/index.js'
import logo from '../assets/logo.png'

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuthStore()
  const { searchOpen, toggleSearch } = useUIStore()
  const [query, setQuery] = useState('')
  const [menuOpen, setMenuOpen] = useState(false)
  const navigate = useNavigate()

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

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <img src={logo} alt="MoodFlix" className="h-16 w-auto" />
          </Link>

          {/* Center Nav Links */}
          <div className="hidden md:flex items-center gap-8">
            <Link to="/dashboard" className="text-ash hover:text-parchment text-sm font-body tracking-wide transition-colors">
              Discover
            </Link>
            <Link to="/dashboard" className="text-ash hover:text-parchment text-sm font-body tracking-wide transition-colors">
              Trending
            </Link>
            {isAuthenticated && (
              <Link to="/profile" className="text-ash hover:text-parchment text-sm font-body tracking-wide transition-colors">
                My Library
              </Link>
            )}
          </div>

          {/* Right Actions */}
          <div className="flex items-center gap-3">
            {/* Search Toggle */}
            <button onClick={toggleSearch} className="p-2 rounded-full hover:bg-stone-mid text-ash hover:text-parchment transition-all">
              {searchOpen ? <FiX size={18} /> : <FiSearch size={18} />}
            </button>

            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setMenuOpen(!menuOpen)}
                  className="flex items-center gap-2 p-2 rounded-full hover:bg-stone-mid transition-all"
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-rust to-rust-pale flex items-center justify-center">
                    <span className="text-xs font-bold text-parchment">
                      {user?.username?.[0]?.toUpperCase() || 'U'}
                    </span>
                  </div>
                </button>
                <AnimatePresence>
                  {menuOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: -10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: -10, scale: 0.95 }}
                      className="absolute right-0 mt-2 w-48 glass rounded-xl overflow-hidden shadow-2xl"
                    >
                      <Link
                        to="/profile"
                        onClick={() => setMenuOpen(false)}
                        className="flex items-center gap-3 px-4 py-3 text-sm text-ash hover:text-parchment hover:bg-stone-mid transition-all"
                      >
                        <FiUser size={14} /> Profile
                      </Link>
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-3 px-4 py-3 text-sm text-ash hover:text-rust-pale hover:bg-stone-mid transition-all"
                      >
                        <FiLogOut size={14} /> Sign Out
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ) : (
              <Link
                to="/login"
                className="px-4 py-2 text-sm font-body bg-gradient-to-r from-rust to-rust-deep text-parchment rounded-lg hover:from-rust-pale hover:to-rust transition-all shadow-lg shadow-rust/20"
              >
                Sign In
              </Link>
            )}

            {/* Mobile menu */}
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="md:hidden p-2 text-ash hover:text-parchment"
            >
              <FiMenu size={20} />
            </button>
          </div>
        </div>

        {/* Search Bar Expansion */}
        <AnimatePresence>
          {searchOpen && (
            <motion.form
              onSubmit={handleSearch}
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden pb-4"
            >
              <div className="relative">
                <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-ash" />
                <input
                  autoFocus
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search movies, shows, or describe what you want..."
                  className="w-full pl-12 pr-4 py-3 bg-stone-mid border border-stone-light/30 rounded-xl text-parchment placeholder:text-stone-light focus:outline-none focus:border-rust/50 focus:ring-1 focus:ring-rust/30 font-body text-sm transition-all"
                />
              </div>
            </motion.form>
          )}
        </AnimatePresence>
      </div>
    </nav>
  )
}
