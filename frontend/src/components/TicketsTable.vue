<script lang="ts" setup>
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import type { SupportTicket } from '@/composables/useSupportTickets'
import { MessageSquare, Mail, Globe, CheckCircle2, Clock, AlertCircle, ShieldAlert, Phone } from '@lucide/vue'

defineProps<{
  tickets: SupportTicket[]
  loading?: boolean
  sortBy?: string
}>()

const emit = defineEmits<{
  (e: 'inspect', ticket: SupportTicket): void
  (e: 'resolve', ticket: SupportTicket): void
}>()

function getStatusBadgeClass(status: string) {
  switch (status) {
    case 'open':
      return 'bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300'
    case 'in_progress':
      return 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300'
    case 'resolved':
      return 'bg-green-100 text-green-800 border-green-200 dark:bg-green-950/40 dark:text-green-300'
    case 'closed':
      return 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-800 dark:text-gray-300'
    default:
      return 'bg-muted text-muted-foreground border-border'
  }
}

function getPriorityBadgeClass(priority: string) {
  switch (priority) {
    case 'urgent':
      return 'bg-red-500 text-white font-bold animate-pulse'
    case 'high':
      return 'bg-orange-100 text-orange-800 border-orange-200 font-semibold'
    case 'normal':
      return 'bg-blue-50 text-blue-700 border-blue-200'
    default:
      return 'bg-muted text-muted-foreground border-border'
  }
}
</script>

<template>
  <div>
    <div v-if="!loading && tickets && tickets.length > 0" class="pb-3 mb-3 border-b border-border flex items-center justify-between text-xs text-muted-foreground">
      <span class="font-medium">Showing <strong class="text-foreground font-semibold">{{ tickets.length }}</strong> support ticket{{ tickets.length === 1 ? '' : 's' }}</span>
      <span class="font-mono text-[11px] text-primary font-semibold bg-primary/5 px-2.5 py-1 rounded-md border border-primary/20">
        Sorted by: {{ sortBy === 'oldest' ? 'Oldest First' : sortBy === 'priority' ? 'Priority (High → Low)' : sortBy === 'status' ? 'Status (Open → Closed)' : 'Newest First' }}
      </span>
    </div>

    <div v-if="loading" class="space-y-4 py-2">
      <div v-for="i in 5" :key="i" class="flex items-center gap-4 p-3">
        <Skeleton class="w-8 h-8 rounded-full shrink-0" />
        <div class="flex-1 space-y-2">
          <Skeleton class="h-4 w-32" />
          <Skeleton class="h-3 w-48" />
        </div>
        <Skeleton class="h-6 w-16" />
        <Skeleton class="h-6 w-20" />
      </div>
    </div>

    <div v-else-if="!tickets || tickets.length === 0" class="text-center py-12">
      <MessageSquare class="size-12 text-muted-foreground/50 mx-auto mb-3" />
      <p class="text-muted-foreground font-medium">No support tickets found</p>
      <p class="text-xs text-muted-foreground/80 mt-1">Try adjusting your status, source, or search filters.</p>
    </div>

    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-border text-xs text-muted-foreground">
            <th class="text-left py-3 px-2 font-medium">Ticket #</th>
            <th class="text-left py-3 px-2 font-medium">Sender & Account</th>
            <th class="text-left py-3 px-2 font-medium">Subject</th>
            <th class="text-left py-3 px-2 font-medium">Source</th>
            <th class="text-left py-3 px-2 font-medium">Priority</th>
            <th class="text-left py-3 px-2 font-medium">Status</th>
            <th class="text-left py-3 px-2 font-medium">Created At</th>
            <th class="text-right py-3 px-2 font-medium">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="t in tickets"
            :key="t.id"
            class="border-b border-border last:border-0 hover:bg-muted/50 transition-colors"
          >
            <td class="py-3.5 px-2 font-mono font-semibold text-foreground">
              {{ t.ticket_number }}
            </td>
            <td class="py-3.5 px-2">
              <div>
                <p class="font-medium text-foreground leading-tight">{{ t.sender_name || t.sender_email }}</p>
                <p class="text-xs font-mono text-muted-foreground mt-0.5">{{ t.sender_email }}</p>
                <div v-if="t.user" class="mt-1 flex items-center gap-1.5 flex-wrap">
                  <Badge variant="secondary" class="text-[10px] px-1.5 py-0 uppercase font-semibold">
                    {{ t.user.role }}
                  </Badge>
                  <span v-if="t.user.phone" class="text-[11px] text-muted-foreground font-mono flex items-center gap-1">
                    <Phone class="size-3 text-muted-foreground" /> {{ t.user.phone }}
                  </span>
                </div>
              </div>
            </td>
            <td class="py-3.5 px-2 font-medium text-foreground max-w-xs truncate">
              {{ t.subject }}
            </td>
            <td class="py-3.5 px-2">
              <Badge v-if="t.source === 'email'" variant="outline" class="bg-blue-50/50 text-blue-700 border-blue-200/80 font-medium text-xs flex items-center gap-1 w-fit">
                <Mail class="size-3 text-blue-600" /> Email
              </Badge>
              <Badge v-else variant="outline" class="bg-purple-50/50 text-purple-700 border-purple-200/80 font-medium text-xs flex items-center gap-1 w-fit">
                <Globe class="size-3 text-purple-600" /> Web
              </Badge>
            </td>
            <td class="py-3.5 px-2">
              <Badge :class="['text-[10px] px-2 py-0.5 uppercase border capitalize', getPriorityBadgeClass(t.priority)]">
                {{ t.priority }}
              </Badge>
            </td>
            <td class="py-3.5 px-2">
              <Badge :class="['text-xs font-semibold px-2.5 py-0.5 border capitalize', getStatusBadgeClass(t.status)]">
                {{ t.status.replace('_', ' ') }}
              </Badge>
            </td>
            <td class="py-3.5 px-2 text-xs text-muted-foreground font-mono whitespace-nowrap">
              {{ new Date(t.created_at).toLocaleDateString() }}
            </td>
            <td class="py-3.5 px-2 text-right space-x-1.5 whitespace-nowrap">
              <Button
                variant="outline"
                size="sm"
                class="h-8 text-xs font-semibold shadow-2xs"
                @click="emit('inspect', t)"
              >
                Inspect / Reply
              </Button>
              <Button
                v-if="t.status !== 'resolved' && t.status !== 'closed'"
                size="sm"
                class="h-8 text-xs font-semibold bg-primary hover:bg-primary/90 text-primary-foreground shadow-2xs"
                @click="emit('resolve', t)"
              >
                Resolve
              </Button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
