import { ref } from 'vue'
import { authClient, getStoredToken, setStoredToken } from '@/lib/auth-client'
import api from '@/lib/api'

interface User {
  id: string
  name: string
  email: string
  role: string
  phone: string | null
  suspended: boolean
  isSupreme: boolean
}

const user = ref<User | null>(null)
const loading = ref(true)
let initialized = false
let fetchPromise: Promise<void> | null = null
let requestId = 0

export { user, loading }

function authHeaders(): Record<string, string> {
  const token = getStoredToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function fetchSession(force = false) {
  if (fetchPromise && !force) {
    return fetchPromise
  }

  const currentRequestId = ++requestId
  loading.value = true
  fetchPromise = (async () => {
    try {
      const timeoutPromise = new Promise<never>((_, reject) =>
        setTimeout(() => reject(new Error('Auth request timed out')), 10000)
      )
      const sessionPromise = authClient.getSession({
        fetchOptions: {
          credentials: 'include',
          headers: authHeaders(),
        },
      } as any)
      const result = await Promise.race([sessionPromise, timeoutPromise])
      const data = result?.data ?? result
      if (currentRequestId === requestId) {
        user.value = (data?.user as unknown as User) ?? null
      }
    } catch {
      if (currentRequestId === requestId) {
        user.value = null
      }
    } finally {
      if (currentRequestId === requestId) {
        loading.value = false
        fetchPromise = null
      }
    }
  })()

  return fetchPromise
}

export function useAuth() {
  if (!initialized) {
    initialized = true
    fetchSession()
  }

  const signOut = async () => {
    try {
      await api.post('/auth/sign-out')
    } catch {
      // ignore backend errors, still sign out locally
    }
    try {
      await authClient.signOut({
        fetchOptions: {
          credentials: 'include',
          headers: authHeaders(),
        },
      } as any)
    } catch {
      // ignore
    }
    setStoredToken(null)
    user.value = null
    window.location.href = '/login'
  }

  return { user, loading, fetchSession, signOut }
}
