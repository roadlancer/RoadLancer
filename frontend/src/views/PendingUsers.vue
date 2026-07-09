<script lang="ts" setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { usePendingUsers } from '@/composables/usePendingUsers'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Dialog, DialogContent, DialogDescription, DialogFooter,
  DialogHeader, DialogTitle,
} from '@/components/ui/dialog'
import { LoaderCircle, Search, AlertCircle, CheckCircle, XCircle, ArrowLeft } from '@lucide/vue'

const router = useRouter()
const { user, loading } = useAuth()

const {
  data: users,
  isLoading: loadingUsers,
  error,
  searchQuery,
  approveMutation,
  rejectMutation,
} = usePendingUsers()

const rejectDialogOpen = ref(false)
const rejectTarget = ref<any>(null)
const rejectReason = ref('')

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
  if (!searchQuery.value) return users.value ?? []
  const q = searchQuery.value.toLowerCase()
  return (users.value ?? []).filter((u: any) =>
    u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)
  )
})

function approveUser(userId: string) {
  approveMutation.mutate(userId)
}

function openRejectDialog(u: any) {
  rejectTarget.value = u
  rejectReason.value = ''
  rejectDialogOpen.value = true
}

function confirmReject() {
  if (!rejectTarget.value || !rejectReason.value) return
  rejectMutation.mutate(
    { userId: rejectTarget.value.id, reason: rejectReason.value },
    { onSuccess: () => { rejectDialogOpen.value = false } },
  )
}

watch([user, loading], ([u, l]) => {
  if (!l && (!u || u.role !== 'admin')) router.replace('/login')
})
</script>

<template>
  <div class="flex-1 p-8">
    <div v-if="loading" class="max-w-5xl mx-auto">
      <div class="flex items-center gap-4 mb-8">
        <Skeleton class="h-9 w-24" />
        <div>
          <Skeleton class="h-9 w-48 mb-1" />
          <Skeleton class="h-5 w-64" />
        </div>
      </div>
      <Card>
        <CardHeader>
          <Skeleton class="h-6 w-32 mb-4" />
          <Skeleton class="h-10 w-full" />
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div v-for="i in 3" :key="i" class="flex items-center gap-4 p-4">
              <Skeleton class="w-10 h-10 rounded-full" />
              <div class="flex-1 space-y-2">
                <Skeleton class="h-4 w-32" />
                <Skeleton class="h-3 w-48" />
              </div>
              <div class="flex gap-2">
                <Skeleton class="h-8 w-20" />
                <Skeleton class="h-8 w-16" />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <div v-else-if="user && user.role === 'admin'" class="max-w-5xl mx-auto">
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

      <Alert v-if="error" variant="destructive" class="mb-6">
        <AlertCircle class="h-4 w-4" />
        <AlertDescription>{{ error.message }}</AlertDescription>
      </Alert>

      <Card>
        <CardHeader>
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div class="flex items-center gap-3">
              <CardTitle>Pending Users</CardTitle>
              <Badge variant="secondary" class="text-xs">{{ users?.length ?? 0 }}</Badge>
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
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div v-if="loadingUsers" class="space-y-4">
            <div v-for="i in 3" :key="i" class="flex items-center gap-4 p-4">
              <Skeleton class="w-10 h-10 rounded-full" />
              <div class="flex-1 space-y-2">
                <Skeleton class="h-4 w-32" />
                <Skeleton class="h-3 w-48" />
                <div class="flex gap-2 mt-1">
                  <Skeleton class="h-4 w-16" />
                  <Skeleton class="h-4 w-24" />
                </div>
              </div>
              <div class="flex gap-2">
                <Skeleton class="h-8 w-20" />
                <Skeleton class="h-8 w-16" />
              </div>
            </div>
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
                  <div class="flex flex-wrap items-center gap-2 mt-1">
                    <Badge variant="secondary" class="capitalize text-xs">{{ u.role }}</Badge>
                    <Badge v-if="u.verification_status === 'pending'" class="bg-amber-100 text-amber-800 border border-amber-200 text-[10px]">Docs Submitted</Badge>
                    <Badge v-else-if="u.verification_status === 'none'" variant="outline" class="text-muted-foreground text-[10px]">No Docs Yet</Badge>
                    <span v-if="u.phone" class="text-xs text-muted-foreground">{{ u.phone }}</span>
                    <span class="text-xs text-muted-foreground">
                      Registered {{ new Date(u.created_at!).toLocaleDateString() }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="flex flex-wrap items-center gap-2 sm:ml-4">
                <router-link v-if="u.verification_status === 'pending'" to="/admin/verifications" class="inline-block">
                  <Button variant="outline" size="sm" class="border-amber-500/30 text-amber-600 dark:text-amber-400 hover:bg-amber-500/10 font-semibold text-xs h-8">
                    Review Docs
                  </Button>
                </router-link>
                <Button
                  variant="default"
                  size="sm"
                  :disabled="approveMutation.isPending.value || rejectMutation.isPending.value"
                  @click="approveUser(u.id)"
                >
                  <LoaderCircle v-if="approveMutation.isPending.value" class="size-3 animate-spin mr-1" />
                  <CheckCircle v-else class="size-3 mr-1" />
                  Approve
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  :disabled="approveMutation.isPending.value || rejectMutation.isPending.value"
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
              :disabled="!rejectReason || rejectMutation.isPending.value"
              @click="confirmReject"
            >
              <LoaderCircle v-if="rejectMutation.isPending.value" class="size-4 animate-spin mr-1" />
              {{ rejectMutation.isPending.value ? 'Rejecting...' : 'Confirm Rejection' }}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  </div>
</template>
