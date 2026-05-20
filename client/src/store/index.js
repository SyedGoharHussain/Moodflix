import { create } from 'zustand'

export const useAuthStore = create((set) => ({
  user: JSON.parse(localStorage.getItem('moodflix_user') || 'null'),
  token: localStorage.getItem('moodflix_token') || null,
  isAuthenticated: !!localStorage.getItem('moodflix_token'),

  setAuth: (user, token) => {
    localStorage.setItem('moodflix_user', JSON.stringify(user))
    localStorage.setItem('moodflix_token', token)
    set({ user, token, isAuthenticated: true })
  },

  logout: () => {
    localStorage.removeItem('moodflix_user')
    localStorage.removeItem('moodflix_token')
    set({ user: null, token: null, isAuthenticated: false })
  },

  updateUser: (data) => {
    set((state) => {
      const updated = { ...state.user, ...data }
      localStorage.setItem('moodflix_user', JSON.stringify(updated))
      return { user: updated }
    })
  },
}))

export const useMoodStore = create((set) => ({
  currentMood: null,
  confidence: 0,
  emotionBreakdown: {},
  moodHistory: [],

  setMood: (mood, confidence, breakdown) =>
    set((state) => ({
      currentMood: mood,
      confidence,
      emotionBreakdown: breakdown || {},
      moodHistory: [
        { mood, confidence, timestamp: Date.now() },
        ...state.moodHistory.slice(0, 19),
      ],
    })),

  clearMood: () =>
    set({ currentMood: null, confidence: 0, emotionBreakdown: {} }),
}))

export const useUIStore = create((set) => ({
  searchOpen: false,
  sidebarOpen: false,
  toggleSearch: () => set((s) => ({ searchOpen: !s.searchOpen })),
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  closeAll: () => set({ searchOpen: false, sidebarOpen: false }),
}))
