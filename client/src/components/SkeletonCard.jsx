import { motion } from 'framer-motion'

export default function SkeletonCard({ count = 6 }) {
  return (
    <div className="flex gap-3 sm:gap-4 overflow-hidden px-4 sm:px-6">
      {Array.from({ length: count }).map((_, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: i * 0.06 }}
          className="flex-shrink-0 w-[170px] sm:w-[190px]"
        >
          <div className="aspect-[2/3] rounded-md skeleton" />
          <div className="mt-2 space-y-1.5 px-0.5">
            <div className="h-3 w-3/4 rounded skeleton" />
            <div className="h-2 w-1/2 rounded skeleton" />
          </div>
        </motion.div>
      ))}
    </div>
  )
}
