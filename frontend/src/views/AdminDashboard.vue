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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Dialog, DialogContent, DialogDescription, DialogFooter,
  DialogHeader, DialogTitle, DialogTrigger,
} from '@/components/ui/dialog'
import {   LoaderCircle, Users, UserCheck, UserX, Search, AlertCircle, Shield, Clock, ShieldCheck, XCircle } from '@lucide/vue'

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
const activeTab = ref('all')
const actionLoading = ref<string | null>(null)
const error = ref('')
const pendingVerifications = ref(0)
const rejectedVerifications = ref(0)

// Suspend dialog state
const suspendDialogOpen = ref(false)
const suspendTarget = ref<UserRecord | null>(null)
const suspendReason = ref('')
const suspendLoading = ref(false)

const driverReasons = [
  'Repeated late deliveries',
  'Poor driving behavior reported',
  'Vehicle safety violations',
  'Refusal to accept assigned shipments',
  'Fraudulent activity or document tampering',
  'Abandoning a shipment mid-route',
  'Damage to goods in transit',
  'Unprofessional conduct with shippers',
  'Violation of terms of service',
  'Other',
]

const shipperReasons = [
  'Fraudulent shipment listings',
  'Non-payment for completed deliveries',
  'Repeated cancellation of active shipments',
  'Listing prohibited or illegal goods',
  'Providing false pickup/dropoff addresses',
  'Harassment or abuse of drivers',
  'Violation of terms of service',
  'Other',
]

const suspendReasons = computed(() => {
  if (suspendTarget.value?.role === 'driver') return driverReasons
  if (suspendTarget.value?.role === 'shipper') return shipperReasons
  return []
})

const filteredUsers = computed(() => {
  let result = users.value
  if (activeTab.value !== 'all') {
    result = result.filter(u => u.role === activeTab.value)
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(u =>
      u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)
    )
  }
  return result
})

const stats = computed(() => ({
  total: users.value.length,
  drivers: users.value.filter(u => u.role === 'driver').length,
  shippers: users.value.filter(u => u.role === 'shipper').length,
  admins: users.value.filter(u => u.role === 'admin').length,
  suspended: users.value.filter(u => u.suspended).length,
}))

async function getSessionToken(): Promise<string | null> {
  try {
    const { data: sessionData } = await authClient.getSession()
    return (sessionData as any)?.session?.token ?? null
  } catch {
    return null
  }
}

