<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { authClient } from '@/lib/auth-client'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Dialog, DialogContent, DialogDescription, DialogFooter,
  DialogHeader, DialogTitle,
} from '@/components/ui/dialog'
import { LoaderCircle, Clock, Search, AlertCircle, CheckCircle, XCircle, ArrowLeft } from '@lucide/vue'

const router = useRouter()
const { user, loading } = useAuth()

interface UserRecord {
  id: string
  name: string
  email: string
  role: string
  phone: string | null
  suspended: boolean
  status: string
  created_at: string | null
}

const users = ref<UserRecord[]>([])
const loadingUsers = ref(false)
const searchQuery = ref('')
const actionLoading = ref<string | null>(null)
const error = ref('')

// Reject dialog state
const rejectDialogOpen = ref(false)
const rejectTarget = ref<UserRecord | null>(null)
const rejectReason = ref('')
const rejectLoading = ref(false)

const rejectReasons = [
  'Incomplete or missing registration information',
  'Invalid identity verification documents',
  'Suspicious or fraudulent registration',
  'Does not meet platform eligibility requirements',
  'Duplicate account detected',
  'Violation of terms of service during registration',
  'Other',
]

const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value
  const q = searchQuery.value.toLowerCase()
  return users.value.filter(u =>
    u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)
  )
})

async function getSessionToken(): Promise<string | null> {
  try {
    const { data: sessionData } = await authClient.getSession()
    return (sessionData as any)?.session?.token ?? null
  } catch {
    return null
  }
}

