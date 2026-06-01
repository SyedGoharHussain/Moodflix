import { useState, useEffect, useRef } from 'react'
import { motion, useScroll, useTransform } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { FiTrendingUp, FiAward, FiArrowDown, FiStar } from 'react-icons/fi'
import MoodInput from '../components/MoodInput.jsx'
import MovieCarousel from '../components/MovieCarousel.jsx'
import SkeletonCard from '../components/SkeletonCard.jsx'
import { movieAPI } from '../services/api.js'

export default function Landing() {
  const [trending, setTrending] = useState([])
  const [topRated, setTopRated] = useState([])
  const [popular, setPopular]   = useState([])
  const [loading, setLoading]   = useState(true)
  const [heroBg, setHeroBg]     = useState('')
  const navigate = useNavigate()
  const heroRef  = useRef(null)

  // Parallax transforms driven by scroll
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ['start start', 'end start'] })
  const heroScale   = useTransform(scrollYProgress, [0, 1], [1, 1.1])
  const heroOpacity = useTransform(scrollYProgress, [0, 0.55], [0.4, 0])
  const heroY       = useTransform(scrollYProgress, [0, 1], [0, 100])
  const contentY    = useTransform(scrollYProgress, [0, 1], [0, -40])

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
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.6 }}
      className="min-h-screen bg-bg-base"
    >
      {/* ─── HERO ──────────────────────────────────── */}
      <section ref={heroRef} className="relative min-h-screen flex items-center justify-center overflow-hidden">

        {/* Parallax backdrop image */}
        <div className="absolute inset-0">
          {heroBg && (
            <motion.img
              initial={{ scale: 1.15, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 3, ease: [0.16, 1, 0.3, 1] }}
              style={{ scale: heroScale, opacity: heroOpacity, y: heroY }}
              src={heroBg}
              alt=""
              className="w-full h-full object-cover"
            />
          )}

          {/* Gradient overlays */}
          <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/40 to-[#000]" />
          <div className="absolute inset-0 bg-gradient-to-r from-black/60 via-transparent to-black/60" />

          {/* Scanlines */}
          <div className="scanlines" />

          {/* Vignette */}
          <div className="vignette" />

          {/* Top glow */}
          <div
            className="absolute pointer-events-none"
            style={{
              top: '-8%',
              left: '50%',
              transform: 'translateX(-50%)',
              width: 'min(1000px, 80vw)',
              height: '350px',
              background: 'radial-gradient(ellipse, rgba(0,212,255,0.06) 0%, transparent 70%)',
            }}
          />
        </div>

        {/* Hero content */}
        <motion.div
          style={{ y: contentY }}
          className="relative z-10 max-w-4xl mx-auto px-4 text-center pt-24 pb-16"
        >
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: -12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full mb-8 pulse-badge"
            style={{
              background: 'rgba(0,212,255,0.06)',
              border: '1px solid rgba(0,212,255,0.2)',
            }}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-accent-cyan animate-pulse" />
            <span className="text-accent-cyan text-[10px] uppercase tracking-[0.4em] font-mono font-medium">
              AI-Powered Mood Engine
            </span>
          </motion.div>

          {/* Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="font-display font-extrabold tracking-tight leading-[0.9] mb-6"
            style={{ fontSize: 'clamp(2.8rem, 7.5vw, 5.5rem)' }}
          >
            Netflix, but it
            <br />
            <span className="gradient-text">reads the room.</span>
          </motion.h1>

          {/* Sub-headline */}
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.5 }}
            className="font-body text-base sm:text-lg text-ink-dim max-w-md mx-auto mb-12 leading-relaxed"
          >
            Tell us how you feel. Our AI maps your emotion to the perfect film
            — with transparent, explainable reasoning.
          </motion.p>

          {/* Mood input */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6, ease: [0.16, 1, 0.3, 1] }}
          >
            <MoodInput onMoodDetected={handleMoodDetected} />
          </motion.div>

          {/* Scroll indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            transition={{ duration: 0.5, delay: 1.6 }}
            className="mt-16 flex flex-col items-center gap-2 text-ink-mute"
          >
            <span className="text-[9px] font-mono uppercase tracking-[0.3em]">Explore</span>
            <motion.div
              animate={{ y: [0, 5, 0] }}
              transition={{ duration: 1.8, repeat: Infinity, ease: 'easeInOut' }}
            >
              <FiArrowDown size={13} />
            </motion.div>
          </motion.div>
        </motion.div>
      </section>

      {/* ─── CAROUSELS ─────────────────────────────── */}
      <section className="relative z-10 max-w-7xl mx-auto pt-8 pb-24">
        {loading ? (
          <div className="space-y-14">
            {[0, 1, 2].map(i => (
              <div key={i}>
                <div className="px-6 mb-4 flex items-center gap-3">
                  <div className="h-5 w-5 rounded-full skeleton" />
                  <div className="h-6 w-52 rounded skeleton" />
                </div>
                <SkeletonCard />
              </div>
            ))}
          </div>
        ) : (
          <>
            <MovieCarousel title="Trending Now" subtitle="What the world is watching this week"   movies={trending} icon={FiTrendingUp} />
            <MovieCarousel title="Top Rated"    subtitle="The highest-rated films of all time"    movies={topRated} icon={FiAward} />
            <MovieCarousel title="Popular"      subtitle="Fan favorites you can't miss"           movies={popular}  icon={FiStar} />
          </>
        )}
      </section>
    </motion.div>
  )
}
