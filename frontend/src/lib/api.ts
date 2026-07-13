import axios from 'axios'
import { authClient, getStoredToken } from './auth-client'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
})

api.interceptors.request.use(async (config) => {
  const token = getStoredToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
    return config
  }
  try {
    const { data: sessionData } = await authClient.getSession()
    const sessionToken = (sessionData as any)?.session?.token
    if (sessionToken) {
      config.headers.Authorization = `Bearer ${sessionToken}`
    }
  } catch {
    // ignore
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && window.location.pathname !== '/login') {
      window.location.href = '/login'
    }
    return Promise.reject(err)
  },
)

export default api
