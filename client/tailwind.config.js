/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Backgrounds — pure black-on-black ladder
        bg: {
          base:     '#000000',
          elevated: '#0a0a0a',
          card:     '#141414',
          hover:    '#1f1f1f',
        },
        // Borders
        line: {
          subtle: '#1f1f1f',
          DEFAULT: '#262626',
          strong: '#3a3a3a',
        },
        // Text
        ink: {
          DEFAULT: '#ffffff',
          dim:     '#a3a3a3',
          mute:    '#6b6b6b',
          faint:   '#404040',
        },
        // Accents
        accent: {
          red:  '#e50914',   // Netflix-red, used very sparingly
          cyan: '#00d4ff',   // "intelligence" — AI / mood signals
          mood: '#7c5cff',   // calmer mood-pulse purple
        },
      },
      fontFamily: {
        display: ['"Manrope"', 'system-ui', 'sans-serif'],
        body: ['"Inter"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.6s ease-out both',
        'card-expand': 'cardExpand 0.35s cubic-bezier(.2,.8,.2,1) both',
        'mood-pulse': 'moodPulse 2.4s ease-in-out infinite',
        'shimmer': 'shimmer 1.6s linear infinite',
        'gradient-pan': 'gradientPan 18s ease infinite',
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(24px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        cardExpand: {
          '0%':   { transform: 'scale(1)',    boxShadow: '0 0 0 rgba(0,0,0,0)' },
          '100%': { transform: 'scale(1.08)', boxShadow: '0 20px 60px -10px rgba(0,0,0,0.95)' },
        },
        moodPulse: {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(0,212,255,0.0)' },
          '50%':      { boxShadow: '0 0 36px 0 rgba(0,212,255,0.35)' },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        gradientPan: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%':      { backgroundPosition: '100% 50%' },
        },
      },
      backgroundImage: {
        'fade-down': 'linear-gradient(180deg, rgba(0,0,0,0) 0%, #000 80%)',
        'fade-up':   'linear-gradient(0deg, rgba(0,0,0,0) 0%, #000 80%)',
        'fade-right':'linear-gradient(90deg, rgba(0,0,0,0) 0%, #000 100%)',
        'fade-left': 'linear-gradient(270deg, rgba(0,0,0,0) 0%, #000 100%)',
        'cyan-glow': 'radial-gradient(circle at 50% 0%, rgba(0,212,255,0.18) 0%, transparent 60%)',
      },
    },
  },
  plugins: [],
}
