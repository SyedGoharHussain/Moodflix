import { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { FiBookmark, FiStar, FiInfo } from 'react-icons/fi'
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
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.05 }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={handleClick}
      className="relative flex-shrink-0 w-[180px] sm:w-[200px] cursor-pointer group"
    >
      {/* Poster */}
      <div className="relative aspect-[2/3] rounded-xl overflow-hidden card-glow">
        {movie.poster ? (
          <img
            src={movie.poster}
            alt={movie.title}
            className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full bg-stone-mid flex items-center justify-center">
            <span className="text-stone-light text-xs">No Poster</span>
          </div>
        )}

        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-stone via-stone/20 to-transparent opacity-60 group-hover:opacity-80 transition-opacity" />

        {/* Hover Info */}
        <motion.div
          initial={false}
          animate={{ opacity: hovered ? 1 : 0, y: hovered ? 0 : 10 }}
          className="absolute inset-0 flex flex-col justify-end p-3"
        >
          {/* Rating Badge */}
          <div className="flex items-center gap-1 mb-2">
            <span className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-stone/70 backdrop-blur-sm text-xs">
              <FiStar className="text-rust-pale" size={10} />
              <span className="text-parchment font-mono text-[11px]">{movie.rating?.toFixed(1)}</span>
            </span>
            {moodPct > 0 && (
              <span className="px-2 py-0.5 rounded-md bg-rust/30 backdrop-blur-sm text-xs text-rust-pale font-mono">
                {moodPct}% match
              </span>
            )}
          </div>

          {/* AI Explanation Preview */}
          {movie.ai_explanation?.reasons?.[0] && (
            <p className="text-[10px] text-ash/80 line-clamp-2 mb-2 font-body">
              <FiInfo size={8} className="inline mr-1" />
              {movie.ai_explanation.reasons[0]}
            </p>
          )}

          {/* Actions */}
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              className={`p-1.5 rounded-lg transition-all ${saved ? 'bg-rust text-parchment' : 'bg-stone/60 backdrop-blur-sm text-ash hover:text-parchment hover:bg-stone-mid'}`}
            >
              <FiBookmark size={12} fill={saved ? 'currentColor' : 'none'} />
            </button>
          </div>
        </motion.div>

        {/* Cinematic Glow Border on Hover */}
        <motion.div
          initial={false}
          animate={{ opacity: hovered ? 1 : 0 }}
          className="absolute inset-0 rounded-xl pointer-events-none"
          style={{
            boxShadow: 'inset 0 0 30px rgba(139,58,42,0.15), 0 0 40px rgba(139,58,42,0.1)',
          }}
        />
      </div>

      {/* Title */}
      <div className="mt-2 px-1">
        <h3 className="font-body text-sm text-parchment/90 truncate group-hover:text-parchment transition-colors">
          {movie.title}
        </h3>
        <p className="text-[11px] text-stone-light font-body">
          {movie.release_date?.slice(0, 4)}
        </p>
      </div>
    </motion.div>
  )
}
