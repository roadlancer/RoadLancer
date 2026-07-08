import { ref } from 'vue'
import { authClient } from '@/lib/auth-client'
import api from '@/lib/api'

interface User {
  id: string
  name: string
  email: string
  role: string
  phone: string | null
}

const user = ref<User | null>(null)
const loading = ref(true)
let initialized = false
let fetchPromise: Promise<void> | null = null

export { user, loading }

export async function fetchSession(force = false) {
  if (fetchPromise && !force) {
    return fetchPromise
  }

  loading.value = true
  fetchPromise = (async () => {
    try {
      const timeoutPromise = new Promise<{ data: any }>((_, reject) =>
        setTimeout(() => reject(new Error('Auth request timed out')), 3000)
      )
      const sessionPromise = authClient.getSession()
      const { data } = await Promise.race([sessionPromise, timeoutPromise])
      user.value = (data?.user as unknown as User) ?? null
    } catch {
      user.value = null
    } finally {
      loading.value = false
      fetchPromise = null
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
    await authClient.signOut()
    user.value = null
    window.location.href = '/login'
  }

  return { user, loading, fetchSession, signOut }
}
