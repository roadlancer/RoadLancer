<script lang="ts" setup>
import { watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useVerificationStatus } from '@/composables/useVerificationStatus'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'
import { LoaderCircle, ShieldCheck, FileText, AlertCircle } from '@lucide/vue'

const router = useRouter()
const { user, loading } = useAuth()
const { isVerified, isLoading: loadingVerification } = useVerificationStatus()

watch([user, loading], ([u, l]) => {
  if (!l) {
    if (!u) router.replace('/login')
    else if (u.role !== 'shipper') router.replace('/')
  }
})
</script>

<template>
  <div class="flex-1 flex items-center justify-center p-8">
    <div v-if="loading || loadingVerification" class="text-center max-w-lg">
      <Skeleton class="h-9 w-48 mx-auto mb-2" />
      <Skeleton class="h-5 w-64 mx-auto mb-6" />
      <Skeleton class="h-20 w-full mb-6" />
      <Card>
        <CardHeader>
          <Skeleton class="h-6 w-32 mb-2" />
          <Skeleton class="h-4 w-48" />
        </CardHeader>
        <CardContent class="space-y-3">
          <Skeleton class="h-4 w-full" />
          <Skeleton class="h-4 w-full" />
          <Skeleton class="h-4 w-2/3" />
        </CardContent>
      </Card>
    </div>
    <div v-else-if="user?.role === 'shipper'" class="text-center max-w-lg">
      <h1 class="text-3xl font-bold text-foreground mb-2">Shipper Dashboard</h1>
      <p class="text-muted-foreground mb-6">Welcome, {{ user.name }}. This is your shipper portal.</p>

      <Alert v-if="isVerified === false" class="mb-6 text-left">
        <AlertCircle class="h-4 w-4" />
        <AlertDescription>
          <div class="flex items-center justify-between">
            <span>Your account is not verified yet. Complete verification to access all features.</span>
            <Button size="sm" class="ml-4 shrink-0" @click="router.push('/get-validated-shipper')">
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
            <FileText class="size-5" />
            Your Profile
          </CardTitle>
          <CardDescription>Manage your shipper account</CardDescription>
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
