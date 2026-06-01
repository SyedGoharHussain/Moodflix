import { useRef, useState, useEffect } from 'react'
import { motion, useInView } from 'framer-motion'
import { FiChevronLeft, FiChevronRight } from 'react-icons/fi'
import MovieCard from './MovieCard.jsx'

export default function MovieCarousel({ title, subtitle, movies = [], icon: Icon }) {
  const scrollRef = useRef(null)
  const sectionRef = useRef(null)
  const [hoverArrows, setHoverArrows] = useState(false)
  const [canScrollLeft, setCanScrollLeft] = useState(false)
  const [canScrollRight, setCanScrollRight] = useState(true)
  const isInView = useInView(sectionRef, { once: true, margin: '-80px' })

  const updateScrollState = () => {
    const el = scrollRef.current
    if (!el) return
    setCanScrollLeft(el.scrollLeft > 8)
    setCanScrollRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 8)
  }

  useEffect(() => {
    const el = scrollRef.current
    if (!el) return
    el.addEventListener('scroll', updateScrollState, { passive: true })
    updateScrollState()
    return () => el.removeEventListener('scroll', updateScrollState)
  }, [movies])

  const scroll = (dir) => {
    if (!scrollRef.current) return
    scrollRef.current.scrollBy({ left: dir === 'left' ? -620 : 620, behavior: 'smooth' })
  }

  if (!movies.length) return null

  return (
    <motion.section
      ref={sectionRef}
      initial={{ opacity: 0, y: 32 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className="mb-12"
      onMouseEnter={() => setHoverArrows(true)}
      onMouseLeave={() => setHoverArrows(false)}
    >
      {/* Header */}
      <div className="flex items-end justify-between mb-4 px-4 sm:px-6">
        <div>
          <div className="flex items-center gap-2.5">
            {Icon && (
              <div className="w-7 h-7 rounded-lg flex items-center justify-center"
                   style={{ background: 'rgba(0,212,255,0.1)', border: '1px solid rgba(0,212,255,0.2)' }}>
                <Icon size={13} style={{ color: '#00d4ff' }} />
              </div>
            )}
            <h2 className="font-display text-xl sm:text-2xl text-ink font-bold tracking-tight">
              {title}
            </h2>
          </div>
          {subtitle && (
            <p className="text-xs text-ink-mute mt-1 font-body ml-[2.375rem]">{subtitle}</p>
          )}
        </div>

        {/* Scroll indicators */}
        <div className="hidden sm:flex items-center gap-1 mr-1">
          <div className="flex gap-0.5">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="w-1 h-1 rounded-full"
                   style={{ background: i === 0 ? '#00d4ff' : 'rgba(255,255,255,0.15)' }} />
            ))}
          </div>
        </div>
      </div>

      {/* Carousel track */}
      <div className="relative group">
        {/* Left arrow */}
        <motion.button
          onClick={() => scroll('left')}
          aria-label="Scroll left"
          animate={{ opacity: hoverArrows && canScrollLeft ? 1 : 0 }}
          transition={{ duration: 0.2 }}
          className="absolute left-0 top-0 bottom-6 z-10 w-14 flex items-center justify-start pl-2"
          style={{
            background: 'linear-gradient(to right, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.6) 60%, transparent 100%)',
            pointerEvents: hoverArrows && canScrollLeft ? 'all' : 'none',
          }}
        >
          <motion.div
            whileHover={{ scale: 1.2, x: -2 }}
            whileTap={{ scale: 0.9 }}
            className="w-8 h-8 rounded-full flex items-center justify-center"
            style={{ background: 'rgba(255,255,255,0.12)', border: '1px solid rgba(255,255,255,0.15)' }}
          >
            <FiChevronLeft size={18} color="#fff" />
          </motion.div>
        </motion.button>

        {/* Right arrow */}
        <motion.button
          onClick={() => scroll('right')}
          aria-label="Scroll right"
          animate={{ opacity: hoverArrows && canScrollRight ? 1 : 0 }}
          transition={{ duration: 0.2 }}
          className="absolute right-0 top-0 bottom-6 z-10 w-14 flex items-center justify-end pr-2"
          style={{
            background: 'linear-gradient(to left, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.6) 60%, transparent 100%)',
            pointerEvents: hoverArrows && canScrollRight ? 'all' : 'none',
          }}
        >
          <motion.div
            whileHover={{ scale: 1.2, x: 2 }}
            whileTap={{ scale: 0.9 }}
            className="w-8 h-8 rounded-full flex items-center justify-center"
            style={{ background: 'rgba(255,255,255,0.12)', border: '1px solid rgba(255,255,255,0.15)' }}
          >
            <FiChevronRight size={18} color="#fff" />
          </motion.div>
        </motion.button>

        {/* Scroll track */}
        <div
          ref={scrollRef}
          className="flex gap-3 sm:gap-4 overflow-x-auto no-scrollbar px-4 sm:px-6 pb-6 pt-2 snap-x snap-mandatory"
          style={{ scrollPaddingLeft: '16px' }}
        >
          {movies.map((movie, i) => (
            <div key={movie.tmdb_id || i} className="snap-start flex-shrink-0">
              <MovieCard movie={movie} index={i} />
            </div>
          ))}
        </div>
      </div>
    </motion.section>
  )
}