async function fetchPendingUsers() {
  loadingUsers.value = true
  error.value = ''
  try {
    const token = await getSessionToken()
    if (!token) {
      router.push('/login')
      return
    }
    const params = new URLSearchParams()
    if (searchQuery.value) params.set('search', searchQuery.value)

    const res = await fetch(`/api/admin/users/pending/list?${params}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) {
      const data = await res.json()
      throw new Error(data.detail || 'Failed to fetch pending users')
    }
    users.value = await res.json()
  } catch (e: any) {
    error.value = e.message || 'Failed to load pending users'
  } finally {
    loadingUsers.value = false
  }
}

async function approveUser(userId: string) {
  actionLoading.value = userId
  error.value = ''
  try {
    const token = await getSessionToken()
    if (!token) {
      router.push('/login')
      return
    }
    const res = await fetch(`/api/admin/users/${userId}/approve`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) {
      const data = await res.json()
      throw new Error(data.detail || 'Failed to approve user')
    }
    users.value = users.value.filter(u => u.id !== userId)
  } catch (e: any) {
    error.value = e.message || 'Failed to approve user'
  } finally {
    actionLoading.value = null
  }
}

function openRejectDialog(u: UserRecord) {
  rejectTarget.value = u
  rejectReason.value = ''
  rejectDialogOpen.value = true
}

async function confirmReject() {
  if (!rejectTarget.value || !rejectReason.value) return
  rejectLoading.value = true
  error.value = ''
  try {
    const token = await getSessionToken()
    if (!token) {
      router.push('/login')
      return
    }
    const res = await fetch(`/api/admin/users/${rejectTarget.value.id}/reject`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ reason: rejectReason.value }),
    })
    if (!res.ok) {
      const data = await res.json()
      throw new Error(data.detail || 'Failed to reject user')
    }
    users.value = users.value.filter(u => u.id !== rejectTarget.value!.id)
    rejectDialogOpen.value = false
  } catch (e: any) {
    error.value = e.message || 'Failed to reject user'
  } finally {
    rejectLoading.value = false
  }
}

onMounted(() => {
  if (!loading.value && (!user.value || user.value.role !== 'admin')) {
    router.replace('/login')
  } else {
    fetchPendingUsers()
  }
})
</script>

<template>
  <div class="flex-1 p-8">
    <div v-if="loading" class="text-center py-20">
      <LoaderCircle class="size-8 text-primary animate-spin mx-auto mb-4" />
      <p class="text-muted-foreground">Loading...</p>
    </div>

    <div v-else-if="user && user.role === 'admin'" class="max-w-5xl mx-auto">
      <!-- Header -->
      <div class="flex items-center gap-4 mb-8">
        <Button variant="ghost" size="sm" @click="router.push('/admin')">
          <ArrowLeft class="size-4 mr-1" />
          Back
        </Button>
        <div>
          <h1 class="text-3xl font-bold text-foreground mb-1">Pending Approvals</h1>
          <p class="text-muted-foreground">Review and approve or reject new user registrations</p>
        </div>
      </div>

      <!-- Error -->
      <Alert v-if="error" variant="destructive" class="mb-6">
        <AlertCircle class="h-4 w-4" />
        <AlertDescription>{{ error }}</AlertDescription>
      </Alert>

      <!-- Pending Users Card -->
      <Card>
        <CardHeader>
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div class="flex items-center gap-3">
              <CardTitle>Pending Users</CardTitle>
              <Badge variant="secondary" class="text-xs">{{ users.length }}</Badge>
            </div>
            <div class="flex items-center gap-3">
              <div class="relative">
                <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                <Input
                  v-model="searchQuery"
                  placeholder="Search by name or email..."
                  class="pl-9 w-64"
                />
              </div>
              <Button variant="outline" size="sm" @click="fetchPendingUsers" :disabled="loadingUsers">
                <LoaderCircle v-if="loadingUsers" class="size-4 animate-spin" />
                Refresh
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div v-if="loadingUsers" class="text-center py-12">
            <LoaderCircle class="size-6 text-primary animate-spin mx-auto mb-3" />
            <p class="text-sm text-muted-foreground">Loading pending users...</p>
          </div>

          <div v-else-if="filteredUsers.length === 0" class="text-center py-12">
            <CheckCircle class="size-12 text-green-500/50 mx-auto mb-3" />
            <p class="text-muted-foreground font-medium">All caught up!</p>
            <p class="text-sm text-muted-foreground mt-1">No pending users to review</p>
          </div>

          <div v-else class="space-y-4">
            <div
              v-for="u in filteredUsers"
              :key="u.id"
              class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-lg border p-4 hover:bg-muted/50 transition-colors"
            >
              <div class="flex items-center gap-4">
                <div class="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                  <span class="text-sm font-bold text-primary">{{ u.name?.charAt(0)?.toUpperCase() }}</span>
                </div>
                <div>
                  <p class="font-medium">{{ u.name }}</p>
                  <p class="text-sm text-muted-foreground">{{ u.email }}</p>
                  <div class="flex items-center gap-2 mt-1">
                    <Badge variant="secondary" class="capitalize text-xs">{{ u.role }}</Badge>
                    <span v-if="u.phone" class="text-xs text-muted-foreground">{{ u.phone }}</span>
                    <span class="text-xs text-muted-foreground">
                      Registered {{ new Date(u.created_at!).toLocaleDateString() }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-2 sm:ml-4">
                <Button
                  variant="default"
                  size="sm"
                  :disabled="actionLoading === u.id"
                  @click="approveUser(u.id)"
                >
                  <LoaderCircle v-if="actionLoading === u.id" class="size-3 animate-spin mr-1" />
                  <CheckCircle v-else class="size-3 mr-1" />
                  Approve
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  :disabled="actionLoading === u.id"
                  @click="openRejectDialog(u)"
                >
                  <XCircle class="size-3 mr-1" />
                  Reject
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Reject Dialog -->
      <Dialog v-model:open="rejectDialogOpen">
        <DialogContent class="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Reject User</DialogTitle>
            <DialogDescription>
              Select a reason for rejecting
              <span class="font-semibold text-foreground">{{ rejectTarget?.name }}</span>
              ({{ rejectTarget?.email }}).
            </DialogDescription>
          </DialogHeader>

          <div class="space-y-2 max-h-64 overflow-y-auto py-2">
            <label
              v-for="reason in rejectReasons"
              :key="reason"
              class="flex items-center gap-3 rounded-lg border p-3 cursor-pointer transition-colors"
              :class="rejectReason === reason ? 'border-destructive bg-destructive/5' : 'border-border hover:border-destructive/50'"
            >
              <input
                type="radio"
                :value="reason"
                v-model="rejectReason"
                class="size-4 accent-destructive"
              />
              <span class="text-sm">{{ reason }}</span>
            </label>
          </div>

          <DialogFooter>
            <Button variant="outline" @click="rejectDialogOpen = false">Cancel</Button>
            <Button
              variant="destructive"
              :disabled="!rejectReason || rejectLoading"
              @click="confirmReject"
            >
              <LoaderCircle v-if="rejectLoading" class="size-4 animate-spin mr-1" />
              {{ rejectLoading ? 'Rejecting...' : 'Confirm Rejection' }}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  </div>
</template>
