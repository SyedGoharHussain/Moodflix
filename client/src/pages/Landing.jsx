import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { FiTrendingUp, FiAward, FiArrowDown } from 'react-icons/fi'
import MoodInput from '../components/MoodInput.jsx'
import MovieCarousel from '../components/MovieCarousel.jsx'
import SkeletonCard from '../components/SkeletonCard.jsx'
import { movieAPI } from '../services/api.js'

export default function Landing() {
  const [trending, setTrending] = useState([])
  const [topRated, setTopRated] = useState([])
  const [popular, setPopular] = useState([])
  const [loading, setLoading] = useState(true)
  const [heroBg, setHeroBg] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [trendRes, topRes, popRes] = await Promise.all([
          movieAPI.trending('movie', 1),
          movieAPI.topRated('movie', 1),
          movieAPI.popular('movie', 1),
        ])
        setTrending(trendRes.data.results || [])
        setTopRated(topRes.data.results || [])
        setPopular(popRes.data.results || [])
        const candidates = (trendRes.data.results || []).filter(m => m.backdrop)
        if (candidates.length) setHeroBg(candidates[0].backdrop)
      } catch (err) {
        console.error('Failed to load data:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const handleMoodDetected = (mood) => {
    navigate(`/dashboard?mood=${mood}`)
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="min-h-screen bg-bg-base">
      {/* Hero */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0">
          {heroBg && (
            <motion.img
              initial={{ scale: 1.08, opacity: 0 }}
              animate={{ scale: 1, opacity: 0.45 }}
              transition={{ duration: 2.2 }}
              src={heroBg}
              alt=""
              className="w-full h-full object-cover"
            />
          )}
          <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-black/70 to-black" />
          <div className="absolute inset-0 bg-gradient-to-r from-black via-black/40 to-black" />
        </div>

        <div className="relative z-10 max-w-4xl mx-auto px-4 text-center pt-24 pb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <p className="text-accent-cyan text-[11px] uppercase tracking-[0.4em] mb-5 font-mono">
              AI · Mood-aware recommendations
            </p>
            <h1 className="font-display text-5xl sm:text-7xl lg:text-8xl text-ink mb-5 leading-[0.95] font-extrabold tracking-tight">
              Netflix, but it<br />
              <span className="bg-gradient-to-r from-accent-cyan via-white to-accent-mood bg-clip-text text-transparent">
                reads the room.
              </span>
            </h1>
            <p className="font-body text-base sm:text-lg text-ink-dim max-w-xl mx-auto mb-10 leading-relaxed">
              Tell us how you feel and our AI matches you to movies and shows
              tuned to your exact mood — with the reasoning shown.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
          >
            <MoodInput onMoodDetected={handleMoodDetected} />
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 1.2 }}
            className="mt-16 flex items-center justify-center gap-2 text-ink-mute text-xs font-mono uppercase tracking-widest"
          >
            <FiArrowDown size={12} className="animate-bounce" /> Scroll for trending
          </motion.div>
        </div>
      </section>

      {/* Carousels */}
      <section className="relative z-10 max-w-7xl mx-auto pt-8 pb-20">
        {loading ? (
          <div className="space-y-12">
            {[0, 1, 2].map(i => (
              <div key={i}>
                <div className="px-6 mb-3"><div className="h-6 w-48 rounded skeleton" /></div>
                <SkeletonCard />
              </div>
            ))}
          </div>
        ) : (
          <>
            <MovieCarousel title="Trending Now" subtitle="What everyone is watching this week" movies={trending} icon={FiTrendingUp} />
            <MovieCarousel title="Top Rated" subtitle="The highest-rated films of all time" movies={topRated} icon={FiAward} />
            <MovieCarousel title="Popular" subtitle="Fan favorites you can't miss" movies={popular} icon={FiTrendingUp} />
          </>
        )}
      </section>
    </motion.div>
  )
}
