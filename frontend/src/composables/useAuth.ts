import { ref } from 'vue'
import { authClient } from '@/lib/auth-client'

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
      const { data: sessionData } = await authClient.getSession()
      const token = (sessionData as any)?.session?.token
      if (token) {
        await fetch('/api/auth/sign-out', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
        })
      }
    } catch {
      // ignore backend errors, still sign out locally
    }
    await authClient.signOut()
    user.value = null
    window.location.href = '/login'
  }

  return { user, loading, fetchSession, signOut }
}
