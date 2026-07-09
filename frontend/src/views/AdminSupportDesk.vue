<script setup lang="ts">
import { ref, watch } from 'vue'
import { useAdminTickets } from '@/composables/useSupportTickets'
import TicketsTable from '@/components/TicketsTable.vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import {
  MessageSquare,
  Clock,
  LoaderCircle,
  CheckCircle2,
  Mail,
  Globe,
  Search,
  XCircle,
  Sparkles,
} from '@lucide/vue'

const {
  tickets,
  isLoading,
  refetch,
  counts,
  searchQuery,
  statusFilter,
  sourceFilter,
  sortField,
  sortOrder,
  updateStatus,
  isUpdating,
  seedTickets,
  isSeeding,
} = useAdminTickets()

async function handleSeedTickets() {
  if (!confirm('This will clean existing tickets and generate 100 diversified, real-life demo tickets. Continue?')) return
  try {
    await seedTickets()
    await refetch()
    alert('Successfully cleaned and generated 100 diversified support tickets!')
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Failed to seed tickets.')
  }
}

// TanStack Table sorting state — syncs to composable's sortField/sortOrder for server-side sorting
const sorting = ref<SortingState>([])

watch(sorting, (newSorting) => {
  if (newSorting.length > 0) {
    sortField.value = newSorting[0].id
    sortOrder.value = newSorting[0].desc ? 'desc' : 'asc'
  } else {
    sortField.value = null
    sortOrder.value = 'desc'
  }
}, { deep: true })



const selectedTicket = ref<SupportTicket | null>(null)
const isInspectOpen = ref(false)
const replyNotes = ref('')
const replyStatus = ref<'open' | 'in_progress' | 'resolved' | 'closed'>('open')
const replyPriority = ref<'low' | 'normal' | 'high' | 'urgent'>('normal')

function openInspect(ticket: SupportTicket) {
  selectedTicket.value = ticket
  replyNotes.value = ticket.admin_notes || ''
  replyStatus.value = ticket.status
  replyPriority.value = ticket.priority
  isInspectOpen.value = true
}

async function handleSaveReply() {
  if (!selectedTicket.value) return
  try {
    const updated = await updateStatus({
      id: selectedTicket.value.id,
      status: replyStatus.value,
      adminNotes: replyNotes.value || undefined,
      priority: replyPriority.value,
    })
    selectedTicket.value = updated
    alert(`Ticket #${updated.ticket_number} updated successfully!`)
    isInspectOpen.value = false
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Failed to update ticket.')
  }
}

async function handleQuickResolve(ticket: SupportTicket) {
  try {
    await updateStatus({
      id: ticket.id,
      status: 'resolved',
      adminNotes: ticket.admin_notes || 'Resolved by Admin.',
    })
    alert(`Ticket #${ticket.ticket_number} marked as Resolved!`)
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Failed to resolve ticket.')
  }
}

function getStatusBadgeClass(status: string) {
  switch (status) {
    case 'open':
      return 'bg-amber-100 text-amber-800 border-amber-300 dark:bg-amber-950/40 dark:text-amber-300'
    case 'in_progress':
      return 'bg-blue-100 text-blue-800 border-blue-300 dark:bg-blue-950/40 dark:text-blue-300'
    case 'resolved':
      return 'bg-emerald-100 text-emerald-800 border-emerald-300 dark:bg-emerald-950/40 dark:text-emerald-300'
    case 'closed':
      return 'bg-gray-200 text-gray-800 border-gray-400 dark:bg-gray-800 dark:text-gray-300'
    default:
      return 'bg-gray-100 text-gray-800 border-gray-300'
  }
}
</script>

