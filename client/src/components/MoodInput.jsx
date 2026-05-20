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
  { icon: FiSmile,          mood: 'happy',        label: 'Happy' },
  { icon: FiFrown,          mood: 'sad',          label: 'Sad' },
  { icon: FiMoon,           mood: 'lonely',       label: 'Lonely' },
  { icon: FiHeart,          mood: 'romantic',     label: 'Romantic' },
  { icon: FiZap,            mood: 'excited',      label: 'Excited' },
  { icon: FiSun,            mood: 'relaxed',      label: 'Relaxed' },
  { icon: FiCloud,          mood: 'stressed',     label: 'Stressed' },
  { icon: FiAlertTriangle,  mood: 'dark',         label: 'Dark' },
  { icon: FiActivity,       mood: 'emotional',    label: 'Emotional' },
  { icon: FiEye,            mood: 'mind-bending', label: 'Mind-Bending' },
  { icon: FiCompass,        mood: 'curious',      label: 'Curious' },
  { icon: FiClock,          mood: 'nostalgic',    label: 'Nostalgic' },
  { icon: FiTarget,         mood: 'motivated',    label: 'Motivated' },
  { icon: FiMap,            mood: 'adventurous',  label: 'Adventurous' },
  { icon: FiStar,           mood: 'wholesome',    label: 'Wholesome' },
  { icon: FiShield,         mood: 'scared',       label: 'Scared' },
]

function HighlightedText({ text, lime }) {
  if (!lime?.words?.length) return <span className="text-ink-dim">{text}</span>
  // Build a map of token -> weight (lowercased)
  const weights = {}
  for (const { word, weight } of lime.words) weights[word.toLowerCase()] = weight
  const tokens = text.split(/(\s+)/) // preserves whitespace
  return (
    <span className="leading-relaxed">
      {tokens.map((tok, i) => {
        if (!tok.trim()) return <span key={i}>{tok}</span>
        const w = weights[tok.toLowerCase().replace(/[^\w'-]/g, '')]
        if (w === undefined) return <span key={i} className="text-ink-dim">{tok}</span>
        const intensity = Math.min(1, Math.abs(w))
        const positive = w >= 0
        // Positive = cyan (drove the prediction); negative = red (worked against it)
        const bg = positive
          ? `rgba(0, 212, 255, ${0.10 + intensity * 0.45})`
          : `rgba(229, 9, 20, ${0.08 + intensity * 0.30})`
        return (
          <span
            key={i}
            className="text-ink rounded px-1 py-0.5"
            style={{ backgroundColor: bg, border: `1px solid rgba(255,255,255,0.04)` }}
            title={`weight: ${w.toFixed(2)}`}
          >
            {tok}
          </span>
        )
      })}
    </span>
  )
}

export default function MoodInput({ onMoodDetected }) {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [lastInput, setLastInput] = useState('')
  const { setMood } = useMoodStore()

  const analyzeMood = async (input) => {
    setLoading(true)
    setLastInput(input)
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

  return (
    <div className="w-full max-w-2xl mx-auto">
      <form onSubmit={handleSubmit} className="relative mb-6">
        <div className="surface relative p-1.5 focus-within:border-accent-cyan/60 focus-within:shadow-[0_0_0_3px_rgba(0,212,255,0.12)] transition-shadow">
          <input
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="How are you feeling right now?"
            className="w-full px-5 py-3.5 bg-transparent text-ink placeholder:text-ink-mute font-body text-base focus:outline-none"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !text.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 px-5 py-2 bg-accent-red text-white font-semibold text-sm rounded-md hover:brightness-110 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {loading ? (
              <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: 'linear' }} className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full" />
            ) : (
              'Analyze'
            )}
          </button>
        </div>
      </form>

      <div className="mb-6">
        <p className="text-center text-ink-mute text-xs tracking-widest uppercase mb-3">Or pick a mood</p>
        <div className="flex flex-wrap justify-center gap-2">
          {MOOD_ITEMS.map(({ icon: Icon, mood, label }) => (
            <motion.button
              key={mood}
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => analyzeMood(mood)}
              className="flex items-center gap-2 px-3 py-2 rounded-full bg-bg-card border border-line text-ink-dim hover:text-ink hover:border-accent-cyan/50 hover:bg-bg-hover transition-colors"
            >
              <Icon size={14} />
              <span className="text-xs font-medium">{label}</span>
            </motion.button>
          ))}
        </div>
      </div>

      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="surface p-6"
          >
            <div className="flex items-center justify-between mb-5">
              <div>
                <p className="text-ink-mute text-[10px] uppercase tracking-widest mb-1">Detected Mood</p>
                <h3 className="font-display text-3xl text-ink capitalize tracking-tight">{result.detected_mood}</h3>
              </div>
              <div className="text-right">
                <p className="text-ink-mute text-[10px] uppercase tracking-widest mb-1">Confidence</p>
                <p className="font-mono text-2xl text-accent-cyan">{Math.round(result.confidence * 100)}%</p>
              </div>
            </div>

            <div className="w-full h-1.5 bg-bg-hover rounded-full overflow-hidden mb-5">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${result.confidence * 100}%` }}
                transition={{ duration: 0.9, ease: 'easeOut' }}
                className="h-full bg-gradient-to-r from-accent-cyan to-accent-mood rounded-full"
              />
            </div>

            {result.emotion_breakdown && Object.keys(result.emotion_breakdown).length > 0 && (
              <div className="space-y-2 mb-5">
                <p className="text-ink-mute text-[10px] uppercase tracking-widest">Emotional Spectrum</p>
                {Object.entries(result.emotion_breakdown).slice(0, 4).map(([emotion, score]) => (
                  <div key={emotion} className="flex items-center gap-3">
                    <span className="text-xs text-ink-dim w-28 capitalize">{emotion}</span>
                    <div className="flex-1 h-1 bg-bg-hover rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${score * 100}%` }}
                        transition={{ duration: 0.8, delay: 0.2 }}
                        className="h-full bg-accent-cyan/70 rounded-full"
                      />
                    </div>
                    <span className="text-xs font-mono text-ink-dim w-10 text-right">{Math.round(score * 100)}%</span>
                  </div>
                ))}
              </div>
            )}

            {result.lime_explanation?.words?.length > 0 && (
              <div className="pt-4 border-t border-line">
                <p className="text-ink-mute text-[10px] uppercase tracking-widest mb-2">
                  Why this mood?
                  <span className="ml-2 text-ink-mute normal-case tracking-normal text-[11px]">
                    LIME · the highlighted words drove the prediction
                  </span>
                </p>
                <div className="text-sm font-body">
                  <HighlightedText text={lastInput} lime={result.lime_explanation} />
                </div>
                <div className="mt-3 flex items-center gap-4 text-[10px] text-ink-mute">
                  <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-sm" style={{ background: 'rgba(0,212,255,0.4)' }} /> pushed toward</span>
                  <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-sm" style={{ background: 'rgba(229,9,20,0.3)' }} /> pushed away</span>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
