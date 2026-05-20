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
    { id: 'saved',   label: 'Saved',    icon: <FiBookmark size={14} />, count: saved.length },
    { id: 'history', label: 'History',  icon: <FiClock size={14} />,    count: history.length },
    { id: 'moods',   label: 'Mood Log', icon: <FiHeart size={14} />,    count: moodHistory.length },
  ]

  const activeItems = activeTab === 'saved' ? saved : activeTab === 'history' ? history : []

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="min-h-screen pt-24 pb-20 max-w-7xl mx-auto px-4 sm:px-6 bg-bg-base">

      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
        className="surface p-7 mb-8 flex items-center gap-6">
        <div className="w-20 h-20 rounded-md bg-accent-red flex items-center justify-center">
          <FiUser className="text-white text-2xl" />
        </div>
        <div>
          <h1 className="font-display text-3xl text-ink font-extrabold tracking-tight">{user?.username || user?.email?.split('@')[0] || 'User'}</h1>
          <p className="text-ink-dim text-sm font-body">{user?.email}</p>
          {user?.created_at && <p className="text-ink-mute text-xs font-mono mt-1">Member since {user.created_at.slice(0, 10)}</p>}
        </div>
      </motion.div>

      <div className="flex gap-2 mb-8 border-b border-line">
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            className={`flex items-center gap-2 px-4 py-3 font-medium text-sm transition-all border-b-2 -mb-px ${activeTab === t.id
              ? 'border-accent-cyan text-ink'
              : 'border-transparent text-ink-dim hover:text-ink'}`}
          >
            {t.icon} {t.label}
            {t.count > 0 && <span className="text-[10px] font-mono bg-bg-card border border-line px-1.5 py-0.5 rounded">{t.count}</span>}
          </button>
        ))}
      </div>

      {activeTab === 'moods' ? (
        <div className="space-y-2">
          {moodHistory.length === 0 ? (
            <p className="text-center text-ink-dim py-12 font-body">No mood logs yet. Start by telling us how you feel.</p>
          ) : (
            moodHistory.map((m, i) => {
              const MoodIcon = MOOD_ICON_MAP[m.mood] || FiActivity
              return (
                <motion.div key={i} initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.04 }}
                  className="surface p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-md bg-accent-cyan/15 border border-accent-cyan/30 flex items-center justify-center">
                      <MoodIcon size={18} className="text-accent-cyan" />
                    </div>
                    <div>
                      <p className="text-ink capitalize font-medium">{m.mood}</p>
                      <p className="text-xs text-ink-mute font-mono">{new Date(m.timestamp).toLocaleString()}</p>
                    </div>
                  </div>
                  <span className="font-mono text-sm text-accent-cyan">{Math.round(m.confidence * 100)}%</span>
                </motion.div>
              )
            })
          )}
        </div>
      ) : loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="aspect-[2/3] rounded-md skeleton" />
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
          <FiFilm size={48} className="mx-auto text-ink-mute mb-3" />
          <p className="text-ink-dim font-body">Nothing here yet. Start exploring.</p>
        </div>
      )}
    </motion.div>
  )
}
