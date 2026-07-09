<script lang="ts" setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/lib/api'
import { useAuth } from '@/composables/useAuth'
import { useAdminUsers } from '@/composables/useAdminUsers'
import VerificationDetailDialog from '@/components/VerificationDetailDialog.vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Dialog, DialogContent, DialogDescription, DialogFooter,
  DialogHeader, DialogTitle,
} from '@/components/ui/dialog'
import { Skeleton } from '@/components/ui/skeleton'
import UsersTable from '@/components/UsersTable.vue'
import type { SortingState } from '@tanstack/vue-table'
import { LoaderCircle, Users, UserCheck, UserX, Search, AlertCircle, Shield, Clock, ShieldCheck, XCircle } from '@lucide/vue'

const router = useRouter()
const { user, loading } = useAuth()

const {
  data: users,
  isLoading: loadingUsers,
  error,
  searchQuery,
  activeTab,
  sortField,
  sortOrder,
  pendingCount,
  rejectedCount,
  verifiedCount,
  suspendMutation,
  refetchAll,
} = useAdminUsers()

const userSorting = ref<SortingState>([])

watch(userSorting, (newSorting) => {
  if (newSorting.length > 0) {
    sortField.value = newSorting[0].id
    sortOrder.value = newSorting[0].desc ? 'desc' : 'asc'
  } else {
    sortField.value = null
    sortOrder.value = 'desc'
  }
}, { deep: true })

const suspendDialogOpen = ref(false)
const suspendTarget = ref<any>(null)
const suspendReason = ref('')

