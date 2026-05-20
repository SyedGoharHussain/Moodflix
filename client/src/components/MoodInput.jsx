import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FiSmile, FiFrown, FiHeart, FiZap, FiSun, FiCloud,
  FiMoon, FiEye, FiCompass, FiClock, FiTarget,
  FiMap, FiShield, FiAlertTriangle, FiStar, FiActivity
} from 'react-icons/fi'
import { moodAPI } from '../services/api.js'
import { useMoodStore } from '../store/index.js'

const MOOD_ITEMS = [
  { icon: FiSmile, mood: 'happy', label: 'Happy', color: '#C47555' },
  { icon: FiFrown, mood: 'sad', label: 'Sad', color: '#6B5C57' },
  { icon: FiMoon, mood: 'lonely', label: 'Lonely', color: '#6B5C57' },
  { icon: FiHeart, mood: 'romantic', label: 'Romantic', color: '#C47555' },
  { icon: FiZap, mood: 'excited', label: 'Excited', color: '#C47555' },
  { icon: FiSun, mood: 'relaxed', label: 'Relaxed', color: '#B8ABA4' },
  { icon: FiCloud, mood: 'stressed', label: 'Stressed', color: '#6B5C57' },
  { icon: FiAlertTriangle, mood: 'dark', label: 'Dark', color: '#5C2218' },
  { icon: FiActivity, mood: 'emotional', label: 'Emotional', color: '#8B3A2A' },
  { icon: FiEye, mood: 'mind-bending', label: 'Mind-Bending', color: '#8B3A2A' },
  { icon: FiCompass, mood: 'curious', label: 'Curious', color: '#B8ABA4' },
  { icon: FiClock, mood: 'nostalgic', label: 'Nostalgic', color: '#C47555' },
  { icon: FiTarget, mood: 'motivated', label: 'Motivated', color: '#8B3A2A' },
  { icon: FiMap, mood: 'adventurous', label: 'Adventurous', color: '#C47555' },
  { icon: FiStar, mood: 'wholesome', label: 'Wholesome', color: '#C47555' },
  { icon: FiShield, mood: 'scared', label: 'Scared', color: '#5C2218' },
]

export default function MoodInput({ onMoodDetected }) {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const { setMood } = useMoodStore()

  const analyzeMood = async (input) => {
    setLoading(true)
    try {
      const { data } = await moodAPI.analyze(input)
      setResult(data)
      setMood(data.detected_mood, data.confidence, data.emotion_breakdown)
      onMoodDetected?.(data.detected_mood, data.confidence)
    } catch (err) {
      console.error('Mood analysis failed:', err)
      const fallbackMood = input.toLowerCase().trim()
      const found = MOOD_ITEMS.find(m => m.mood === fallbackMood || m.label.toLowerCase() === fallbackMood)
      if (found) {
        setMood(found.mood, 0.8, { [found.mood]: 0.8 })
        onMoodDetected?.(found.mood, 0.8)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (text.trim()) analyzeMood(text.trim())
  }

  const handleMoodClick = (mood) => {
    analyzeMood(mood)
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Text Input */}
      <form onSubmit={handleSubmit} className="relative mb-6">
        <div className="relative group">
          <div className="absolute -inset-0.5 bg-gradient-to-r from-rust via-rust-pale to-rust rounded-2xl opacity-30 group-hover:opacity-50 blur transition-opacity" />
          <div className="relative glass rounded-2xl p-1">
            <input
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="How are you feeling right now?"
              className="w-full px-6 py-4 bg-transparent text-parchment placeholder:text-stone-light font-body text-lg focus:outline-none"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !text.trim()}
              className="absolute right-3 top-1/2 -translate-y-1/2 px-5 py-2 bg-gradient-to-r from-rust to-rust-deep text-parchment font-body text-sm rounded-xl hover:from-rust-pale hover:to-rust transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-lg shadow-rust/20"
            >
              {loading ? (
                <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: 'linear' }} className="w-5 h-5 border-2 border-parchment/30 border-t-parchment rounded-full" />
              ) : (
                'Analyze'
              )}
            </button>
          </div>
        </div>
      </form>

      {/* Mood Picker with Icons */}
      <div className="mb-6">
        <p className="text-center text-ash text-sm mb-4 font-body">Or pick your mood</p>
        <div className="flex flex-wrap justify-center gap-2">
          {MOOD_ITEMS.map(({ icon: Icon, mood, label, color }) => (
            <motion.button
              key={mood}
              whileHover={{ scale: 1.1, y: -3 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleMoodClick(mood)}
              className="flex flex-col items-center gap-1.5 px-3 py-2.5 rounded-xl hover:bg-stone-mid/60 transition-all group"
              title={label}
            >
              <div
                className="w-9 h-9 rounded-lg flex items-center justify-center transition-all group-hover:shadow-lg"
                style={{ backgroundColor: `${color}20`, border: `1px solid ${color}30` }}
              >
                <Icon size={16} style={{ color }} className="group-hover:scale-110 transition-transform" />
              </div>
              <span className="text-[10px] text-stone-light group-hover:text-ash transition-colors font-body">{label}</span>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Confidence Result */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10 }}
            className="glass rounded-2xl p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-ash text-xs uppercase tracking-widest mb-1">Detected Mood</p>
                <h3 className="font-display text-3xl text-parchment capitalize">{result.detected_mood}</h3>
              </div>
              <div className="text-right">
                <p className="text-ash text-xs uppercase tracking-widest mb-1">Confidence</p>
                <p className="font-mono text-2xl text-rust-pale">{Math.round(result.confidence * 100)}%</p>
              </div>
            </div>

            {/* Confidence Bar */}
            <div className="w-full h-2 bg-stone-mid rounded-full overflow-hidden mb-4">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${result.confidence * 100}%` }}
                transition={{ duration: 1, ease: 'easeOut' }}
                className="h-full bg-gradient-to-r from-rust to-rust-pale rounded-full"
              />
            </div>

            {/* Emotion Breakdown */}
            {result.emotion_breakdown && Object.keys(result.emotion_breakdown).length > 0 && (
              <div className="space-y-2">
                <p className="text-ash text-xs uppercase tracking-widest">Emotional Spectrum</p>
                {Object.entries(result.emotion_breakdown).slice(0, 4).map(([emotion, score]) => (
                  <div key={emotion} className="flex items-center gap-3">
                    <span className="text-xs text-stone-light w-24 capitalize">{emotion}</span>
                    <div className="flex-1 h-1.5 bg-stone-mid rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${score * 100}%` }}
                        transition={{ duration: 0.8, delay: 0.2 }}
                        className="h-full bg-rust-pale/70 rounded-full"
                      />
                    </div>
                    <span className="text-xs font-mono text-ash w-10 text-right">{Math.round(score * 100)}%</span>
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
