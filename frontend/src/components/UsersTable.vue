<script lang="ts" setup>
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Users, LoaderCircle } from '@lucide/vue'

defineProps<{
  users: any[]
  loading?: boolean
  suspendPending?: boolean
}>()

const emit = defineEmits<{
  (e: 'suspend', user: any): void
  (e: 'unsuspend', userId: string): void
  (e: 'viewVerification', user: any): void
}>()
</script>

<template>
  <div v-if="loading" class="space-y-4">
    <div v-for="i in 5" :key="i" class="flex items-center gap-4 p-3">
      <Skeleton class="w-8 h-8 rounded-full" />
      <div class="flex-1 space-y-2">
        <Skeleton class="h-4 w-32" />
        <Skeleton class="h-3 w-48" />
      </div>
      <Skeleton class="h-6 w-16" />
      <Skeleton class="h-6 w-20" />
    </div>
  </div>

  <div v-else-if="users.length === 0" class="text-center py-12">
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
          v-for="u in users"
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
          <td class="py-3 px-2 space-x-1.5">
            <Badge :variant="u.suspended ? 'destructive' : 'default'">
              {{ u.suspended ? 'Suspended' : 'Active' }}
            </Badge>
            <Badge v-if="u.verification_status === 'approved'" class="bg-green-100 text-green-800 border border-green-200 hover:bg-green-100">Verified</Badge>
            <Badge v-else-if="u.verification_status === 'pending'" class="bg-amber-100 text-amber-800 border border-amber-200 hover:bg-amber-100">Pending</Badge>
            <Badge v-else-if="u.verification_status === 'rejected'" class="bg-red-100 text-red-800 border border-red-200 hover:bg-red-100">Rejected</Badge>
          </td>
          <td class="py-3 px-2 text-right space-x-1.5">
            <Button
              v-if="u.verification_status === 'pending'"
              variant="outline"
              size="sm"
              class="border-amber-500/30 text-amber-600 dark:text-amber-400 hover:bg-amber-500/10 font-semibold h-8 text-xs"
              @click="emit('viewVerification', u)"
            >
              Review Docs
            </Button>
            <Button
              v-if="u.role !== 'admin' && !u.suspended"
              variant="destructive"
              size="sm"
              class="h-8 text-xs"
              @click="emit('suspend', u)"
            >
              Suspend
            </Button>
            <Button
              v-else-if="u.role !== 'admin' && u.suspended"
              variant="outline"
              size="sm"
              class="h-8 text-xs"
              :disabled="suspendPending"
              @click="emit('unsuspend', u.id)"
            >
              <LoaderCircle v-if="suspendPending" class="size-3 animate-spin mr-1" />
              Unsuspend
            </Button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
