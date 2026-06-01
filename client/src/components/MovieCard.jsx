import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { FiBookmark, FiStar, FiPlay, FiInfo } from 'react-icons/fi'
import { userAPI } from '../services/api.js'
import { useAuthStore } from '../store/index.js'

export default function MovieCard({ movie, index = 0 }) {
  const [saved, setSaved]     = useState(false)
  const [hovered, setHovered] = useState(false)
  const [saving, setSaving]   = useState(false)
  const { isAuthenticated }   = useAuthStore()
  const navigate              = useNavigate()

  const handleSave = async (e) => {
    e.stopPropagation()
    if (!isAuthenticated) return navigate('/login')
    setSaving(true)
    try {
      if (saved) {
        await userAPI.unsave(movie.tmdb_id)
      } else {
        await userAPI.save({
          tmdb_id:    movie.tmdb_id,
          title:      movie.title,
          poster:     movie.poster,
          rating:     movie.rating,
          media_type: movie.media_type,
        })
      }
      setSaved(!saved)
    } catch (err) {
      console.error('Save error:', err)
    } finally {
      setSaving(false)
    }
  }

  const handleClick = () => {
    navigate(`/movie/${movie.tmdb_id}?type=${movie.media_type || 'movie'}`)
  }

  const moodPct = movie.mood_match_pct

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: Math.min(index, 10) * 0.05, ease: 'easeOut' }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={handleClick}
      className="relative flex-shrink-0 w-[168px] sm:w-[192px] cursor-pointer card-shine"
    >
      {/* Poster frame */}
      <motion.div
        animate={{
          scale: hovered ? 1.05 : 1,
          y:     hovered ? -8 : 0,
        }}
        transition={{ type: 'spring', stiffness: 300, damping: 22 }}
        className="relative aspect-[2/3] rounded-xl overflow-hidden"
        style={{
          boxShadow: hovered
            ? '0 28px 70px -10px rgba(0,0,0,0.95), 0 0 30px rgba(0,212,255,0.08)'
            : '0 8px 24px -4px rgba(0,0,0,0.7)',
          background: 'var(--bg-card)',
        }}
      >
        {movie.poster ? (
          <img
            src={movie.poster}
            alt={movie.title}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center gap-2 text-ink-mute">
            <FiInfo size={24} />
            <span className="text-xs">No Poster</span>
          </div>
        )}

        {/* Top-right save button */}
        <motion.button
          onClick={handleSave}
          aria-label={saved ? 'Unsave' : 'Save'}
          whileHover={{ scale: 1.15 }}
          whileTap={{ scale: 0.9 }}
          className="absolute top-2 right-2 p-2 rounded-full transition-all z-10"
          style={{
            background: saved ? 'rgba(229,9,20,0.9)' : 'rgba(0,0,0,0.65)',
            backdropFilter: 'blur(6px)',
            border: saved ? '1px solid rgba(229,9,20,0.5)' : '1px solid rgba(255,255,255,0.1)',
            boxShadow: saved ? '0 0 12px rgba(229,9,20,0.4)' : 'none',
          }}
        >
          <FiBookmark
            size={12}
            fill={saved ? 'currentColor' : 'none'}
            className={saving ? 'opacity-50' : ''}
            color={saved ? '#fff' : '#a3a3b8'}
          />
        </motion.button>

        {/* Mood match badge */}
        <AnimatePresence>
          {moodPct > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.7, y: -4 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              className="absolute top-2 left-2 z-10 px-2 py-0.5 rounded-md text-[9px] font-mono font-bold"
              style={{
                background: 'rgba(0,212,255,0.15)',
                border: '1px solid rgba(0,212,255,0.4)',
                color: '#00d4ff',
                boxShadow: '0 0 10px rgba(0,212,255,0.2)',
              }}
            >
              {moodPct}%
            </motion.div>
          )}
        </AnimatePresence>

        {/* Hover overlay */}
        <motion.div
          initial={false}
          animate={{ opacity: hovered ? 1 : 0 }}
          transition={{ duration: 0.22 }}
          className="absolute inset-0 flex flex-col justify-end p-3"
          style={{
            background: 'linear-gradient(to top, rgba(0,0,0,0.97) 0%, rgba(0,0,0,0.65) 45%, transparent 80%)',
          }}
        >
          <h3 className="font-display text-[13px] text-white font-bold mb-1.5 line-clamp-2 leading-tight">
            {movie.title}
          </h3>

          {/* Rating */}
          <div className="flex items-center gap-2 mb-2">
            <span className="flex items-center gap-1 text-[10px]">
              <FiStar size={9} className="star-filled" />
              <span className="font-mono text-white font-semibold">{movie.rating?.toFixed(1)}</span>
            </span>
            <span className="text-[9px] text-ink-mute font-mono">
              {movie.release_date?.slice(0, 4)}
            </span>
          </div>

          {/* AI explanation snippet */}
          {movie.ai_explanation?.reasons?.[0] && (
            <p className="text-[9px] text-ink-dim line-clamp-2 mb-2 font-body leading-relaxed">
              {movie.ai_explanation.reasons[0]}
            </p>
          )}

          {/* Details CTA */}
          <div className="flex items-center gap-1.5 text-[10px] text-accent-cyan font-semibold">
            <FiPlay size={9} fill="currentColor" />
            View Details
          </div>
        </motion.div>
      </motion.div>

      {/* Below-card text */}
      <div className="mt-2.5 px-0.5">
        <h3 className="font-body text-[13px] text-ink truncate font-medium leading-snug">
          {movie.title}
        </h3>
        <div className="flex items-center justify-between mt-0.5">
          <p className="text-[10px] text-ink-mute font-mono">{movie.release_date?.slice(0, 4)}</p>
          {movie.rating > 7 && (
            <span className="flex items-center gap-0.5 text-[9px] text-yellow-400/80 font-mono">
              <FiStar size={8} className="star-filled" />{movie.rating?.toFixed(1)}
            </span>
          )}
        </div>
      </div>
    </motion.div>
  )
}
