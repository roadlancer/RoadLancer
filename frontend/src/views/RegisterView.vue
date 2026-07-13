<script lang="ts" setup>
import { ref, reactive } from 'vue'
import { z } from 'zod'
import { signUp, setStoredToken } from '@/lib/auth-client'
import { fetchSession } from '@/composables/useAuth'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Separator } from '@/components/ui/separator'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { LoaderCircle, Mail, Lock, Phone, User as UserIcon, AlertCircle, Truck, Package, CheckCircle, Eye, EyeOff } from '@lucide/vue'

const submitError = ref('')
const submitting = ref(false)
const isSuccess = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const form = reactive({
  name: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
  role: 'driver' as 'driver' | 'shipper',
})

const errors = reactive({
  name: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
})

const registerSchema = z.object({
  name: z.string().min(1, 'Full name is required').min(2, 'Name must be at least 2 characters'),
  email: z.string().min(1, 'Email is required').email('Invalid email address'),
  phone: z.string().min(1, 'Phone number is required').regex(/^\+?[\d\s-]{10,}$/, 'Invalid phone number (at least 10 digits)'),
  password: z.string().min(1, 'Password is required').min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string().min(1, 'Please confirm your password'),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
})

function validate(field?: string) {
  let valid = true
  const fields = field ? [field] : ['name', 'email', 'phone', 'password', 'confirmPassword']
  
  if (field && field !== 'confirmPassword') {
    const result = (registerSchema.shape as Record<string, any>)[field].safeParse(form[field as keyof typeof form])
    errors[field as keyof typeof errors] = result.success ? '' : (result.error.issues[0]?.message ?? '')
    return result.success
  }

  const fullResult = registerSchema.safeParse(form)
  if (!fullResult.success) {
    valid = false
    for (const f of fields) {
      const issue = fullResult.error.issues.find((i) => i.path[0] === f)
      errors[f as keyof typeof errors] = issue ? issue.message : ''
    }
  } else {
    for (const f of fields) {
      errors[f as keyof typeof errors] = ''
    }
  }
  return valid
}

function handleInput(field: string) {
  submitError.value = ''
  if (errors[field as keyof typeof errors]) validate(field)
  if (field === 'password' && errors.confirmPassword) validate('confirmPassword')
}

function handleBlur(field: string) {
  validate(field)
}

