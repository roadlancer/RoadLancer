<script lang="ts" setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { z } from 'zod'
import { signIn } from '@/lib/auth-client'
import { useAuth, user } from '@/composables/useAuth'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Separator } from '@/components/ui/separator'
import { LoaderCircle, Mail, Lock, AlertCircle, Shield, Eye, EyeOff } from '@lucide/vue'

const router = useRouter()
const { fetchSession } = useAuth()

const submitError = ref('')
const submitting = ref(false)
const showPassword = ref(false)

const form = reactive({ email: '', password: '' })
const errors = reactive({ email: '', password: '' })

const loginSchema = z.object({
  email: z.string().min(1, 'Email is required').email('Invalid email address'),
  password: z.string().min(1, 'Password is required').min(6, 'Password must be at least 6 characters'),
})

function validate(field?: string) {
  let valid = true
  const fields = field ? [field] : ['email', 'password']

  for (const f of fields) {
    const result = (loginSchema.shape as Record<string, any>)[f].safeParse(form[f as keyof typeof form])
    errors[f as keyof typeof errors] = result.success ? '' : (result.error.issues[0]?.message ?? '')
    if (!result.success) valid = false
  }
  return valid
}

function handleInput(field: string) {
  submitError.value = ''
  if (errors[field as keyof typeof errors]) validate(field)
}

function handleBlur(field: string) {
  validate(field)
}

async function handleSubmit() {
  submitError.value = ''
  if (!validate()) return

  submitting.value = true
  try {
    const { data: signInData, error: signInError } = await signIn.email({
      email: form.email,
      password: form.password,
    })

    if (signInError) {
      submitError.value = signInError.message || 'Invalid credentials'
      return
    }

    await fetchSession(true)

    if (!user.value && signInData?.user) {
      user.value = signInData.user as any
    }

    const actualRole = user.value?.role
    const userStatus = (user.value as any)?.status

    if (actualRole !== 'admin') {
      submitError.value = 'Access denied. This login is for admin/agent accounts only.'
      await signIn.email({ email: form.email, password: form.password }).catch(() => {})
      user.value = null
      return
    }

    if (userStatus === 'rejected') {
      submitError.value = 'Your account has been rejected. Please contact support.'
      user.value = null
      return
    }

    if (user.value?.suspended) {
      submitError.value = 'Your account has been deactivated. Please contact a supreme admin.'
      user.value = null
      return
    }

    router.push('/admin')
  } catch {
    submitError.value = 'Something went wrong. Please try again.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="flex-1 flex items-center justify-center p-8 bg-background">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="flex items-center gap-2 mb-8 justify-center">
        <div class="w-9 h-9 bg-primary rounded-xl flex items-center justify-center">
          <Shield class="w-5 h-5 text-primary-foreground" />
        </div>
        <span class="text-xl font-bold text-foreground">RoadLancer Admin</span>
      </div>

      <Card>
        <CardHeader class="text-center">
          <CardTitle class="text-2xl">Admin / Agent Login</CardTitle>
          <CardDescription>Sign in to your admin or agent account</CardDescription>
        </CardHeader>
        <CardContent>
          <!-- Error Alert -->
          <Alert v-if="submitError" variant="destructive" class="mb-4">
            <AlertCircle class="h-4 w-4" />
            <AlertDescription>{{ submitError }}</AlertDescription>
          </Alert>

          <form @submit.prevent="handleSubmit" class="space-y-4" novalidate>
            <div class="space-y-2">
              <Label for="email">Email</Label>
              <div class="relative">
                <Mail class="absolute left-2.5 top-1/2 -translate-y-1/2 size-4 text-muted-foreground pointer-events-none" />
                <Input
                  id="email"
                  v-model="form.email"
                  type="email"
                  required
                  placeholder="admin@roadlancer.com"
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
                <Lock class="absolute left-2.5 top-1/2 -translate-y-1/2 size-4 text-muted-foreground pointer-events-none" />
                <Input
                  id="password"
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  placeholder="Enter your password"
                  autocomplete="new-password"
                  class="pl-9 pr-9"
                  :class="errors.password ? 'border-destructive focus-visible:ring-destructive/20' : ''"
                  @input="handleInput('password')"
                  @blur="handleBlur('password')"
                />
                <button
                  type="button"
                  class="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground focus:outline-none p-1"
                  @click="showPassword = !showPassword"
                  :aria-label="showPassword ? 'Hide password' : 'Show password'"
                >
                  <EyeOff v-if="showPassword" class="size-4" />
                  <Eye v-else class="size-4" />
                </button>
              </div>
              <p v-if="errors.password" class="text-sm text-destructive">{{ errors.password }}</p>
            </div>

            <Button type="submit" :disabled="submitting" class="w-full" size="lg">
              <LoaderCircle v-if="submitting" class="size-4 animate-spin" />
              {{ submitting ? 'Signing in...' : 'Sign in as Admin / Agent' }}
            </Button>
          </form>

          <!-- Divider -->
          <div class="relative my-6">
            <Separator />
            <div class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-card px-2 text-sm text-muted-foreground">
              Not an admin?
            </div>
          </div>

          <Button variant="outline" class="w-full" @click="router.push('/login')">
            Back to User Login
          </Button>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