const verificationDialogOpen = ref(false)
const selectedVerification = ref<any>(null)

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
  let result = [...(users.value ?? [])]
  if (activeTab.value !== 'all') {
    if (['driver', 'shipper', 'admin'].includes(activeTab.value)) {
      result = result.filter((u: any) => u.role === activeTab.value)
    } else if (activeTab.value === 'verified') {
      result = result.filter((u: any) => u.verification_status === 'approved')
    } else if (activeTab.value === 'pending') {
      result = result.filter((u: any) => u.verification_status === 'pending')
    } else if (activeTab.value === 'rejected') {
      result = result.filter((u: any) => u.verification_status === 'rejected')
    } else if (activeTab.value === 'suspended') {
      result = result.filter((u: any) => u.suspended)
    }
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

async function openVerificationDetails(user: any) {
  try {
    const { data } = await api.get('/verification/admin/list', {
      params: { search: user.email, status: 'all' }
    })
    const record = data?.find((v: any) => v.userId === user.id)
    
    if (record) {
      selectedVerification.value = record
    } else {
      selectedVerification.value = {
        id: user.id,
        userId: user.id,
        userName: user.name,
        userEmail: user.email,
        userRole: user.role,
        status: user.verification_status || 'none',
      }
    }
  } catch(e) {
    selectedVerification.value = {
      id: user.id,
      userId: user.id,
      userName: user.name,
      userEmail: user.email,
      userRole: user.role,
      status: user.verification_status || 'pending',
    }
  }
  verificationDialogOpen.value = true
}

watch([user, loading], ([u, l]) => {
  if (!l && (!u || u.role !== 'admin')) router.replace('/login')
})
</script>

<template>
  <div class="flex-1 p-6 sm:p-8">
    <div v-if="loading" class="max-w-7xl mx-auto">
      <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 auto-rows-fr gap-2.5 mb-6">
        <Card v-for="i in 8" :key="i">
          <CardContent class="p-3">
            <div class="flex items-center gap-2.5">
              <Skeleton class="w-8 h-8 rounded-md shrink-0" />
              <div class="space-y-1.5 min-w-0">
                <Skeleton class="h-4 w-10" />
                <Skeleton class="h-3 w-14" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      <Card>
        <CardHeader class="py-4 px-5">
          <Skeleton class="h-6 w-24 mb-4" />
          <Skeleton class="h-9 w-full" />
        </CardHeader>
        <CardContent class="px-5 pb-5">
          <div class="space-y-3">
            <div v-for="i in 5" :key="i" class="flex items-center gap-3 py-2">
              <Skeleton class="w-7 h-7 rounded-full" />
              <div class="flex-1 space-y-1.5">
                <Skeleton class="h-4 w-28" />
                <Skeleton class="h-3 w-40" />
              </div>
              <Skeleton class="h-6 w-14" />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <div v-else-if="user && user.role === 'admin'" class="max-w-7xl mx-auto">
      <!-- Admin Portal Navigation Header -->
      <div class="mb-6 p-5 rounded-2xl bg-gradient-to-r from-gray-900 to-teal-950 text-white flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl">
        <div>
          <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-teal-500/20 border border-teal-500/30 text-[10px] font-bold uppercase tracking-wider text-teal-300">
            <span>🛡️</span> RoadLancer Admin Portal
          </div>
          <h2 class="text-xl font-black text-white mt-1">System Administration & Helpdesk</h2>
        </div>
        <div class="flex items-center gap-2 flex-wrap">
          <a
            href="/admin"
            class="px-4 py-2 rounded-xl bg-teal-600 text-white font-extrabold text-xs shadow-md hover:bg-teal-500 transition-all flex items-center gap-1.5"
          >
            <span>👥</span> User Management
          </a>
          <a
            href="/admin/support"
            class="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white font-extrabold text-xs transition-all flex items-center gap-1.5"
          >
            <span>🎧</span> Support Desk & Inbound Emails
          </a>
        </div>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 auto-rows-fr gap-2.5 mb-6">
        <Card
          @click="activeTab = 'all'"
          class="cursor-pointer transition-all hover:border-primary/50"
          :class="activeTab === 'all' ? 'ring-2 ring-primary border-primary bg-primary/5' : ''"
        >
          <CardContent class="p-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-primary/10 rounded-md flex items-center justify-center shrink-0">
                <Users class="size-4 text-primary" />
              </div>
              <div class="min-w-0">
                <p class="text-lg font-bold leading-none mb-1">{{ stats.total }}</p>
                <p class="text-[11px] text-muted-foreground truncate">Total Users</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card
          @click="activeTab = 'driver'"
          class="cursor-pointer transition-all hover:border-blue-500/50"
          :class="activeTab === 'driver' ? 'ring-2 ring-blue-600 border-blue-600 bg-blue-500/5' : ''"
        >
          <CardContent class="p-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-blue-500/10 rounded-md flex items-center justify-center shrink-0">
                <UserCheck class="size-4 text-blue-600" />
              </div>
              <div class="min-w-0">
                <p class="text-lg font-bold leading-none mb-1">{{ stats.drivers }}</p>
                <p class="text-[11px] text-muted-foreground truncate">Drivers</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card
          @click="activeTab = 'shipper'"
          class="cursor-pointer transition-all hover:border-green-500/50"
          :class="activeTab === 'shipper' ? 'ring-2 ring-green-600 border-green-600 bg-green-500/5' : ''"
        >
          <CardContent class="p-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-green-500/10 rounded-md flex items-center justify-center shrink-0">
                <UserCheck class="size-4 text-green-600" />
              </div>
              <div class="min-w-0">
                <p class="text-lg font-bold leading-none mb-1">{{ stats.shippers }}</p>
                <p class="text-[11px] text-muted-foreground truncate">Shippers</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card
          @click="activeTab = 'admin'"
          class="cursor-pointer transition-all hover:border-amber-500/50"
          :class="activeTab === 'admin' ? 'ring-2 ring-amber-600 border-amber-600 bg-amber-500/5' : ''"
        >
          <CardContent class="p-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-amber-500/10 rounded-md flex items-center justify-center shrink-0">
                <Shield class="size-4 text-amber-600" />
              </div>
              <div class="min-w-0">
                <p class="text-lg font-bold leading-none mb-1">{{ stats.admins }}</p>
                <p class="text-[11px] text-muted-foreground truncate">Admins</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card
          @click="activeTab = 'verified'"
          class="cursor-pointer transition-all hover:border-green-500/50"
          :class="activeTab === 'verified' ? 'ring-2 ring-green-600 border-green-600 bg-green-500/5' : ''"
        >
          <CardContent class="p-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-green-500/10 rounded-md flex items-center justify-center shrink-0">
                <ShieldCheck class="size-4 text-green-600" />
              </div>
              <div class="min-w-0">
                <p class="text-lg font-bold leading-none mb-1">{{ verifiedCount.data.value ?? 0 }}</p>
                <p class="text-[11px] text-muted-foreground truncate">Verified</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card
          @click="activeTab = 'pending'"
          class="cursor-pointer transition-all hover:border-orange-500/50"
          :class="activeTab === 'pending' ? 'ring-2 ring-orange-600 border-orange-600 bg-orange-500/5' : ''"
        >
          <CardContent class="p-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-orange-500/10 rounded-md flex items-center justify-center shrink-0">
                <Clock class="size-4 text-orange-600" />
              </div>
              <div class="min-w-0">
                <p class="text-lg font-bold leading-none mb-1">{{ pendingCount.data.value ?? 0 }}</p>
                <p class="text-[11px] text-muted-foreground truncate">Pending</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card
          @click="activeTab = 'rejected'"
          class="cursor-pointer transition-all hover:border-destructive/50"
          :class="activeTab === 'rejected' ? 'ring-2 ring-destructive border-destructive bg-destructive/5' : ''"
        >
          <CardContent class="p-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-red-500/10 rounded-md flex items-center justify-center shrink-0">
                <XCircle class="size-4 text-red-600" />
              </div>
              <div class="min-w-0">
                <p class="text-lg font-bold leading-none mb-1">{{ rejectedCount.data.value ?? 0 }}</p>
                <p class="text-[11px] text-muted-foreground truncate">Rejected</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card
          @click="activeTab = 'suspended'"
          class="cursor-pointer transition-all hover:border-red-500/50"
          :class="activeTab === 'suspended' ? 'ring-2 ring-red-600 border-red-600 bg-red-500/5' : ''"
        >
          <CardContent class="p-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-red-500/10 rounded-md flex items-center justify-center shrink-0">
                <UserX class="size-4 text-red-600" />
              </div>
              <div class="min-w-0">
                <p class="text-lg font-bold leading-none mb-1">{{ stats.suspended }}</p>
                <p class="text-[11px] text-muted-foreground truncate">Suspended</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Alert v-if="error" variant="destructive" class="mb-6">
        <AlertCircle class="h-4 w-4" />
        <AlertDescription>{{ error.message }}</AlertDescription>
      </Alert>

      <Card class="border shadow-sm">
        <CardHeader class="pb-4 border-b border-border bg-card/50">
          <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div class="flex flex-wrap items-center gap-3">
              <CardTitle class="mr-1 text-lg font-bold text-foreground">User Management</CardTitle>
              <Button size="sm" class="bg-primary hover:bg-primary/90 text-primary-foreground h-8 text-xs font-semibold shadow-2xs" @click="router.push('/admin/verifications')">
                <ShieldCheck class="size-3.5 mr-1.5" /> Review Verification Docs
              </Button>
            </div>
            <div class="flex flex-wrap items-center gap-2.5">
              <div class="relative">
                <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                <Input
                  v-model="searchQuery"
                  placeholder="Search users..."
                  class="pl-9 w-52 h-9 text-xs"
                />
              </div>

              <Button variant="outline" size="sm" class="h-9 text-xs font-semibold" @click="refetchAll" :disabled="loadingUsers">
                <LoaderCircle v-if="loadingUsers" class="size-3.5 animate-spin mr-1.5" />
                Refresh
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent class="p-4 sm:p-6">
          <UsersTable
            :users="filteredUsers"
            :loading="loadingUsers"
            :suspend-pending="suspendMutation.isPending.value"
            v-model:sorting="userSorting"
            @suspend="openSuspendDialog"
            @unsuspend="unsuspendUser"
            @view-verification="openVerificationDetails"
          />
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

      <!-- Verification Details Dialog -->
      <VerificationDetailDialog
        :open="verificationDialogOpen"
        :verification="selectedVerification"
        :show-actions="false"
        @update:open="verificationDialogOpen = $event"
      />
    </div>
  </div>
</template>