<template>
  <div class="flex-1 p-6 sm:p-8">
    <div class="max-w-7xl mx-auto">
      <!-- Admin Portal Navigation Header (Matching User Management) -->
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
            class="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white font-extrabold text-xs transition-all flex items-center gap-1.5"
          >
            <span>👥</span> User Management
          </a>
          <a
            href="/admin/support"
            class="px-4 py-2 rounded-xl bg-teal-600 text-white font-extrabold text-xs shadow-md hover:bg-teal-500 transition-all flex items-center gap-1.5"
          >
            <span>🎧</span> Support Desk & Inbound Emails
          </a>
        </div>
      </div>

      <!-- KPI Cards Grid (Exact matches with User Management KPI cards style) -->
      <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 auto-rows-fr gap-2.5 mb-6">
        <!-- Card 1: All Tickets -->
        <Card
          @click="statusFilter = 'all'; sourceFilter = 'all'"
          class="cursor-pointer transition-all hover:border-primary/50"
          :class="statusFilter === 'all' && sourceFilter === 'all' ? 'ring-2 ring-primary border-primary bg-primary/5' : ''"
        >
          <CardContent class="p-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-primary/10 rounded-md flex items-center justify-center shrink-0">
                <MessageSquare class="size-4 text-primary" />
              </div>
              <div class="min-w-0">
                <p class="text-lg font-bold leading-none mb-1">{{ counts?.total || 0 }}</p>
                <p class="text-[11px] text-muted-foreground truncate">All Tickets</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Card 2: Open / Pending -->
        <Card
          @click="statusFilter = 'open'; sourceFilter = 'all'"
          class="cursor-pointer transition-all hover:border-amber-500/50"
          :class="statusFilter === 'open' ? 'ring-2 ring-amber-600 border-amber-600 bg-amber-500/5' : ''"
        >
          <CardContent class="p-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-amber-500/10 rounded-md flex items-center justify-center shrink-0">
                <Clock class="size-4 text-amber-600" />
              </div>
              <div class="min-w-0">
                <p class="text-lg font-bold leading-none mb-1">{{ counts?.open || 0 }}</p>
                <p class="text-[11px] text-muted-foreground truncate">Open / Pending</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Card 3: In Progress -->
        <Card
          @click="statusFilter = 'in_progress'; sourceFilter = 'all'"
          class="cursor-pointer transition-all hover:border-blue-500/50"
          :class="statusFilter === 'in_progress' ? 'ring-2 ring-blue-600 border-blue-600 bg-blue-500/5' : ''"
        >
          <CardContent class="p-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-blue-500/10 rounded-md flex items-center justify-center shrink-0">
                <LoaderCircle class="size-4 text-blue-600 animate-spin" />
              </div>
              <div class="min-w-0">
                <p class="text-lg font-bold leading-none mb-1">{{ counts?.in_progress || 0 }}</p>
                <p class="text-[11px] text-muted-foreground truncate">In Progress</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Card 4: Resolved -->
        <Card
          @click="statusFilter = 'resolved'; sourceFilter = 'all'"
          class="cursor-pointer transition-all hover:border-green-500/50"
          :class="statusFilter === 'resolved' ? 'ring-2 ring-green-600 border-green-600 bg-green-500/5' : ''"
        >
          <CardContent class="p-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-green-500/10 rounded-md flex items-center justify-center shrink-0">
                <CheckCircle2 class="size-4 text-green-600" />
              </div>
              <div class="min-w-0">
                <p class="text-lg font-bold leading-none mb-1">{{ counts?.resolved || 0 }}</p>
                <p class="text-[11px] text-muted-foreground truncate">Resolved</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Card 5: Closed -->
        <Card
          @click="statusFilter = 'closed'; sourceFilter = 'all'"
          class="cursor-pointer transition-all hover:border-gray-500/50"
          :class="statusFilter === 'closed' ? 'ring-2 ring-gray-600 border-gray-600 bg-gray-500/5' : ''"
        >
          <CardContent class="p-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-gray-500/10 rounded-md flex items-center justify-center shrink-0">
                <XCircle class="size-4 text-gray-600" />
              </div>
              <div class="min-w-0">
                <p class="text-lg font-bold leading-none mb-1">{{ counts?.closed || 0 }}</p>
                <p class="text-[11px] text-muted-foreground truncate">Closed</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Card 6: Inbound Email -->
        <Card
          @click="sourceFilter = 'email'; statusFilter = 'all'"
          class="cursor-pointer transition-all hover:border-purple-500/50"
          :class="sourceFilter === 'email' ? 'ring-2 ring-purple-600 border-purple-600 bg-purple-500/5' : ''"
        >
          <CardContent class="p-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-purple-500/10 rounded-md flex items-center justify-center shrink-0">
                <Mail class="size-4 text-purple-600" />
              </div>
              <div class="min-w-0">
                <p class="text-lg font-bold leading-none mb-1">{{ counts?.inbound_email || 0 }}</p>
                <p class="text-[11px] text-muted-foreground truncate">Inbound Email</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Card 7: Web Form -->
        <Card
          @click="sourceFilter = 'web'; statusFilter = 'all'"
          class="cursor-pointer transition-all hover:border-teal-500/50"
          :class="sourceFilter === 'web' ? 'ring-2 ring-teal-600 border-teal-600 bg-teal-500/5' : ''"
        >
          <CardContent class="p-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-teal-500/10 rounded-md flex items-center justify-center shrink-0">
                <Globe class="size-4 text-teal-600" />
              </div>
              <div class="min-w-0">
                <p class="text-lg font-bold leading-none mb-1">{{ counts?.web || 0 }}</p>
                <p class="text-[11px] text-muted-foreground truncate">Web Form</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Unified Card with Header Filters and TicketsTable (Matches UsersTable / AdminDashboard structure) -->
      <Card class="border shadow-sm">
        <CardHeader class="pb-4 border-b border-border bg-card/50">
          <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div class="flex items-center gap-3">
              <CardTitle class="mr-1 text-lg font-bold text-foreground">Support Desk & Inbound Email Queue</CardTitle>
            </div>
            <div class="flex flex-wrap items-center gap-2.5">
              <!-- Search box -->
              <div class="relative">
                <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                <Input
                  v-model="searchQuery"
                  placeholder="Search tickets, sender..."
                  class="pl-9 w-52 h-9 text-xs"
                />
              </div>

              <!-- Seed 100 Demo Tickets Button -->
              <Button
                variant="outline"
                size="sm"
                class="h-9 text-xs font-semibold border-amber-500/40 text-amber-600 dark:text-amber-400 hover:bg-amber-500/10"
                @click="handleSeedTickets"
                :disabled="isSeeding"
              >
                <Sparkles v-if="!isSeeding" class="size-3.5 mr-1.5 text-amber-500" />
                <LoaderCircle v-else class="size-3.5 animate-spin mr-1.5" />
                Seed 100 Tickets
              </Button>

              <!-- Refresh Button -->
              <Button variant="outline" size="sm" class="h-9 text-xs font-semibold" @click="refetch()" :disabled="isLoading">
                <LoaderCircle v-if="isLoading" class="size-3.5 animate-spin mr-1.5" />
                Refresh
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent class="p-4 sm:p-6">
          <TicketsTable
            :tickets="tickets ?? []"
            :loading="isLoading"
            v-model:sorting="sorting"
            @inspect="openInspect"
            @resolve="handleQuickResolve"
          />
        </CardContent>
      </Card>

      <!-- Ticket Inspect & Reply Dialog -->
      <Dialog :open="isInspectOpen" @update:open="isInspectOpen = $event">
        <DialogContent class="max-w-xl max-h-[90vh] overflow-y-auto p-6 rounded-2xl bg-card border border-border shadow-2xl">
          <DialogHeader v-if="selectedTicket">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <Badge class="bg-foreground text-background font-mono font-bold text-xs px-2.5 py-1">
                  {{ selectedTicket.ticket_number }}
                </Badge>
                <Badge :class="['text-xs font-bold uppercase px-2.5 py-0.5 border', getStatusBadgeClass(selectedTicket.status)]">
                  {{ selectedTicket.status.replace('_', ' ') }}
                </Badge>
              </div>
              <span class="text-xs font-mono text-muted-foreground">
                {{ new Date(selectedTicket.created_at).toLocaleString() }}
              </span>
            </div>
            <DialogTitle class="text-xl font-bold text-foreground mt-3">
              {{ selectedTicket.subject }}
            </DialogTitle>
            <DialogDescription class="text-xs text-muted-foreground flex items-center gap-2 mt-1">
              <span>From: <strong class="text-foreground">{{ selectedTicket.sender_name || selectedTicket.sender_email }}</strong> (&lt;{{ selectedTicket.sender_email }}&gt;)</span>
            </DialogDescription>
          </DialogHeader>

          <div v-if="selectedTicket" class="space-y-5 my-2">
            <!-- User Profile Box -->
            <div v-if="selectedTicket.user" class="p-3.5 rounded-xl bg-primary/5 border border-primary/20 flex items-center justify-between text-xs">
              <div>
                <div class="font-semibold text-foreground flex items-center gap-1.5">
                  <span>👤</span> Linked RoadLancer Account:
                  <Badge variant="secondary" class="text-[10px] uppercase font-bold px-1.5 py-0">
                    {{ selectedTicket.user.role }}
                  </Badge>
                </div>
                <p class="text-muted-foreground mt-0.5">
                  {{ selectedTicket.user.name }} — <span class="font-mono">{{ selectedTicket.user.email }}</span>
                </p>
              </div>
              <a
                href="/admin"
                class="px-3 py-1.5 rounded-lg bg-background border border-border text-foreground font-semibold hover:bg-muted transition-colors text-xs shadow-2xs"
              >
                Verify Profile →
              </a>
            </div>

            <!-- Message Body -->
            <div class="space-y-1">
              <Label class="text-xs font-bold uppercase tracking-wider text-muted-foreground">Message Content</Label>
              <div class="p-4 rounded-xl bg-muted/40 border border-border text-xs text-foreground leading-relaxed font-sans whitespace-pre-wrap">
                {{ selectedTicket.message }}
              </div>
            </div>

            <!-- Admin Management Box -->
            <div class="p-4 rounded-xl bg-muted/60 border border-border space-y-4">
              <div class="font-semibold text-xs text-foreground flex items-center gap-1.5">
                <span>🛡️</span> Admin Status & Reply Management
              </div>

              <div class="grid grid-cols-2 gap-3">
                <div class="space-y-1">
                  <Label class="text-xs font-semibold text-foreground">Update Status</Label>
                  <select
                    v-model="replyStatus"
                    class="w-full h-9 px-3 bg-background border border-input rounded-lg text-xs font-semibold text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                  >
                    <option value="open">Open / Pending</option>
                    <option value="in_progress">In Progress</option>
                    <option value="resolved">Resolved</option>
                    <option value="closed">Closed</option>
                  </select>
                </div>
                <div class="space-y-1">
                  <Label class="text-xs font-semibold text-foreground">Priority</Label>
                  <select
                    v-model="replyPriority"
                    class="w-full h-9 px-3 bg-background border border-input rounded-lg text-xs font-semibold text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                  >
                    <option value="low">Low</option>
                    <option value="normal">Normal</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>
              </div>

              <div class="space-y-1">
                <Label class="text-xs font-semibold text-foreground">Admin Reply / Internal Notes</Label>
                <textarea
                  v-model="replyNotes"
                  rows="3"
                  placeholder="Type your response or resolution note (e.g., 'Profile edit request approved and license updated')..."
                  class="flex w-full rounded-md border border-input bg-background px-3 py-2 text-xs placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary leading-relaxed"
                />
              </div>
            </div>

            <div class="flex items-center justify-end gap-3 pt-2">
              <Button
                variant="outline"
                size="sm"
                class="text-xs font-semibold"
                @click="isInspectOpen = false"
              >
                Cancel
              </Button>
              <Button
                size="sm"
                @click="handleSaveReply"
                :disabled="isUpdating"
                class="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold text-xs px-5 shadow-2xs"
              >
                <LoaderCircle v-if="isUpdating" class="size-3.5 animate-spin mr-1.5" />
                <span>💾 Save Status & Send Reply</span>
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  </div>
</template>