async function handleSubmit() {
  submitError.value = ''
  if (!validate()) return

  submitting.value = true
  try {
    const { data: signUpData, error: signUpError } = await signUp.email({
      email: form.email,
      password: form.password,
      name: form.name,
      role: form.role,
      phone: form.phone,
    } as any)

    if (signUpError) {
      submitError.value = signUpError.message || 'Registration failed. Please try again or use a different email/phone.'
      return
    }

    // Store the session token from signUp response (better-auth bearer plugin)
    const signUpToken = signUpData?.session?.token
    if (signUpToken) {
      setStoredToken(signUpToken)
    }

    await fetchSession(true)
    isSuccess.value = true
  } catch (err: any) {
    submitError.value = err?.message || 'Something went wrong during registration. Please try again.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="flex-1 flex items-center justify-center p-6 sm:p-10 bg-background">
    <div class="w-full max-w-lg">
      <!-- Mobile logo -->
      <div class="lg:hidden flex items-center gap-2 mb-8 justify-center">
        <div class="w-10 h-10 bg-primary rounded-xl flex items-center justify-center shadow-md shadow-primary/20">
          <Truck class="w-5 h-5 text-primary-foreground" />
        </div>
        <span class="text-2xl font-bold tracking-tight text-foreground">RoadLancer</span>
      </div>

      <!-- Success Card -->
      <Card v-if="isSuccess" class="border shadow-lg animate-in fade-in zoom-in-95 duration-300">
        <CardHeader class="text-center pb-2">
          <div class="size-16 bg-green-500/10 text-green-600 rounded-full flex items-center justify-center mx-auto mb-4 border border-green-500/20">
            <CheckCircle class="size-8" />
          </div>
          <CardTitle class="text-2xl font-bold text-foreground">Registration Successful!</CardTitle>
          <CardDescription class="text-base mt-1">
            Welcome to RoadLancer, <span class="font-semibold text-foreground">{{ form.name }}</span>!
          </CardDescription>
        </CardHeader>
        <CardContent class="space-y-4 pt-4">
          <div class="p-4 rounded-xl bg-muted/60 border space-y-2 text-sm text-muted-foreground">
            <div class="flex items-center gap-2 font-semibold text-foreground">
              <span class="size-2 rounded-full bg-yellow-500 animate-pulse"></span>
              Account Status: Verification Pending
            </div>
            <p>
              You are now logged into RoadLancer! To ensure platform security across India's logistics network, all <strong class="capitalize text-foreground">{{ form.role }}</strong> accounts must complete verification and be reviewed by an administrator.
            </p>
            <p class="pt-1">
              You can explore the dashboard immediately. However, placing bids and posting shipments will remain restricted until your verification is submitted and approved.
            </p>
          </div>
        </CardContent>
        <CardFooter class="flex flex-col gap-3 pt-2">
          <a
            href="/get-validated"
            class="inline-flex items-center justify-center gap-2 rounded-lg px-4 text-sm font-semibold h-10 bg-primary text-primary-foreground hover:bg-primary/90 w-full shadow-md transition-all select-none no-underline"
          >
            Submit Verification Documents Now
          </a>
          <a
            :href="form.role === 'driver' ? '/driver' : '/shipper'"
            class="inline-flex items-center justify-center gap-2 rounded-lg border border-border bg-background hover:bg-muted text-foreground px-4 text-sm font-semibold h-10 w-full transition-all select-none no-underline"
          >
            Go to Dashboard
          </a>
        </CardFooter>
      </Card>

      <!-- Registration Form Card -->
      <Card v-else class="border shadow-lg">
        <CardHeader class="text-center pb-6">
          <CardTitle class="text-2xl font-bold tracking-tight">Create an Account</CardTitle>
          <CardDescription class="text-sm">
            Join India's fair pricing transport and logistics network
          </CardDescription>
        </CardHeader>

        <CardContent>
          <!-- Error Alert -->
          <Alert v-if="submitError" variant="destructive" class="mb-6 animate-in fade-in duration-200">
            <AlertCircle class="h-4 w-4" />
            <AlertDescription>{{ submitError }}</AlertDescription>
          </Alert>

          <form @submit.prevent="handleSubmit" class="space-y-5" novalidate>
            <!-- Account Type / Role Selection -->
            <div class="space-y-2">
              <Label class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Select Account Type *</Label>
              <RadioGroup v-model="form.role" class="grid grid-cols-2 gap-3">
                <!-- Driver Option -->
                <label
                  for="role-driver"
                  class="flex flex-col items-start gap-2 rounded-xl border-2 p-3.5 cursor-pointer transition-all hover:border-primary/50 relative"
                  :class="form.role === 'driver' ? 'border-primary bg-primary/5 shadow-sm shadow-primary/5' : 'border-border/80 bg-card'"
                >
                  <div class="flex items-center justify-between w-full">
                    <div class="size-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                      <Truck class="size-4" />
                    </div>
                    <RadioGroupItem value="driver" id="role-driver" class="sr-only" />
                    <div class="size-4 rounded-full border flex items-center justify-center transition-colors" :class="form.role === 'driver' ? 'border-primary bg-primary' : 'border-muted-foreground/30'">
                      <div v-if="form.role === 'driver'" class="size-1.5 rounded-full bg-white"></div>
                    </div>
                  </div>
                  <div>
                    <span class="text-sm font-bold text-foreground block">Driver / Transporter</span>
                    <span class="text-xs text-muted-foreground line-clamp-2 mt-0.5">Find shipments, submit bids, and earn without brokers.</span>
                  </div>
                </label>

                <!-- Shipper Option -->
                <label
                  for="role-shipper"
                  class="flex flex-col items-start gap-2 rounded-xl border-2 p-3.5 cursor-pointer transition-all hover:border-primary/50 relative"
                  :class="form.role === 'shipper' ? 'border-primary bg-primary/5 shadow-sm shadow-primary/5' : 'border-border/80 bg-card'"
                >
                  <div class="flex items-center justify-between w-full">
                    <div class="size-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                      <Package class="size-4" />
                    </div>
                    <RadioGroupItem value="shipper" id="role-shipper" class="sr-only" />
                    <div class="size-4 rounded-full border flex items-center justify-center transition-colors" :class="form.role === 'shipper' ? 'border-primary bg-primary' : 'border-muted-foreground/30'">
                      <div v-if="form.role === 'shipper'" class="size-1.5 rounded-full bg-white"></div>
                    </div>
                  </div>
                  <div>
                    <span class="text-sm font-bold text-foreground block">Shipper / Business</span>
                    <span class="text-xs text-muted-foreground line-clamp-2 mt-0.5">Post cargo loads, get AI price quotes, and hire verified drivers.</span>
                  </div>
                </label>
              </RadioGroup>
            </div>

            <!-- Full Name -->
            <div class="space-y-1.5">
              <Label for="name" class="text-sm font-medium">Full Name *</Label>
              <div class="relative">
                <UserIcon class="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                <Input
                  id="name"
                  v-model="form.name"
                  type="text"
                  required
                  placeholder="John Doe / Company Name"
                  class="pl-9"
                  :class="errors.name ? 'border-destructive focus-visible:ring-destructive/20' : ''"
                  @input="handleInput('name')"
                  @blur="handleBlur('name')"
                />
              </div>
              <p v-if="errors.name" class="text-xs text-destructive">{{ errors.name }}</p>
            </div>

            <!-- Email & Phone Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div class="space-y-1.5">
                <Label for="email" class="text-sm font-medium">Email Address *</Label>
                <div class="relative">
                  <Mail class="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                  <Input
                    id="email"
                    v-model="form.email"
                    type="email"
                    required
                    placeholder="you@example.com"
                    autocomplete="email"
                    class="pl-9"
                    :class="errors.email ? 'border-destructive focus-visible:ring-destructive/20' : ''"
                    @input="handleInput('email')"
                    @blur="handleBlur('email')"
                  />
                </div>
                <p v-if="errors.email" class="text-xs text-destructive">{{ errors.email }}</p>
              </div>

              <div class="space-y-1.5">
                <Label for="phone" class="text-sm font-medium">Phone Number *</Label>
                <div class="relative">
                  <Phone class="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                  <Input
                    id="phone"
                    v-model="form.phone"
                    type="tel"
                    required
                    placeholder="+91 98765 43210"
                    autocomplete="tel"
                    class="pl-9"
                    :class="errors.phone ? 'border-destructive focus-visible:ring-destructive/20' : ''"
                    @input="handleInput('phone')"
                    @blur="handleBlur('phone')"
                  />
                </div>
                <p v-if="errors.phone" class="text-xs text-destructive">{{ errors.phone }}</p>
              </div>
            </div>

            <!-- Password & Confirm Password Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div class="space-y-1.5">
                <Label for="password" class="text-sm font-medium">Password *</Label>
                <div class="relative">
                  <Lock class="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground pointer-events-none" />
                  <Input
                    id="password"
                    v-model="form.password"
                    :type="showPassword ? 'text' : 'password'"
                    required
                    placeholder="Min. 8 characters"
                    autocomplete="new-password"
                    class="pl-9 pr-9"
                    :class="errors.password ? 'border-destructive focus-visible:ring-destructive/20' : ''"
                    @input="handleInput('password')"
                    @blur="handleBlur('password')"
                  />
                  <button
                    type="button"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground focus:outline-none p-1"
                    @click="showPassword = !showPassword"
                    :aria-label="showPassword ? 'Hide password' : 'Show password'"
                  >
                    <EyeOff v-if="showPassword" class="size-4" />
                    <Eye v-else class="size-4" />
                  </button>
                </div>
                <p v-if="errors.password" class="text-xs text-destructive">{{ errors.password }}</p>
              </div>

              <div class="space-y-1.5">
                <Label for="confirm-password" class="text-sm font-medium">Confirm Password *</Label>
                <div class="relative">
                  <Lock class="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground pointer-events-none" />
                  <Input
                    id="confirm-password"
                    v-model="form.confirmPassword"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    required
                    placeholder="Repeat password"
                    autocomplete="new-password"
                    class="pl-9 pr-9"
                    :class="errors.confirmPassword ? 'border-destructive focus-visible:ring-destructive/20' : ''"
                    @input="handleInput('confirmPassword')"
                    @blur="handleBlur('confirmPassword')"
                  />
                  <button
                    type="button"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground focus:outline-none p-1"
                    @click="showConfirmPassword = !showConfirmPassword"
                    :aria-label="showConfirmPassword ? 'Hide password' : 'Show password'"
                  >
                    <EyeOff v-if="showConfirmPassword" class="size-4" />
                    <Eye v-else class="size-4" />
                  </button>
                </div>
                <p v-if="errors.confirmPassword" class="text-xs text-destructive">{{ errors.confirmPassword }}</p>
              </div>
            </div>

            <!-- Submit Button -->
            <Button type="submit" :disabled="submitting" class="w-full font-semibold shadow-md mt-2" size="lg">
              <LoaderCircle v-if="submitting" class="size-4 animate-spin mr-2" />
              {{ submitting ? 'Creating Account...' : 'Create Account' }}
            </Button>
          </form>

          <!-- Divider -->
          <div class="relative my-6">
            <Separator />
            <div class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-card px-3 text-xs text-muted-foreground uppercase font-medium">
              Or
            </div>
          </div>

          <!-- Social Login -->
          <div class="grid grid-cols-2 gap-3">
            <Button variant="outline" class="w-full text-xs font-medium">
              <svg class="w-4 h-4 mr-2" viewBox="0 0 24 24">
                <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
              </svg>
              Google
            </Button>
            <Button variant="outline" class="w-full text-xs font-medium">
              <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 1.183-4.961 3.014-2.117 3.675-.546 9.103 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 1.52-.065 2.09-.987 3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 1.636-3.325 1.662-3.415-.039-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 2.597-4.559-1.429-2.09-3.623-2.324-4.39-2.376-2-.156-3.675 1.09-4.61 1.09zM15.53 3.83c.843-1.012 1.4-2.427 1.245-3.83-1.207.052-2.662.805-3.532 1.818-.78.896-1.454 2.338-1.273 3.714 1.338.104 2.715-.688 3.559-1.701" />
              </svg>
              Apple
            </Button>
          </div>
        </CardContent>

        <CardFooter class="justify-center border-t py-4 bg-muted/20">
          <p class="text-sm text-muted-foreground">
            Already have an account?
            <RouterLink to="/login" class="text-primary hover:text-primary/80 font-semibold ml-1">Sign in</RouterLink>
          </p>
        </CardFooter>
      </Card>
    </div>
  </div>
</template>
