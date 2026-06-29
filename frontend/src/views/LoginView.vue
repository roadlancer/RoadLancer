<script lang="ts" setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { z } from 'zod'
import { signIn } from '@/lib/auth-client'
import { useAuth } from '@/composables/useAuth'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Checkbox } from '@/components/ui/checkbox'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Separator } from '@/components/ui/separator'
import { LoaderCircle, Mail, Lock, Phone, AlertCircle, Truck } from '@lucide/vue'

const router = useRouter()
const { fetchSession } = useAuth()

const submitError = ref('')
const submitting = ref(false)
const activeTab = ref('email')

const form = reactive({ email: '', phone: '', password: '' })
const errors = reactive({ email: '', phone: '', password: '' })

const emailSchema = z.object({
  email: z.string().min(1, 'Email is required').email('Invalid email address'),
  password: z.string().min(1, 'Password is required').min(6, 'Password must be at least 6 characters'),
})

const phoneSchema = z.object({
  phone: z.string().min(1, 'Phone number is required').regex(/^\+?[\d\s-]{10,}$/, 'Invalid phone number'),
  password: z.string().min(1, 'Password is required').min(6, 'Password must be at least 6 characters'),
})

function validate(field?: string) {
  let valid = true
  const fields = field ? [field] : activeTab.value === 'email' ? ['email', 'password'] : ['phone', 'password']
  const schema = activeTab.value === 'email' ? emailSchema : phoneSchema
  
  for (const f of fields) {
    const result = (schema.shape as Record<string, any>)[f].safeParse(form[f as keyof typeof form])
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
    const email = activeTab.value === 'email' ? form.email : form.phone
    const { error: signInError } = await signIn.email({
      email,
      password: form.password,
    })

    if (signInError) {
      submitError.value = signInError.message || 'Invalid credentials'
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
  <div class="flex-1 flex items-center justify-center p-8 bg-background">
      <div class="w-full max-w-md">
        <!-- Mobile logo -->
        <div class="lg:hidden flex items-center gap-2 mb-8">
          <div class="w-9 h-9 bg-primary rounded-xl flex items-center justify-center">
            <Truck class="w-5 h-5 text-primary-foreground" />
          </div>
          <span class="text-xl font-bold text-foreground">RoadLancer</span>
        </div>

        <Card>
          <CardHeader class="text-center">
            <CardTitle class="text-2xl">Welcome back</CardTitle>
            <CardDescription>Sign in to your account</CardDescription>
          </CardHeader>
          <CardContent>
            <!-- Error Alert -->
            <Alert v-if="submitError" variant="destructive" class="mb-4">
              <AlertCircle class="h-4 w-4" />
              <AlertDescription>{{ submitError }}</AlertDescription>
            </Alert>

            <!-- Login Tabs -->
            <Tabs v-model="activeTab" class="w-full">
              <TabsList class="grid w-full grid-cols-2 mb-4">
                <TabsTrigger value="email">
                  <Mail class="w-4 h-4 mr-2" />
                  Email
                </TabsTrigger>
                <TabsTrigger value="phone">
                  <Phone class="w-4 h-4 mr-2" />
                  Phone
                </TabsTrigger>
              </TabsList>

              <!-- Email Login -->
              <TabsContent value="email">
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
                    <div class="flex items-center justify-between">
                      <Label for="password">Password</Label>
                      <a href="#" class="text-sm text-primary hover:text-primary/80">Forgot password?</a>
                    </div>
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

                  <div class="flex items-center space-x-2">
                    <Checkbox id="remember" />
                    <Label for="remember" class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                      Remember me
                    </Label>
                  </div>

                  <Button type="submit" :disabled="submitting" class="w-full" size="lg">
                    <LoaderCircle v-if="submitting" class="size-4 animate-spin" />
                    {{ submitting ? 'Signing in...' : 'Sign in' }}
                  </Button>
                </form>
              </TabsContent>

              <!-- Phone Login -->
              <TabsContent value="phone">
                <form @submit.prevent="handleSubmit" class="space-y-4" novalidate>
                  <div class="space-y-2">
                    <Label for="phone">Phone Number</Label>
                    <div class="relative">
                      <Phone class="absolute left-2.5 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                      <Input
                        id="phone"
                        v-model="form.phone"
                        type="tel"
                        required
                        placeholder="+1 (555) 000-0000"
                        autocomplete="new-password"
                        class="pl-9"
                        :class="errors.phone ? 'border-destructive focus-visible:ring-destructive/20' : ''"
                        @input="handleInput('phone')"
                        @blur="handleBlur('phone')"
                      />
                    </div>
                    <p v-if="errors.phone" class="text-sm text-destructive">{{ errors.phone }}</p>
                  </div>

                  <div class="space-y-2">
                    <div class="flex items-center justify-between">
                      <Label for="password-phone">Password</Label>
                      <a href="#" class="text-sm text-primary hover:text-primary/80">Forgot password?</a>
                    </div>
                    <div class="relative">
                      <Lock class="absolute left-2.5 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                      <Input
                        id="password-phone"
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

                  <div class="flex items-center space-x-2">
                    <Checkbox id="remember-phone" />
                    <Label for="remember-phone" class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                      Remember me
                    </Label>
                  </div>

                  <Button type="submit" :disabled="submitting" class="w-full" size="lg">
                    <LoaderCircle v-if="submitting" class="size-4 animate-spin" />
                    {{ submitting ? 'Signing in...' : 'Sign in' }}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>

            <!-- Divider -->
            <div class="relative my-6">
              <Separator />
              <div class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-card px-2 text-sm text-muted-foreground">
                Or continue with
              </div>
            </div>

            <!-- Social Login -->
            <div class="grid grid-cols-2 gap-3">
              <Button variant="outline" class="w-full">
                <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                  <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                  <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                </svg>
                Google
              </Button>
              <Button variant="outline" class="w-full">
                <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 1.183-4.961 3.014-2.117 3.675-.546 9.103 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 1.52-.065 2.09-.987 3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 1.636-3.325 1.662-3.415-.039-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 2.597-4.559-1.429-2.09-3.623-2.324-4.39-2.376-2-.156-3.675 1.09-4.61 1.09zM15.53 3.83c.843-1.012 1.4-2.427 1.245-3.83-1.207.052-2.662.805-3.532 1.818-.78.896-1.454 2.338-1.273 3.714 1.338.104 2.715-.688 3.559-1.701" />
                </svg>
                Apple
              </Button>
            </div>
          </CardContent>
          <CardFooter class="justify-center">
            <p class="text-sm text-muted-foreground">
              Don't have an account?
              <a href="#" class="text-primary hover:text-primary/80 font-medium">Sign up</a>
            </p>
          </CardFooter>
        </Card>
      </div>
  </div>
</template>
