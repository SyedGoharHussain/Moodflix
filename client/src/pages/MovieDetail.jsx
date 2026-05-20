import { useState, useEffect } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FiStar, FiClock, FiBookmark, FiPlay, FiChevronDown, FiCpu, FiGrid } from 'react-icons/fi'
import MovieCarousel from '../components/MovieCarousel.jsx'
import { movieAPI, userAPI } from '../services/api.js'
import { useAuthStore } from '../store/index.js'

const FEATURE_LABELS = {
  mood_signal:       { label: 'Mood signal',      desc: 'How strongly your current mood maps to this title' },
  genre_fit:         { label: 'Genre fit',        desc: "Overlap between your mood's preferred genres and this title's genres" },
  community_rating:  { label: 'Community rating', desc: 'Aggregate viewer rating from TMDB' },
  popularity_factor: { label: 'Popularity',       desc: 'How widely watched this title currently is' },
  history_alignment: { label: 'Your taste fit',   desc: 'Match to genres you have watched in the past' },
}

function Bar({ value }) {
  return (
    <div className="w-full h-1.5 bg-bg-hover rounded-full overflow-hidden">
      <motion.div
        initial={{ width: 0 }}
        whileInView={{ width: `${Math.max(0, Math.min(1, value)) * 100}%` }}
        viewport={{ once: true }}
        transition={{ duration: 0.9, ease: 'easeOut' }}
        className="h-full bg-gradient-to-r from-accent-cyan to-accent-mood rounded-full"
      />
    </div>
  )
}

