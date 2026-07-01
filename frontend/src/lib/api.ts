import axios from 'axios'
import { authClient } from './auth-client'

const api = axios.create({
  baseURL: '/api',
})

api.interceptors.request.use(async (config) => {
  try {
    const { data: sessionData } = await authClient.getSession()
    const token = (sessionData as any)?.session?.token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
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
