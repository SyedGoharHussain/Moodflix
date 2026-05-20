import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FiFilm } from 'react-icons/fi'
import MovieCard from '../components/MovieCard.jsx'
import SkeletonCard from '../components/SkeletonCard.jsx'
import { movieAPI } from '../services/api.js'

export default function Search() {
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q') || ''
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!query) return
    const search = async () => {
      setLoading(true)
      try {
        const res = await movieAPI.search(query)
        setResults(res.data.results || [])
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    search()
  }, [query])

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="min-h-screen pt-24 pb-20 max-w-7xl mx-auto px-4 sm:px-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <h1 className="font-display text-4xl text-parchment mb-2">
          {query ? <>Results for "<span className="text-rust-pale">{query}</span>"</> : 'Search'}
        </h1>
        {results.length > 0 && <p className="text-ash text-sm">{results.length} titles found</p>}
      </motion.div>

      {loading ? (
        <SkeletonCard count={12} />
      ) : results.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {results.map((movie, i) => (
            <MovieCard key={movie.tmdb_id || i} movie={movie} index={i} />
          ))}
        </div>
      ) : query ? (
        <div className="text-center py-20">
          <FiFilm size={48} className="mx-auto text-stone-light mb-4" />
          <p className="text-ash font-body">No results found for "{query}"</p>
        </div>
      ) : null}
    </motion.div>
  )
}
