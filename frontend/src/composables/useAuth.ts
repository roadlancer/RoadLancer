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

export { user, loading }

export async function fetchSession() {
  loading.value = true
  try {
    const { data } = await authClient.getSession()
    user.value = (data?.user as unknown as User) ?? null
  } catch {
    user.value = null
  } finally {
    loading.value = false
  }
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
