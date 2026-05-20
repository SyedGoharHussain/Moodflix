import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FiTarget, FiTrendingUp, FiAward, FiFilm } from 'react-icons/fi'
import MoodInput from '../components/MoodInput.jsx'
import MovieCarousel from '../components/MovieCarousel.jsx'
import SkeletonCard from '../components/SkeletonCard.jsx'
import { movieAPI, moodAPI } from '../services/api.js'
import { useMoodStore } from '../store/index.js'

export default function Dashboard() {
  const [searchParams] = useSearchParams()
  const initialMood = searchParams.get('mood')
  const { currentMood } = useMoodStore()
  const activeMood = currentMood || initialMood

  const [trending, setTrending] = useState([])
  const [topRated, setTopRated] = useState([])
  const [moodPicks, setMoodPicks] = useState([])
  const [popular, setPopular] = useState([])
  const [loading, setLoading] = useState(true)
  const [moodLoading, setMoodLoading] = useState(false)

  useEffect(() => {
    const fetchBase = async () => {
      try {
        const [t, r, p] = await Promise.all([
          movieAPI.trending('movie', 1),
          movieAPI.topRated('movie', 1),
          movieAPI.popular('movie', 1),
        ])
        setTrending(t.data.results || [])
        setTopRated(r.data.results || [])
        setPopular(p.data.results || [])
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetchBase()
  }, [])

  useEffect(() => {
    if (!activeMood) return
    const fetchMoodPicks = async () => {
      setMoodLoading(true)
      try {
        const res = await moodAPI.getRecommendations(activeMood, 1)
        setMoodPicks(res.data.results || [])
      } catch (err) {
        console.error(err)
      } finally {
        setMoodLoading(false)
      }
    }
    fetchMoodPicks()
  }, [activeMood])

  const handleMoodDetected = () => {
    // Mood picks will auto-update via the useEffect
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="min-h-screen pt-24 pb-20"
    >
      {/* Mood Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 mb-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="font-display text-4xl sm:text-5xl text-parchment mb-3">
            {activeMood
              ? <>Because You Feel <span className="text-rust-pale capitalize">{activeMood}</span></>
              : 'How are you feeling?'}
          </h1>
          <p className="text-ash font-body">
            {activeMood
              ? 'Here are your AI-curated recommendations'
              : 'Tell us your mood and we\'ll find the perfect watch'}
          </p>
        </motion.div>
        <MoodInput onMoodDetected={handleMoodDetected} />
      </section>

      {/* Mood-Based Recommendations */}
      {activeMood && (
        <section className="max-w-7xl mx-auto">
          {moodLoading ? (
            <div className="mb-12">
              <div className="px-6 mb-4"><div className="h-8 w-64 rounded skeleton" /></div>
              <SkeletonCard />
            </div>
          ) : moodPicks.length > 0 ? (
            <MovieCarousel
              title={`Because You Feel ${activeMood.charAt(0).toUpperCase() + activeMood.slice(1)}`}
              subtitle="AI-curated picks based on your emotional state"
              movies={moodPicks}
              icon={FiTarget}
            />
          ) : null}
        </section>
      )}

      {/* Other Sections */}
      <section className="max-w-7xl mx-auto">
        {loading ? (
          <div className="space-y-12">
            {[1, 2, 3].map(i => (
              <div key={i}>
                <div className="px-6 mb-4"><div className="h-8 w-48 rounded skeleton" /></div>
                <SkeletonCard />
              </div>
            ))}
          </div>
        ) : (
          <>
            <MovieCarousel title="Trending Now" subtitle="What the world is watching" movies={trending} icon={FiTrendingUp} />
            <MovieCarousel title="Top Rated" subtitle="Critically acclaimed masterpieces" movies={topRated} icon={FiAward} />
            <MovieCarousel title="Popular" subtitle="Fan favorites everyone loves" movies={popular} icon={FiFilm} />
          </>
        )}
      </section>
    </motion.div>
  )
}