async function fetchUsers() {
  loadingUsers.value = true
  error.value = ''
  try {
    const token = await getSessionToken()
    if (!token) {
      router.push('/login')
      return
    }
    const params = new URLSearchParams()
    if (activeTab.value !== 'all') params.set('role', activeTab.value)
    if (searchQuery.value) params.set('search', searchQuery.value)

    const res = await fetch(`/api/admin/users?${params}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) {
      const data = await res.json()
      throw new Error(data.detail || 'Failed to fetch users')
    }
    users.value = await res.json()

    const vRes = await fetch('/api/verification/admin/count', {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (vRes.ok) {
      const vData = await vRes.json()
      pendingVerifications.value = vData.count
    }

    const rRes = await fetch('/api/verification/admin/count?status=rejected', {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (rRes.ok) {
      const rData = await rRes.json()
      rejectedVerifications.value = rData.count
    }
  } catch (e: any) {
    error.value = e.message || 'Failed to load users'
  } finally {
    loadingUsers.value = false
  }
}

function openSuspendDialog(u: UserRecord) {
  suspendTarget.value = u
  suspendReason.value = ''
  suspendDialogOpen.value = true
}

async function confirmSuspend() {
  if (!suspendTarget.value || !suspendReason.value) return
  suspendLoading.value = true
  error.value = ''
  try {
    const token = await getSessionToken()
    if (!token) {
      router.push('/login')
      return
    }
    const res = await fetch(`/api/admin/users/${suspendTarget.value.id}/suspend`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ suspended: true }),
    })
    if (!res.ok) {
      const data = await res.json()
      throw new Error(data.detail || 'Failed to suspend user')
    }
    const updated = await res.json()
    const idx = users.value.findIndex(u => u.id === suspendTarget.value!.id)
    if (idx !== -1) users.value[idx] = updated
    suspendDialogOpen.value = false
  } catch (e: any) {
    error.value = e.message || 'Failed to suspend user'
  } finally {
    suspendLoading.value = false
  }
}

async function unsuspendUser(userId: string) {
  actionLoading.value = userId
  error.value = ''
  try {
    const token = await getSessionToken()
    if (!token) {
      router.push('/login')
      return
    }
    const res = await fetch(`/api/admin/users/${userId}/suspend`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ suspended: false }),
    })
    if (!res.ok) {
      const data = await res.json()
      throw new Error(data.detail || 'Failed to unsuspend user')
    }
    const updated = await res.json()
    const idx = users.value.findIndex(u => u.id === userId)
    if (idx !== -1) users.value[idx] = updated
  } catch (e: any) {
    error.value = e.message || 'Failed to unsuspend user'
  } finally {
    actionLoading.value = null
  }
}

onMounted(() => {
  if (!loading.value && (!user.value || user.value.role !== 'admin')) {
    router.replace('/login')
  } else {
    fetchUsers()
  }
})
</script>

<template>
  <div class="flex-1 p-8">
    <div v-if="loading" class="text-center py-20">
      <LoaderCircle class="size-8 text-primary animate-spin mx-auto mb-4" />
      <p class="text-muted-foreground">Loading...</p>
    </div>

    <div v-else-if="user && user.role === 'admin'" class="max-w-6xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-foreground mb-2">Admin Dashboard</h1>
        <p class="text-muted-foreground">Manage drivers, shippers, and platform users</p>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-7 gap-3 mb-8">
        <Card>
          <CardContent class="pt-6">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                <Users class="size-5 text-primary" />
              </div>
              <div>
                <p class="text-2xl font-bold">{{ stats.total }}</p>
                <p class="text-xs text-muted-foreground">Total Users</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent class="pt-6">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center">
                <UserCheck class="size-5 text-blue-600" />
              </div>
              <div>
                <p class="text-2xl font-bold">{{ stats.drivers }}</p>
                <p class="text-xs text-muted-foreground">Drivers</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent class="pt-6">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-green-500/10 rounded-lg flex items-center justify-center">
                <UserCheck class="size-5 text-green-600" />
              </div>
              <div>
                <p class="text-2xl font-bold">{{ stats.shippers }}</p>
                <p class="text-xs text-muted-foreground">Shippers</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent class="pt-6">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-amber-500/10 rounded-lg flex items-center justify-center">
                <Shield class="size-5 text-amber-600" />
              </div>
              <div>
                <p class="text-2xl font-bold">{{ stats.admins }}</p>
                <p class="text-xs text-muted-foreground">Admins</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <router-link to="/admin/verifications" class="block">
          <Card class="hover:border-primary/50 transition-colors cursor-pointer">
            <CardContent class="pt-6">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-orange-500/10 rounded-lg flex items-center justify-center">
                  <Clock class="size-5 text-orange-600" />
                </div>
                <div>
                  <p class="text-2xl font-bold">{{ pendingVerifications }}</p>
                  <p class="text-xs text-muted-foreground">Pending</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </router-link>
        <router-link to="/admin/verifications" class="block">
          <Card class="hover:border-destructive/50 transition-colors cursor-pointer">
            <CardContent class="pt-6">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-red-500/10 rounded-lg flex items-center justify-center">
                  <XCircle class="size-5 text-red-600" />
                </div>
                <div>
                  <p class="text-2xl font-bold">{{ rejectedVerifications }}</p>
                  <p class="text-xs text-muted-foreground">Rejected</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </router-link>
        <Card>
          <CardContent class="pt-6">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-red-500/10 rounded-lg flex items-center justify-center">
                <UserX class="size-5 text-red-600" />
              </div>
              <div>
                <p class="text-2xl font-bold">{{ stats.suspended }}</p>
                <p class="text-xs text-muted-foreground">Suspended</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Error -->
      <Alert v-if="error" variant="destructive" class="mb-6">
        <AlertCircle class="h-4 w-4" />
        <AlertDescription>{{ error }}</AlertDescription>
      </Alert>

      <!-- User Table -->
      <Card>
        <CardHeader>
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <CardTitle>Users</CardTitle>
            <div class="flex items-center gap-3">
              <div class="relative">
                <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                <Input
                  v-model="searchQuery"
                  placeholder="Search users..."
                  class="pl-9 w-64"
                  @input="fetchUsers"
                />
              </div>
              <Button variant="outline" size="sm" @click="fetchUsers" :disabled="loadingUsers">
                <LoaderCircle v-if="loadingUsers" class="size-4 animate-spin" />
                Refresh
              </Button>
            </div>
          </div>
          <Tabs v-model="activeTab" class="w-full" @update:model-value="fetchUsers">
            <TabsList class="grid w-full grid-cols-4">
              <TabsTrigger value="all">All</TabsTrigger>
              <TabsTrigger value="driver">Drivers</TabsTrigger>
              <TabsTrigger value="shipper">Shippers</TabsTrigger>
              <TabsTrigger value="admin">Admins</TabsTrigger>
            </TabsList>
          </Tabs>
        </CardHeader>
        <CardContent>
          <div v-if="loadingUsers" class="text-center py-12">
            <LoaderCircle class="size-6 text-primary animate-spin mx-auto mb-3" />
            <p class="text-sm text-muted-foreground">Loading users...</p>
          </div>

          <div v-else-if="filteredUsers.length === 0" class="text-center py-12">
            <Users class="size-12 text-muted-foreground/50 mx-auto mb-3" />
            <p class="text-muted-foreground">No users found</p>
          </div>

          <div v-else class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-border">
                  <th class="text-left py-3 px-2 font-medium text-muted-foreground">User</th>
                  <th class="text-left py-3 px-2 font-medium text-muted-foreground">Role</th>
                  <th class="text-left py-3 px-2 font-medium text-muted-foreground">Phone</th>
                  <th class="text-left py-3 px-2 font-medium text-muted-foreground">Status</th>
                  <th class="text-right py-3 px-2 font-medium text-muted-foreground">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="u in filteredUsers"
                  :key="u.id"
                  class="border-b border-border last:border-0 hover:bg-muted/50"
                >
                  <td class="py-3 px-2">
                    <div>
                      <p class="font-medium">{{ u.name }}</p>
                      <p class="text-xs text-muted-foreground">{{ u.email }}</p>
                    </div>
                  </td>
                  <td class="py-3 px-2">
                    <Badge variant="secondary" class="capitalize">{{ u.role }}</Badge>
                  </td>
                  <td class="py-3 px-2 text-muted-foreground">
                    {{ u.phone || '—' }}
                  </td>
                  <td class="py-3 px-2">
                    <Badge :variant="u.suspended ? 'destructive' : 'default'">
                      {{ u.suspended ? 'Suspended' : 'Active' }}
                    </Badge>
                  </td>
                  <td class="py-3 px-2 text-right">
                    <Button
                      v-if="u.role !== 'admin' && !u.suspended"
                      variant="destructive"
                      size="sm"
                      @click="openSuspendDialog(u)"
                    >
                      Suspend
                    </Button>
                    <Button
                      v-else-if="u.role !== 'admin' && u.suspended"
                      variant="outline"
                      size="sm"
                      :disabled="actionLoading === u.id"
                      @click="unsuspendUser(u.id)"
                    >
                      <LoaderCircle v-if="actionLoading === u.id" class="size-3 animate-spin mr-1" />
                      Unsuspend
                    </Button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <!-- Suspend Dialog -->
      <Dialog v-model:open="suspendDialogOpen">
        <DialogContent class="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Suspend User</DialogTitle>
            <DialogDescription>
              Select a reason for suspending
              <span class="font-semibold text-foreground">{{ suspendTarget?.name }}</span>
              ({{ suspendTarget?.role }}).
              This will revoke their active sessions.
            </DialogDescription>
          </DialogHeader>

          <div class="space-y-2 max-h-64 overflow-y-auto py-2">
            <label
              v-for="reason in suspendReasons"
              :key="reason"
              class="flex items-center gap-3 rounded-lg border p-3 cursor-pointer transition-colors"
              :class="suspendReason === reason ? 'border-destructive bg-destructive/5' : 'border-border hover:border-destructive/50'"
            >
              <input
                type="radio"
                :value="reason"
                v-model="suspendReason"
                class="size-4 accent-destructive"
              />
              <span class="text-sm">{{ reason }}</span>
            </label>
          </div>

          <DialogFooter>
            <Button variant="outline" @click="suspendDialogOpen = false">Cancel</Button>
            <Button
              variant="destructive"
              :disabled="!suspendReason || suspendLoading"
              @click="confirmSuspend"
            >
              <LoaderCircle v-if="suspendLoading" class="size-4 animate-spin mr-1" />
              {{ suspendLoading ? 'Suspending...' : 'Confirm Suspension' }}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  </div>
</template>