export default function MovieDetail() {
  const { id } = useParams()
  const [searchParams] = useSearchParams()
  const type = searchParams.get('type') || 'movie'
  const { isAuthenticated } = useAuthStore()

  const [movie, setMovie] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saved, setSaved] = useState(false)
  const [showExpl, setShowExpl] = useState(true)

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
      <div className="min-h-screen pt-20 flex items-center justify-center bg-bg-base">
        <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
          className="w-8 h-8 border-2 border-accent-cyan/30 border-t-accent-cyan rounded-full" />
      </div>
    )
  }

  if (!movie) {
    return <div className="min-h-screen pt-20 flex items-center justify-center text-ink-dim bg-bg-base">Movie not found</div>
  }

  const trailer = movie.videos?.find(v => v.type === 'Trailer') || movie.videos?.[0]
  const director = movie.crew?.find(c => c.job === 'Director')
  const runtime = Array.isArray(movie.runtime) ? movie.runtime[0] : movie.runtime
  const ai = movie.ai_explanation || {}
  const scores = ai.scores || {}

  const featureBars = [
    { key: 'mood_signal',       value: (scores.mood_match ?? (ai.mood_match_pct || 0) / 100) },
    { key: 'genre_fit',         value: (ai.genre_similarity ?? 0) },
    { key: 'community_rating',  value: (movie.rating || 0) / 10 },
    { key: 'popularity_factor', value: Math.min(1, (movie.popularity || 0) / 500) },
  ]

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="min-h-screen bg-bg-base">
      <div className="relative h-[78vh] overflow-hidden">
        {movie.backdrop && (
          <motion.img initial={{ scale: 1.05 }} animate={{ scale: 1 }} transition={{ duration: 1.5 }}
            src={movie.backdrop} alt="" className="w-full h-full object-cover" />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/60 to-black/20" />
        <div className="absolute inset-0 bg-gradient-to-r from-black via-black/40 to-transparent" />

        <div className="absolute bottom-0 left-0 right-0 p-6 sm:p-12 max-w-7xl mx-auto">
          <div className="flex gap-8 items-end">
            <motion.div initial={{ opacity: 0, x: -24 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.25 }}
              className="hidden sm:block flex-shrink-0 w-48 rounded-md overflow-hidden shadow-2xl border border-line">
              <img src={movie.poster} alt={movie.title} className="w-full" />
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
              {movie.tagline && <p className="text-accent-cyan text-sm italic mb-2 font-body">{movie.tagline}</p>}
              <h1 className="font-display text-4xl sm:text-6xl text-ink mb-3 font-extrabold tracking-tight">{movie.title}</h1>
              <div className="flex flex-wrap items-center gap-4 mb-4 text-sm">
                <span className="flex items-center gap-1 text-yellow-400 font-mono">
                  <FiStar size={14} /> {movie.rating?.toFixed(1)}
                </span>
                {runtime > 0 && (
                  <span className="flex items-center gap-1 text-ink-dim font-mono">
                    <FiClock size={14} /> {runtime} min
                  </span>
                )}
                <span className="text-ink-dim font-mono">{movie.release_date?.slice(0, 4)}</span>
                {director && <span className="text-ink-dim">Dir. {director.name}</span>}
              </div>
              <div className="flex flex-wrap gap-2 mb-5">
                {movie.genres?.map(g => (
                  <span key={g} className="px-3 py-1 rounded-full text-xs bg-bg-card border border-line text-ink-dim">{g}</span>
                ))}
              </div>
              <div className="flex gap-3">
                {trailer && (
                  <a href={`https://youtube.com/watch?v=${trailer.key}`} target="_blank" rel="noreferrer"
                    className="flex items-center gap-2 px-6 py-3 bg-accent-red text-white rounded-md font-semibold text-sm hover:brightness-110 transition-all">
                    <FiPlay size={14} /> Watch Trailer
                  </a>
                )}
                <button onClick={() => setSaved(!saved)}
                  className={`flex items-center gap-2 px-5 py-3 rounded-md font-semibold text-sm transition-all ${saved
                    ? 'bg-accent-cyan/15 text-accent-cyan border border-accent-cyan/40'
                    : 'bg-white/10 text-ink border border-line hover:bg-white/20'}`}>
                  <FiBookmark size={14} fill={saved ? 'currentColor' : 'none'} />
                  {saved ? 'Saved' : 'Save'}
                </button>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-12">
        <motion.div initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="mb-12">
          <h2 className="font-display text-2xl text-ink mb-3 font-bold">Overview</h2>
          <p className="text-ink-dim font-body leading-relaxed max-w-3xl">{movie.overview}</p>
        </motion.div>

        {ai && (
          <motion.div initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="surface p-6 mb-12">
            <button onClick={() => setShowExpl(!showExpl)} className="w-full flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-md bg-accent-cyan/15 border border-accent-cyan/30 flex items-center justify-center">
                  <FiCpu className="text-accent-cyan" size={18} />
                </div>
                <div className="text-left">
                  <h3 className="font-display text-xl text-ink font-bold">Why this was recommended</h3>
                  <p className="text-xs text-ink-mute">Explainable AI · feature contributions</p>
                </div>
              </div>
              <FiChevronDown className={`text-ink-mute transition-transform ${showExpl ? 'rotate-180' : ''}`} />
            </button>

            {showExpl && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-6 space-y-5">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-4">
                  {featureBars.map(({ key, value }) => {
                    const meta = FEATURE_LABELS[key] || { label: key, desc: '' }
                    return (
                      <div key={key}>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm text-ink">{meta.label}</span>
                          <span className="text-xs font-mono text-accent-cyan">{Math.round((value || 0) * 100)}%</span>
                        </div>
                        <Bar value={value || 0} />
                        <p className="text-[11px] text-ink-mute mt-1">{meta.desc}</p>
                      </div>
                    )
                  })}
                </div>

                {ai.reasons?.length > 0 && (
                  <div className="pt-4 border-t border-line">
                    <p className="text-ink-mute text-[10px] uppercase tracking-widest mb-3">Reasoning</p>
                    <ul className="space-y-2">
                      {ai.reasons.map((r, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-ink-dim">
                          <span className="text-accent-cyan mt-0.5">·</span>
                          <span>{r}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </motion.div>
            )}
          </motion.div>
        )}

        {movie.cast?.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="mb-12">
            <h2 className="font-display text-2xl text-ink mb-4 font-bold">Cast</h2>
            <div className="flex gap-4 overflow-x-auto no-scrollbar pb-4">
              {movie.cast.slice(0, 10).map((c, i) => (
                <div key={i} className="flex-shrink-0 text-center">
                  <div className="w-20 h-20 rounded-full overflow-hidden mx-auto mb-2 bg-bg-card border border-line">
                    {c.profile
                      ? <img src={c.profile} alt={c.name} className="w-full h-full object-cover" />
                      : <div className="w-full h-full flex items-center justify-center text-ink-mute text-xs">—</div>}
                  </div>
                  <p className="text-xs text-ink font-body truncate w-20">{c.name}</p>
                  <p className="text-[10px] text-ink-mute truncate w-20">{c.character}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {movie.similar?.length > 0 && (
          <MovieCarousel title="Similar Titles" subtitle="You might also enjoy" movies={movie.similar} icon={FiGrid} />
        )}
      </div>
    </motion.div>
  )
}
