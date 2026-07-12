import { createAuthClient } from 'better-auth/vue'
import { customSessionClient } from 'better-auth/client/plugins'

export const authClient = createAuthClient({
  baseURL: import.meta.env.VITE_AUTH_URL || '',
  plugins: [customSessionClient()],
})

export const { signIn, signUp, signOut, useSession } = authClient
