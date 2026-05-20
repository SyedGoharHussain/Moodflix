import { useRef } from 'react'
import { motion } from 'framer-motion'
import { FiChevronLeft, FiChevronRight } from 'react-icons/fi'
import MovieCard from './MovieCard.jsx'

export default function MovieCarousel({ title, subtitle, movies = [], icon: Icon }) {
  const scrollRef = useRef(null)

  const scroll = (dir) => {
    if (!scrollRef.current) return
    const amount = dir === 'left' ? -600 : 600
    scrollRef.current.scrollBy({ left: amount, behavior: 'smooth' })
  }

  if (!movies.length) return null

  return (
    <motion.section
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-50px' }}
      transition={{ duration: 0.6 }}
      className="mb-12"
    >
      {/* Header */}
      <div className="flex items-end justify-between mb-4 px-4 sm:px-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            {Icon && <Icon size={18} className="text-rust-pale" />}
            <h2 className="font-display text-2xl sm:text-3xl text-parchment tracking-wide">{title}</h2>
          </div>
          {subtitle && (
            <p className="text-sm text-stone-light font-body">{subtitle}</p>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => scroll('left')}
            className="p-2 rounded-full glass hover:bg-stone-mid transition-all text-ash hover:text-parchment"
          >
            <FiChevronLeft size={16} />
          </button>
          <button
            onClick={() => scroll('right')}
            className="p-2 rounded-full glass hover:bg-stone-mid transition-all text-ash hover:text-parchment"
          >
            <FiChevronRight size={16} />
          </button>
        </div>
      </div>

      {/* Scrollable Row */}
      <div
        ref={scrollRef}
        className="flex gap-4 overflow-x-auto no-scrollbar px-4 sm:px-6 pb-4"
      >
        {movies.map((movie, i) => (
          <MovieCard key={movie.tmdb_id || i} movie={movie} index={i} />
        ))}
      </div>
    </motion.section>
  )
}
