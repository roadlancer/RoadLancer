<script lang="ts" setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { z } from 'zod'
import { signIn } from '@/lib/auth-client'
import { useAuth } from '@/composables/useAuth'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { LoaderCircle, Mail, Lock } from '@lucide/vue'

const router = useRouter()
const { fetchSession } = useAuth()

const submitError = ref('')
const submitting = ref(false)

const form = reactive({ email: '', password: '' })
const errors = reactive({ email: '', password: '' })

const schema = z.object({
  email: z.string().min(1, 'Email is required').email('Invalid email address'),
  password: z.string().min(1, 'Password is required').min(6, 'Password must be at least 6 characters'),
})

function validate(field?: 'email' | 'password') {
  const fields = field ? [field] : ['email', 'password'] as const
  let valid = true
  for (const f of fields) {
    const result = schema.shape[f].safeParse(form[f])
    errors[f] = result.success ? '' : (result.error.issues[0]?.message ?? '')
    if (!result.success) valid = false
  }
  return valid
}

function handleInput(field: 'email' | 'password') {
  submitError.value = ''
  if (errors[field] && errors[field] !== ' ') validate(field)
}

function handleBlur(field: 'email' | 'password') {
  validate(field)
}

async function handleSubmit() {
  submitError.value = ''
  if (!validate()) return

  submitting.value = true
  try {
    const { error: signInError } = await signIn.email({
      email: form.email,
      password: form.password,
    })

    if (signInError) {
      submitError.value = signInError.message || 'Invalid email or password'
      errors.email = errors.email || ' '
      errors.password = errors.password || ' '
      return
    }

    await fetchSession()
    router.push('/')
  } catch {
    submitError.value = 'Something went wrong. Please try again.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="flex-1 flex">
    <!-- Left Side — Branding -->
    <div
      class="hidden lg:flex lg:w-[42%] relative bg-gradient-to-br from-blue-600 via-blue-700 to-teal-600 text-white p-12 flex-col justify-between overflow-hidden"
    >
      <div class="absolute inset-0 opacity-10">
        <div class="absolute top-20 left-10 w-72 h-72 bg-white rounded-full blur-3xl" />
        <div class="absolute bottom-20 right-10 w-96 h-96 bg-teal-300 rounded-full blur-3xl" />
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-blue-400 rounded-full blur-[120px]" />
      </div>

      <div class="absolute inset-0 opacity-[0.03]" style="background-image: url(&quot;data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E&quot;)" />

      <div class="relative z-10">
        <div class="flex items-center gap-3 mb-2">
          <div class="w-11 h-11 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm border border-white/10">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 18.75a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 0 1-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m3 0h1.125c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H18.75m-7.5-3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
            </svg>
          </div>
          <h1 class="text-2xl font-bold tracking-tight">RoadLancer</h1>
        </div>
      </div>

      <div class="relative z-10 space-y-8">
        <div>
          <div class="inline-flex items-center gap-2 px-3 py-1.5 bg-white/10 rounded-full text-sm font-medium backdrop-blur-sm border border-white/10 mb-6">
            <span class="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
            Trusted by 10,000+ drivers
          </div>
          <h2 class="text-4xl font-bold leading-tight mb-4">
            AI-Powered<br />Transportation<br />
            <span class="text-teal-300">Management</span>
          </h2>
          <p class="text-blue-100 text-lg max-w-md leading-relaxed">
            Connecting truck drivers with shippers through intelligent logistics and real-time bidding.
          </p>
        </div>

        <div class="space-y-4">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur-sm border border-white/10">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 21v-7.5a.75.75 0 0 1 .75-.75h3a.75.75 0 0 1 .75.75V21m-4.5 0H2.36m11.14 0H18m0 0h3.64m-1.39 0V9.349M3.75 21h3.64m-3.64 0h-3.64m0-1.5h3.64m11.14 0h-3.64m0 0V9.349m0 11.651v-3.64" />
              </svg>
            </div>
            <span class="text-blue-50">Connect drivers & shippers instantly</span>
          </div>
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur-sm border border-white/10">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 0 0-2.455 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" />
              </svg>
            </div>
            <span class="text-blue-50">AI-powered price estimation</span>
          </div>
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur-sm border border-white/10">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 3v11.25A2.25 2.25 0 0 0 6 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0 1 18 16.5h-2.25m-7.5 0h7.5m-7.5 0-1 3m8.5-3 1 3m0 0 .5 1.5m-.5-1.5h-9.5m0 0-.5 1.5m.75-9 3-3 2.148 2.148A12.061 12.061 0 0 1 16.5 7.605" />
              </svg>
            </div>
            <span class="text-blue-50">Real-time bidding system</span>
          </div>
        </div>

        <div class="grid grid-cols-3 gap-4 pt-4 border-t border-white/10">
          <div>
            <div class="text-2xl font-bold">5K+</div>
            <div class="text-blue-200 text-sm">Shipments</div>
          </div>
          <div>
            <div class="text-2xl font-bold">98%</div>
            <div class="text-blue-200 text-sm">On-time</div>
          </div>
          <div>
            <div class="text-2xl font-bold">4.9</div>
            <div class="text-blue-200 text-sm">Rating</div>
          </div>
        </div>
      </div>

      <div class="relative z-10 flex items-center justify-between text-blue-200 text-sm">
        <div>&copy; 2026 RoadLancer. All rights reserved.</div>
        <div class="flex gap-4">
          <a href="#" class="hover:text-white transition">Privacy</a>
          <a href="#" class="hover:text-white transition">Terms</a>
        </div>
      </div>
    </div>

    <!-- Right Side — Login Form -->
    <div class="w-full lg:w-[58%] flex items-center justify-center p-8 bg-background">
      <div class="w-full max-w-md">
        <div class="lg:hidden flex items-center gap-2 mb-8">
          <div class="w-9 h-9 bg-primary rounded-xl flex items-center justify-center">
            <svg class="w-5 h-5 text-primary-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 18.75a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 0 1-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m3 0h1.125c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H18.75m-7.5-3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
            </svg>
          </div>
          <span class="text-xl font-bold text-foreground">RoadLancer</span>
        </div>

        <Card>
          <CardHeader class="text-center">
            <CardTitle class="text-2xl">Welcome back</CardTitle>
            <CardDescription>Sign in to your account</CardDescription>
          </CardHeader>
          <CardContent>
            <div
              v-if="submitError"
              class="mb-4 p-3 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive text-sm flex items-center gap-2"
            >
              <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
              </svg>
              {{ submitError }}
            </div>

            <form @submit.prevent="handleSubmit" class="space-y-4" novalidate>
              <div class="space-y-2">
                <Label for="email">Email</Label>
                <div class="relative">
                  <Mail class="absolute left-2.5 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                  <Input
                    id="email"
                    v-model="form.email"
                    type="email"
                    required
                    placeholder="you@example.com"
                    autocomplete="new-password"
                    class="pl-9"
                    :class="errors.email ? 'border-destructive focus-visible:ring-destructive/20' : ''"
                    @input="handleInput('email')"
                    @blur="handleBlur('email')"
                  />
                </div>
                <p v-if="errors.email" class="text-sm text-destructive">{{ errors.email }}</p>
              </div>

              <div class="space-y-2">
                <Label for="password">Password</Label>
                <div class="relative">
                  <Lock class="absolute left-2.5 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                  <Input
                    id="password"
                    v-model="form.password"
                    type="password"
                    required
                    placeholder="Enter your password"
                    autocomplete="new-password"
                    class="pl-9"
                    :class="errors.password ? 'border-destructive focus-visible:ring-destructive/20' : ''"
                    @input="handleInput('password')"
                    @blur="handleBlur('password')"
                  />
                </div>
                <p v-if="errors.password" class="text-sm text-destructive">{{ errors.password }}</p>
              </div>

              <Button type="submit" :disabled="submitting" class="w-full" size="lg">
                <LoaderCircle v-if="submitting" class="size-4 animate-spin" />
                {{ submitting ? 'Signing in...' : 'Sign in' }}
              </Button>
            </form>

            <p class="mt-6 text-center text-sm text-muted-foreground">
              Don't have an account?
              <a href="#" class="text-primary hover:text-primary/80 font-medium">Sign up</a>
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>
