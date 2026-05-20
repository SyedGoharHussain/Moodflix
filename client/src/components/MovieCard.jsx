import { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { FiBookmark, FiStar, FiPlay } from 'react-icons/fi'
import { userAPI } from '../services/api.js'
import { useAuthStore } from '../store/index.js'

export default function MovieCard({ movie, index = 0 }) {
  const [saved, setSaved] = useState(false)
  const [hovered, setHovered] = useState(false)
  const { isAuthenticated } = useAuthStore()
  const navigate = useNavigate()

  const handleSave = async (e) => {
    e.stopPropagation()
    if (!isAuthenticated) return navigate('/login')
    try {
      if (saved) {
        await userAPI.unsave(movie.tmdb_id)
      } else {
        await userAPI.save({
          tmdb_id: movie.tmdb_id,
          title: movie.title,
          poster: movie.poster,
          rating: movie.rating,
          media_type: movie.media_type,
        })
      }
      setSaved(!saved)
    } catch (err) {
      console.error('Save error:', err)
    }
  }

  const handleClick = () => {
    navigate(`/movie/${movie.tmdb_id}?type=${movie.media_type || 'movie'}`)
  }

  const moodPct = movie.mood_match_pct

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: Math.min(index, 8) * 0.04 }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={handleClick}
      className="relative flex-shrink-0 w-[170px] sm:w-[190px] cursor-pointer group"
    >
      <motion.div
        animate={{ scale: hovered ? 1.06 : 1, y: hovered ? -6 : 0 }}
        transition={{ type: 'spring', stiffness: 280, damping: 24 }}
        className="relative aspect-[2/3] rounded-md overflow-hidden bg-bg-card"
        style={{ boxShadow: hovered ? '0 24px 60px -10px rgba(0,0,0,0.95)' : '0 6px 16px -4px rgba(0,0,0,0.6)' }}
      >
        {movie.poster ? (
          <img
            src={movie.poster}
            alt={movie.title}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-ink-mute text-xs">No Poster</div>
        )}

        <button
          onClick={handleSave}
          aria-label={saved ? 'Unsave' : 'Save'}
          className={`absolute top-2 right-2 p-2 rounded-full transition-all ${saved
            ? 'bg-accent-red text-white'
            : 'bg-black/60 backdrop-blur-sm text-ink-dim hover:text-ink hover:bg-black/80'}`}
        >
          <FiBookmark size={12} fill={saved ? 'currentColor' : 'none'} />
        </button>

        <motion.div
          initial={false}
          animate={{ opacity: hovered ? 1 : 0 }}
          transition={{ duration: 0.2 }}
          className="absolute inset-0 flex flex-col justify-end p-3 bg-gradient-to-t from-black via-black/60 to-transparent"
        >
          <h3 className="font-display text-sm text-white font-bold mb-1.5 line-clamp-2 leading-tight">
            {movie.title}
          </h3>
          <div className="flex items-center gap-2 mb-2">
            <span className="flex items-center gap-1 text-[10px] text-white">
              <FiStar size={10} className="text-yellow-400" />
              <span className="font-mono">{movie.rating?.toFixed(1)}</span>
            </span>
            {moodPct > 0 && (
              <span className="px-1.5 py-0.5 rounded-sm bg-accent-cyan/20 border border-accent-cyan/40 text-[10px] text-accent-cyan font-mono">
                {moodPct}% match
              </span>
            )}
          </div>
          {movie.ai_explanation?.reasons?.[0] && (
            <p className="text-[10px] text-ink-dim line-clamp-2 mb-2 font-body">
              {movie.ai_explanation.reasons[0]}
            </p>
          )}
          <div className="flex gap-2">
            <span className="flex items-center gap-1 text-[10px] text-white">
              <FiPlay size={10} /> Details
            </span>
          </div>
        </motion.div>
      </motion.div>

      <div className="mt-2 px-0.5">
        <h3 className="font-body text-sm text-ink truncate transition-colors">{movie.title}</h3>
        <p className="text-[11px] text-ink-mute font-mono">{movie.release_date?.slice(0, 4)}</p>
      </div>
    </motion.div>
  )
}
