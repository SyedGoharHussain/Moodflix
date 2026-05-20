import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { FiTrendingUp, FiAward } from 'react-icons/fi'
import MoodInput from '../components/MoodInput.jsx'
import MovieCarousel from '../components/MovieCarousel.jsx'
import SkeletonCard from '../components/SkeletonCard.jsx'
import { movieAPI } from '../services/api.js'
import logo from '../assets/logo.png'

export default function Landing() {
  const [trending, setTrending] = useState([])
  const [topRated, setTopRated] = useState([])
  const [loading, setLoading] = useState(true)
  const [bgImage, setBgImage] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [trendRes, topRes] = await Promise.all([
          movieAPI.trending('movie', 1),
          movieAPI.topRated('movie', 1),
        ])
        setTrending(trendRes.data.results || [])
        setTopRated(topRes.data.results || [])
        if (trendRes.data.results?.[0]?.backdrop) {
          setBgImage(trendRes.data.results[0].backdrop)
        }
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
      className="min-h-screen"
    >
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Background */}
        <div className="absolute inset-0">
          {bgImage && (
            <motion.img
              initial={{ scale: 1.1, opacity: 0 }}
              animate={{ scale: 1, opacity: 0.25 }}
              transition={{ duration: 2 }}
              src={bgImage}
              alt=""
              className="w-full h-full object-cover"
            />
          )}
          <div className="absolute inset-0 bg-gradient-to-b from-stone/80 via-stone/60 to-stone" />
          <div className="absolute inset-0 bg-gradient-to-r from-stone via-transparent to-stone" />
        </div>

        {/* Floating Particles */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {[...Array(6)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 rounded-full bg-rust-pale/20"
              initial={{ x: `${20 + i * 15}%`, y: '110%' }}
              animate={{ y: '-10%', opacity: [0, 0.6, 0] }}
              transition={{ duration: 8 + i * 2, repeat: Infinity, delay: i * 1.5, ease: 'linear' }}
            />
          ))}
        </div>

        {/* Content */}
        <div className="relative z-10 max-w-4xl mx-auto px-4 text-center pt-20">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
          >
            {/* Logo */}
            <motion.img
              src={logo}
              alt="MoodFlix"
              className="h-32 sm:h-40 mx-auto mb-6"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            />

            <p className="text-rust-pale text-sm uppercase tracking-[0.3em] mb-4 font-body">
              AI-Powered Recommendations
            </p>
            <h1 className="font-display text-5xl sm:text-7xl lg:text-8xl text-parchment mb-6 leading-tight">
              Feel. Discover.
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-rust-pale via-rust to-rust-deep">
                Watch.
              </span>
            </h1>
            <p className="font-body text-lg sm:text-xl text-ash max-w-2xl mx-auto mb-12 leading-relaxed">
              Tell us how you're feeling, and our AI will curate the perfect movies
              and shows — tailored to your emotional state.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            <MoodInput onMoodDetected={handleMoodDetected} />
          </motion.div>
        </div>

        {/* Scroll Indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2"
        >
          <motion.div
            animate={{ y: [0, 8, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-5 h-8 border-2 border-ash/30 rounded-full flex items-start justify-center pt-1.5"
          >
            <div className="w-1 h-2 bg-rust-pale rounded-full" />
          </motion.div>
        </motion.div>
      </section>

      {/* Content Sections */}
      <section className="relative z-10 max-w-7xl mx-auto pt-8 pb-20">
        {loading ? (
          <div className="space-y-12">
            <div>
              <div className="px-6 mb-4">
                <div className="h-8 w-48 rounded skeleton" />
              </div>
              <SkeletonCard />
            </div>
            <div>
              <div className="px-6 mb-4">
                <div className="h-8 w-48 rounded skeleton" />
              </div>
              <SkeletonCard />
            </div>
          </div>
        ) : (
          <>
            <MovieCarousel
              title="Trending Now"
              subtitle="What everyone is watching this week"
              movies={trending}
              icon={FiTrendingUp}
            />
            <MovieCarousel
              title="Top Rated"
              subtitle="The highest rated films of all time"
              movies={topRated}
              icon={FiAward}
            />
          </>
        )}
      </section>
    </motion.div>
  )
}
