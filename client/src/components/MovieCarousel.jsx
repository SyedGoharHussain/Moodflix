import { useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { FiChevronLeft, FiChevronRight } from 'react-icons/fi'
import MovieCard from './MovieCard.jsx'

export default function MovieCarousel({ title, subtitle, movies = [], icon: Icon }) {
  const scrollRef = useRef(null)
  const [hoverArrows, setHoverArrows] = useState(false)

  const scroll = (dir) => {
    if (!scrollRef.current) return
    const amount = dir === 'left' ? -640 : 640
    scrollRef.current.scrollBy({ left: amount, behavior: 'smooth' })
  }

  if (!movies.length) return null

  return (
    <motion.section
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="mb-10"
      onMouseEnter={() => setHoverArrows(true)}
      onMouseLeave={() => setHoverArrows(false)}
    >
      <div className="flex items-end justify-between mb-3 px-4 sm:px-6">
        <div>
          <div className="flex items-center gap-2">
            {Icon && <Icon size={14} className="text-accent-cyan" />}
            <h2 className="font-display text-xl sm:text-2xl text-ink font-bold tracking-tight">{title}</h2>
          </div>
          {subtitle && <p className="text-xs text-ink-mute mt-0.5 font-body">{subtitle}</p>}
        </div>
      </div>

      <div className="relative group">
        {/* Left chevron */}
        <button
          onClick={() => scroll('left')}
          aria-label="Scroll left"
          className={`absolute left-0 top-1/2 -translate-y-1/2 z-10 h-32 w-12 bg-gradient-to-r from-black to-transparent text-ink hover:text-accent-cyan transition-opacity ${hoverArrows ? 'opacity-100' : 'opacity-0'}`}
        >
          <FiChevronLeft size={24} className="ml-2" />
        </button>
        {/* Right chevron */}
        <button
          onClick={() => scroll('right')}
          aria-label="Scroll right"
          className={`absolute right-0 top-1/2 -translate-y-1/2 z-10 h-32 w-12 bg-gradient-to-l from-black to-transparent text-ink hover:text-accent-cyan transition-opacity flex items-center justify-end ${hoverArrows ? 'opacity-100' : 'opacity-0'}`}
        >
          <FiChevronRight size={24} className="mr-2" />
        </button>

        <div
          ref={scrollRef}
          className="flex gap-3 sm:gap-4 overflow-x-auto no-scrollbar px-4 sm:px-6 pb-6 pt-2 snap-x snap-mandatory"
          style={{ scrollPaddingLeft: '24px' }}
        >
          {movies.map((movie, i) => (
            <div key={movie.tmdb_id || i} className="snap-start">
              <MovieCard movie={movie} index={i} />
            </div>
          ))}
        </div>
      </div>
    </motion.section>
  )
}
