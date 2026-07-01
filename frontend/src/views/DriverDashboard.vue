<script lang="ts" setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { authClient } from '@/lib/auth-client'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { LoaderCircle, ShieldCheck, Truck, AlertCircle } from '@lucide/vue'

const router = useRouter()
const { user, loading } = useAuth()
const isVerified = ref<boolean | null>(null)
const loadingVerification = ref(true)

watch([user, loading], ([u, l]) => {
  if (!l) {
    if (!u) router.replace('/login')
    else if (u.role !== 'driver') router.replace('/')
  }
})

onMounted(async () => {
  if (!user.value) return
  try {
    const session = await authClient.getSession()
    const token = (session.data as any)?.session?.token
    if (!token) return

    const res = await fetch('/api/verification/status', {
      headers: { Authorization: `Bearer ${token}` },
    })
    const data = await res.json()
    isVerified.value = data.status === 'approved'
  } catch {
    isVerified.value = false
  } finally {
    loadingVerification.value = false
  }
})
</script>

<template>
  <div class="flex-1 flex items-center justify-center p-8">
    <div v-if="loading || loadingVerification" class="text-center">
      <LoaderCircle class="size-8 animate-spin mx-auto text-muted-foreground" />
      <p class="text-muted-foreground mt-2">Loading...</p>
    </div>
    <div v-else-if="user?.role === 'driver'" class="text-center max-w-lg">
      <h1 class="text-3xl font-bold text-foreground mb-2">Driver Dashboard</h1>
      <p class="text-muted-foreground mb-6">Welcome, {{ user.name }}. This is your driver portal.</p>

      <Alert v-if="isVerified === false" class="mb-6 text-left">
        <AlertCircle class="h-4 w-4" />
        <AlertDescription>
          <div class="flex items-center justify-between">
            <span>Your account is not verified yet. Complete verification to access all features.</span>
            <Button size="sm" class="ml-4 shrink-0" @click="router.push('/get-validated')">
              <ShieldCheck class="size-4 mr-1" />
              Get Validated
            </Button>
          </div>
        </AlertDescription>
      </Alert>

      <Alert v-else-if="isVerified === true" class="mb-6 border-green-200 bg-green-50 text-green-800 text-left">
        <ShieldCheck class="h-4 w-4 text-green-600" />
        <AlertDescription class="text-green-700">
          Your account is verified. You have full access to the platform.
        </AlertDescription>
      </Alert>

      <Card>
        <CardHeader>
          <CardTitle class="flex items-center gap-2">
            <Truck class="size-5" />
            Your Profile
          </CardTitle>
          <CardDescription>Manage your driver account</CardDescription>
        </CardHeader>
        <CardContent class="space-y-2 text-left">
          <p class="text-sm"><span class="font-medium text-muted-foreground">Name:</span> {{ user.name }}</p>
          <p class="text-sm"><span class="font-medium text-muted-foreground">Email:</span> {{ user.email }}</p>
          <p class="text-sm"><span class="font-medium text-muted-foreground">Phone:</span> {{ user.phone || 'Not set' }}</p>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
