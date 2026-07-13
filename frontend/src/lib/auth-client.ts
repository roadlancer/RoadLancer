import { createAuthClient } from 'better-auth/vue'
import { customSessionClient } from 'better-auth/client/plugins'

const TOKEN_KEY = 'rl_session_token'

export function getStoredToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

export function setStoredToken(token: string | null) {
  try {
    if (token) {
      localStorage.setItem(TOKEN_KEY, token)
    } else {
      localStorage.removeItem(TOKEN_KEY)
    }
  } catch {
    // ignore
  }
}

export const authClient = createAuthClient({
  baseURL: import.meta.env.VITE_AUTH_URL || '',
  plugins: [customSessionClient()],
  fetchOptions: {
    credentials: 'include',
  },
})

export const { signIn, signUp, signOut, useSession } = authClient
