<script lang="ts" setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useAdminUsers } from '@/composables/useAdminUsers'
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
import { LoaderCircle, Users, UserCheck, UserX, Search, AlertCircle, Shield, Clock, ShieldCheck, XCircle } from '@lucide/vue'

const router = useRouter()
const { user, loading } = useAuth()

const {
  data: users,
  isLoading: loadingUsers,
  error,
  searchQuery,
  activeTab,
  pendingCount,
  rejectedCount,
  suspendMutation,
  refetchAll,
} = useAdminUsers()

const suspendDialogOpen = ref(false)
const suspendTarget = ref<any>(null)
const suspendReason = ref('')

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
  let result = users.value ?? []
  if (activeTab.value !== 'all') {
    result = result.filter((u: any) => u.role === activeTab.value)
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter((u: any) =>
      u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)
    )
  }
  return result
})

const stats = computed(() => ({
  total: users.value?.length ?? 0,
  drivers: users.value?.filter((u: any) => u.role === 'driver').length ?? 0,
  shippers: users.value?.filter((u: any) => u.role === 'shipper').length ?? 0,
  admins: users.value?.filter((u: any) => u.role === 'admin').length ?? 0,
  suspended: users.value?.filter((u: any) => u.suspended).length ?? 0,
}))

function openSuspendDialog(u: any) {
  suspendTarget.value = u
  suspendReason.value = ''
  suspendDialogOpen.value = true
}

function confirmSuspend() {
  if (!suspendTarget.value || !suspendReason.value) return
  suspendMutation.mutate(
    { userId: suspendTarget.value.id, suspended: true },
    { onSuccess: () => { suspendDialogOpen.value = false } },
  )
}

function unsuspendUser(userId: string) {
  suspendMutation.mutate({ userId, suspended: false })
}

watch([user, loading], ([u, l]) => {
  if (!l && (!u || u.role !== 'admin')) router.replace('/login')
})
</script>

<template>
  <div class="flex-1 p-8">
    <div v-if="loading" class="text-center py-20">
      <LoaderCircle class="size-8 text-primary animate-spin mx-auto mb-4" />
      <p class="text-muted-foreground">Loading...</p>
    </div>

    <div v-else-if="user && user.role === 'admin'" class="max-w-6xl mx-auto">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-foreground mb-2">Admin Dashboard</h1>
        <p class="text-muted-foreground">Manage drivers, shippers, and platform users</p>
      </div>

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
                  <p class="text-2xl font-bold">{{ pendingCount.data.value ?? 0 }}</p>
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
                  <p class="text-2xl font-bold">{{ rejectedCount.data.value ?? 0 }}</p>
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

      <Alert v-if="error" variant="destructive" class="mb-6">
        <AlertCircle class="h-4 w-4" />
        <AlertDescription>{{ error.message }}</AlertDescription>
      </Alert>

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
                />
              </div>
              <Button variant="outline" size="sm" @click="refetchAll" :disabled="loadingUsers">
                <LoaderCircle v-if="loadingUsers" class="size-4 animate-spin" />
                Refresh
              </Button>
            </div>
          </div>
          <Tabs v-model="activeTab" class="w-full">
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
                      :disabled="suspendMutation.isPending.value"
                      @click="unsuspendUser(u.id)"
                    >
                      <LoaderCircle v-if="suspendMutation.isPending.value" class="size-3 animate-spin mr-1" />
                      Unsuspend
                    </Button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

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
              :disabled="!suspendReason || suspendMutation.isPending.value"
              @click="confirmSuspend"
            >
              <LoaderCircle v-if="suspendMutation.isPending.value" class="size-4 animate-spin mr-1" />
              {{ suspendMutation.isPending.value ? 'Suspending...' : 'Confirm Suspension' }}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  </div>
</template>
