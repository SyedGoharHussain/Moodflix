import { useState, useEffect } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FiStar, FiClock, FiBookmark, FiPlay, FiChevronDown, FiCpu, FiGrid } from 'react-icons/fi'
import MovieCarousel from '../components/MovieCarousel.jsx'
import { movieAPI, userAPI } from '../services/api.js'
import { useAuthStore } from '../store/index.js'

export default function MovieDetail() {
  const { id } = useParams()
  const [searchParams] = useSearchParams()
  const type = searchParams.get('type') || 'movie'
  const { isAuthenticated } = useAuthStore()

  const [movie, setMovie] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saved, setSaved] = useState(false)
  const [showExpl, setShowExpl] = useState(false)

  useEffect(() => {
    const fetchMovie = async () => {
      setLoading(true)
      try {
        const res = await movieAPI.details(id, type)
        setMovie(res.data)
        if (isAuthenticated) {
          await userAPI.addToHistory({
            tmdb_id: res.data.tmdb_id,
            title: res.data.title,
            poster: res.data.poster,
            media_type: type,
          })
        }
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetchMovie()
  }, [id, type])

  if (loading) {
    return (
      <div className="min-h-screen pt-20 flex items-center justify-center">
        <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
          className="w-8 h-8 border-2 border-rust-pale/30 border-t-rust-pale rounded-full" />
      </div>
    )
  }

  if (!movie) {
    return <div className="min-h-screen pt-20 flex items-center justify-center text-ash">Movie not found</div>
  }

  const trailer = movie.videos?.find(v => v.type === 'Trailer') || movie.videos?.[0]
  const director = movie.crew?.find(c => c.job === 'Director')
  const runtime = Array.isArray(movie.runtime) ? movie.runtime[0] : movie.runtime

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="min-h-screen">
      {/* Backdrop */}
      <div className="relative h-[70vh] overflow-hidden">
        {movie.backdrop && (
          <motion.img initial={{ scale: 1.05 }} animate={{ scale: 1 }} transition={{ duration: 1.5 }}
            src={movie.backdrop} alt="" className="w-full h-full object-cover" />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-stone via-stone/50 to-stone/30" />
        <div className="absolute inset-0 bg-gradient-to-r from-stone/80 via-transparent to-stone/30" />

        {/* Content Overlay */}
        <div className="absolute bottom-0 left-0 right-0 p-6 sm:p-12 max-w-7xl mx-auto">
          <div className="flex gap-8 items-end">
            {/* Poster */}
            <motion.div initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}
              className="hidden sm:block flex-shrink-0 w-48 rounded-xl overflow-hidden shadow-2xl shadow-stone/50 border border-line">
              <img src={movie.poster} alt={movie.title} className="w-full" />
            </motion.div>

            {/* Info */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
              {movie.tagline && <p className="text-rust-pale text-sm italic mb-2 font-body">{movie.tagline}</p>}
              <h1 className="font-display text-4xl sm:text-6xl text-parchment mb-3">{movie.title}</h1>
              <div className="flex flex-wrap items-center gap-3 mb-4 text-sm">
                <span className="flex items-center gap-1 text-rust-pale">
                  <FiStar size={14} /> {movie.rating?.toFixed(1)}
                </span>
                {runtime > 0 && (
                  <span className="flex items-center gap-1 text-ash">
                    <FiClock size={14} /> {runtime} min
                  </span>
                )}
                <span className="text-ash">{movie.release_date?.slice(0, 4)}</span>
                {director && <span className="text-ash">Dir. {director.name}</span>}
              </div>
              <div className="flex flex-wrap gap-2 mb-4">
                {movie.genres?.map(g => (
                  <span key={g} className="px-3 py-1 rounded-full text-xs glass text-ash">{g}</span>
                ))}
              </div>
              <div className="flex gap-3">
                {trailer && (
                  <a href={`https://youtube.com/watch?v=${trailer.key}`} target="_blank" rel="noreferrer"
                    className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-rust to-rust-deep text-parchment rounded-xl font-body text-sm hover:from-rust-pale hover:to-rust transition-all shadow-lg shadow-rust/30">
                    <FiPlay size={14} /> Watch Trailer
                  </a>
                )}
                <button onClick={() => setSaved(!saved)}
                  className={`flex items-center gap-2 px-5 py-3 rounded-xl font-body text-sm transition-all ${saved ? 'bg-rust/20 text-rust-pale border border-rust/30' : 'glass text-ash hover:text-parchment'}`}>
                  <FiBookmark size={14} fill={saved ? 'currentColor' : 'none'} />
                  {saved ? 'Saved' : 'Save'}
                </button>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Details Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-12">
        {/* Overview */}
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
          className="mb-12">
          <h2 className="font-display text-2xl text-parchment mb-4">Overview</h2>
          <p className="text-ash font-body leading-relaxed max-w-3xl">{movie.overview}</p>
        </motion.div>

        {/* AI Explanation Panel */}
        {movie.ai_explanation && (
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="glass rounded-2xl p-6 mb-12">
            <button onClick={() => setShowExpl(!showExpl)}
              className="w-full flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-rust to-rust-deep flex items-center justify-center">
                  <FiCpu className="text-parchment" size={18} />
                </div>
                <div className="text-left">
                  <h3 className="font-display text-xl text-parchment">AI Recommendation Insight</h3>
                  <p className="text-xs text-ash">Why this was recommended for you</p>
                </div>
              </div>
              <FiChevronDown className={`text-ash transition-transform ${showExpl ? 'rotate-180' : ''}`} />
            </button>
            {showExpl && (
              <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
                className="mt-4 pt-4 border-t border-line space-y-3">
                {movie.ai_explanation.reasons?.map((r, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <span className="text-rust-pale mt-0.5">•</span>
                    <p className="text-sm text-ash font-body">{r}</p>
                  </div>
                ))}
              </motion.div>
            )}
          </motion.div>
        )}

        {/* Cast */}
        {movie.cast?.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="mb-12">
            <h2 className="font-display text-2xl text-parchment mb-4">Cast</h2>
            <div className="flex gap-4 overflow-x-auto no-scrollbar pb-4">
              {movie.cast.slice(0, 10).map((c, i) => (
                <div key={i} className="flex-shrink-0 text-center">
                  <div className="w-20 h-20 rounded-full overflow-hidden mx-auto mb-2 bg-stone-mid">
                    {c.profile ? <img src={c.profile} alt={c.name} className="w-full h-full object-cover" /> :
                      <div className="w-full h-full flex items-center justify-center text-stone-light text-xs">No img</div>}
                  </div>
                  <p className="text-xs text-parchment font-body truncate w-20">{c.name}</p>
                  <p className="text-[10px] text-stone-light truncate w-20">{c.character}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Similar */}
        {movie.similar?.length > 0 && (
          <MovieCarousel title="Similar Titles" subtitle="You might also enjoy" movies={movie.similar} icon={FiGrid} />
        )}
      </div>
    </motion.div>
  )
}
