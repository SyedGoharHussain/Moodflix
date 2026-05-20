import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('moodflix_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401s globally
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('moodflix_token')
      localStorage.removeItem('moodflix_user')
    }
    return Promise.reject(err)
  }
)

// Auth
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
  logout: () => api.post('/auth/logout'),
}

// Mood & Recommendations
export const moodAPI = {
  analyze: (text) => api.post('/analyze-mood', { text }),
  getRecommendations: (mood, page = 1) =>
    api.get(`/recommendations?mood=${mood}&page=${page}`),
  becauseYouFeel: (mood) => api.get(`/because-you-feel?mood=${mood}`),
}

// Movies
export const movieAPI = {
  trending: (type = 'all', page = 1) =>
    api.get(`/trending?type=${type}&page=${page}`),
  topRated: (type = 'movie', page = 1) =>
    api.get(`/top-rated?type=${type}&page=${page}`),
  popular: (type = 'movie', page = 1) =>
    api.get(`/popular?type=${type}&page=${page}`),
  details: (id, type = 'movie') =>
    api.get(`/movie/${id}?type=${type}`),
  search: (q, page = 1) =>
    api.get(`/search?q=${encodeURIComponent(q)}&page=${page}`),
  genres: (type = 'movie') => api.get(`/genres?type=${type}`),
}

// User
export const userAPI = {
  profile: () => api.get('/user/profile'),
  updateProfile: (data) => api.put('/user/profile', data),
  save: (movie) => api.post('/user/save', movie),
  unsave: (tmdbId) => api.delete(`/user/save/${tmdbId}`),
  getSaved: () => api.get('/user/saved'),
  rate: (data) => api.post('/user/rate', data),
  history: () => api.get('/user/history'),
  addToHistory: (movie) => api.post('/user/history', movie),
  moodHistory: () => api.get('/user/mood-history'),
}

export default api
