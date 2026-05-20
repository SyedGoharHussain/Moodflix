import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  FiUser, FiBookmark, FiClock, FiHeart,
  FiSmile, FiFrown, FiMoon, FiZap, FiSun, FiCloud,
  FiAlertTriangle, FiActivity, FiEye, FiCompass,
  FiTarget, FiMap, FiStar, FiShield, FiFilm
} from 'react-icons/fi'
import MovieCard from '../components/MovieCard.jsx'
import { useAuthStore, useMoodStore } from '../store/index.js'
import { userAPI } from '../services/api.js'

const MOOD_ICON_MAP = {
  happy: FiSmile, sad: FiFrown, lonely: FiMoon, romantic: FiHeart, excited: FiZap,
  relaxed: FiSun, stressed: FiCloud, dark: FiAlertTriangle, emotional: FiActivity,
  'mind-bending': FiEye, curious: FiCompass, nostalgic: FiClock, motivated: FiTarget,
  adventurous: FiMap, wholesome: FiStar, scared: FiShield,
}

export default function Profile() {
  const { user, isAuthenticated } = useAuthStore()
  const { moodHistory } = useMoodStore()
  const navigate = useNavigate()
  const [saved, setSaved] = useState([])
  const [history, setHistory] = useState([])
  const [activeTab, setActiveTab] = useState('saved')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isAuthenticated) { navigate('/login'); return }
    const fetch = async () => {
      try {
        const [s, h] = await Promise.all([userAPI.getSaved(), userAPI.history()])
        setSaved(s.data.results || [])
        setHistory(h.data.results || [])
      } catch (err) { console.error(err) }
      finally { setLoading(false) }
    }
    fetch()
  }, [isAuthenticated])

  const tabs = [
    { id: 'saved', label: 'Saved', icon: <FiBookmark size={14} />, count: saved.length },
    { id: 'history', label: 'History', icon: <FiClock size={14} />, count: history.length },
    { id: 'moods', label: 'Mood Log', icon: <FiHeart size={14} />, count: moodHistory.length },
  ]

  const activeItems = activeTab === 'saved' ? saved : activeTab === 'history' ? history : []

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="min-h-screen pt-24 pb-20 max-w-7xl mx-auto px-4 sm:px-6">

      {/* Profile Header */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-8 mb-8 flex items-center gap-6">
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-rust to-rust-pale flex items-center justify-center shadow-lg">
          <FiUser className="text-parchment text-2xl" />
        </div>
        <div>
          <h1 className="font-display text-3xl text-parchment">{user?.username || 'User'}</h1>
          <p className="text-ash text-sm font-body">{user?.email}</p>
          <p className="text-stone-light text-xs font-body mt-1">Member since {user?.created_at?.slice(0, 10)}</p>
        </div>
      </motion.div>

      {/* Tabs */}
      <div className="flex gap-2 mb-8">
        {tabs.map(t => (
          <button key={t.id} onClick={() => setActiveTab(t.id)}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-body text-sm transition-all
              ${activeTab === t.id ? 'bg-rust/20 text-rust-pale border border-rust/30' : 'glass text-ash hover:text-parchment'}`}>
            {t.icon} {t.label}
            {t.count > 0 && <span className="text-[10px] font-mono bg-stone-mid px-1.5 py-0.5 rounded-md">{t.count}</span>}
          </button>
        ))}
      </div>

      {/* Content */}
      {activeTab === 'moods' ? (
        <div className="space-y-3">
          {moodHistory.length === 0 ? (
            <p className="text-center text-ash py-12">No mood logs yet. Start by telling us how you feel!</p>
          ) : (
            moodHistory.map((m, i) => {
              const MoodIcon = MOOD_ICON_MAP[m.mood] || FiActivity
              return (
                <motion.div key={i} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="glass rounded-xl p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-rust/15 flex items-center justify-center">
                      <MoodIcon size={18} className="text-rust-pale" />
                    </div>
                    <div>
                      <p className="text-parchment capitalize font-body">{m.mood}</p>
                      <p className="text-xs text-stone-light">{new Date(m.timestamp).toLocaleString()}</p>
                    </div>
                  </div>
                  <span className="font-mono text-sm text-rust-pale">{Math.round(m.confidence * 100)}%</span>
                </motion.div>
              )
            })
          )}
        </div>
      ) : loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="aspect-[2/3] rounded-xl skeleton" />
          ))}
        </div>
      ) : activeItems.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {activeItems.map((m, i) => (
            <MovieCard key={m.tmdb_id || i} movie={m} index={i} />
          ))}
        </div>
      ) : (
        <div className="text-center py-20">
          <FiFilm size={48} className="mx-auto text-stone-light mb-4" />
          <p className="text-ash font-body">Nothing here yet. Start exploring!</p>
        </div>
      )}
    </motion.div>
  )
}
