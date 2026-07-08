<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAdminTickets, type SupportTicket } from '@/composables/useSupportTickets'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'

const {
  tickets,
  isLoading,
  counts,
  searchQuery,
  statusFilter,
  sourceFilter,
  updateStatus,
  isUpdating,
} = useAdminTickets()

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
      return 'bg-amber-100 text-amber-800 border-amber-300'
    case 'in_progress':
      return 'bg-blue-100 text-blue-800 border-blue-300'
    case 'resolved':
      return 'bg-emerald-100 text-emerald-800 border-emerald-300'
    case 'closed':
      return 'bg-gray-200 text-gray-800 border-gray-400'
    default:
      return 'bg-gray-100 text-gray-800 border-gray-300'
  }
}

function getPriorityBadgeClass(priority: string) {
  switch (priority) {
    case 'urgent':
      return 'bg-red-500 text-white font-black animate-pulse'
    case 'high':
      return 'bg-orange-100 text-orange-800 border-orange-300 font-bold'
    case 'normal':
      return 'bg-blue-50 text-blue-700 border-blue-200'
    default:
      return 'bg-gray-50 text-gray-600 border-gray-200'
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header Banner -->
    <div class="bg-gradient-to-r from-teal-900 via-teal-800 to-blue-900 rounded-3xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
      <div class="relative z-10 max-w-3xl space-y-2">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-xs font-bold uppercase tracking-wider text-teal-200">
          <span>🎧</span> Admin Helpdesk & Inbound Email Portal
        </div>
        <h1 class="text-3xl sm:text-4xl font-black tracking-tight text-white">
          Support Tickets & Profile Edit Trails
        </h1>
        <p class="text-xs sm:text-sm text-teal-100/90 leading-relaxed max-w-2xl">
          Review tickets converted from inbound emails (<span class="font-mono underline">support@roadlancer.com</span>) and manage user profile edit requests.
        </p>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <Card class="rounded-2xl border-2 border-gray-100 shadow-sm bg-white overflow-hidden">
        <CardContent class="p-5 flex items-center justify-between">
          <div>
            <p class="text-xs font-bold uppercase tracking-wider text-gray-400">Total Tickets</p>
            <p class="text-3xl font-black text-gray-900 mt-1">{{ counts?.total || 0 }}</p>
          </div>
          <div class="w-12 h-12 rounded-2xl bg-gray-100 flex items-center justify-center text-2xl">📋</div>
        </CardContent>
      </Card>

      <Card class="rounded-2xl border-2 border-amber-200 shadow-sm bg-amber-50/50 overflow-hidden">
        <CardContent class="p-5 flex items-center justify-between">
          <div>
            <p class="text-xs font-bold uppercase tracking-wider text-amber-700">Open / Pending</p>
            <p class="text-3xl font-black text-amber-900 mt-1">{{ counts?.open || 0 }}</p>
          </div>
          <div class="w-12 h-12 rounded-2xl bg-amber-100 flex items-center justify-center text-2xl">⏳</div>
        </CardContent>
      </Card>

      <Card class="rounded-2xl border-2 border-blue-200 shadow-sm bg-blue-50/50 overflow-hidden">
        <CardContent class="p-5 flex items-center justify-between">
          <div>
            <p class="text-xs font-bold uppercase tracking-wider text-blue-700">Inbound Emails</p>
            <p class="text-3xl font-black text-blue-900 mt-1">{{ counts?.inbound_email || 0 }}</p>
          </div>
          <div class="w-12 h-12 rounded-2xl bg-blue-100 flex items-center justify-center text-2xl">📧</div>
        </CardContent>
      </Card>

      <Card class="rounded-2xl border-2 border-emerald-200 shadow-sm bg-emerald-50/50 overflow-hidden">
        <CardContent class="p-5 flex items-center justify-between">
          <div>
            <p class="text-xs font-bold uppercase tracking-wider text-emerald-700">Resolved</p>
            <p class="text-3xl font-black text-emerald-900 mt-1">{{ counts?.resolved || 0 }}</p>
          </div>
          <div class="w-12 h-12 rounded-2xl bg-emerald-100 flex items-center justify-center text-2xl">✅</div>
        </CardContent>
      </Card>
    </div>

    <!-- Filter & Search Bar -->
    <Card class="rounded-2xl border border-gray-200 shadow-sm bg-white p-4">
      <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div class="flex items-center gap-3 w-full sm:w-auto flex-wrap">
          <div class="w-full sm:w-48">
            <select
              v-model="statusFilter"
              class="w-full h-10 px-3 py-2 bg-gray-50 border border-gray-300 rounded-xl text-xs font-bold text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500"
            >
              <option value="all">All Statuses</option>
              <option value="open">Open / Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
          </div>
          <div class="w-full sm:w-48">
            <select
              v-model="sourceFilter"
              class="w-full h-10 px-3 py-2 bg-gray-50 border border-gray-300 rounded-xl text-xs font-bold text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500"
            >
              <option value="all">All Sources</option>
              <option value="email">📧 Inbound Email</option>
              <option value="web">🌐 Web Form</option>
            </select>
          </div>
        </div>

        <div class="w-full sm:w-80">
          <Input
            v-model="searchQuery"
            placeholder="Search by Ticket #, Email, Subject..."
            class="bg-gray-50 border-gray-300 rounded-xl text-xs"
          />
        </div>
      </div>
    </Card>

    <!-- Tickets Table -->
    <Card class="rounded-2xl border border-gray-200 shadow-sm bg-white overflow-hidden">
      <div v-if="isLoading" class="text-center py-12 text-gray-500 text-xs">
        Loading support tickets...
      </div>
      <div v-else-if="!tickets || tickets.length === 0" class="text-center py-12 bg-gray-50">
        <div class="text-4xl mb-2">📭</div>
        <p class="text-xs font-bold text-gray-600">No support tickets match your filters.</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-gray-50/80 border-b border-gray-200 text-[11px] font-extrabold text-gray-500 uppercase tracking-wider">
              <th class="py-3 px-4">Ticket #</th>
              <th class="py-3 px-4">Sender & Account</th>
              <th class="py-3 px-4">Subject</th>
              <th class="py-3 px-4">Source</th>
              <th class="py-3 px-4">Priority</th>
              <th class="py-3 px-4">Status</th>
              <th class="py-3 px-4">Created At</th>
              <th class="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-150 text-xs">
            <tr
              v-for="t in tickets"
              :key="t.id"
              class="hover:bg-teal-50/30 transition-colors duration-150"
            >
              <td class="py-3.5 px-4 font-mono font-bold text-gray-900">
                {{ t.ticket_number }}
              </td>
              <td class="py-3.5 px-4">
                <div class="font-bold text-gray-900">{{ t.sender_name || t.sender_email }}</div>
                <div class="text-[11px] font-mono text-gray-500">{{ t.sender_email }}</div>
                <div v-if="t.user" class="mt-1 flex items-center gap-1">
                  <Badge class="bg-teal-100 text-teal-800 text-[9px] px-1.5 py-0 uppercase font-bold border border-teal-200">
                    {{ t.user.role }}
                  </Badge>
                  <span v-if="t.user.phone" class="text-[10px] text-gray-400 font-mono">📞 {{ t.user.phone }}</span>
                </div>
              </td>
              <td class="py-3.5 px-4 font-bold text-gray-800 max-w-xs truncate">
                {{ t.subject }}
              </td>
              <td class="py-3.5 px-4">
                <Badge v-if="t.source === 'email'" class="bg-blue-100 text-blue-800 text-[10px] border border-blue-200">
                  📧 Email
                </Badge>
                <Badge v-else class="bg-purple-100 text-purple-800 text-[10px] border border-purple-200">
                  🌐 Web
                </Badge>
              </td>
              <td class="py-3.5 px-4">
                <Badge :class="['text-[10px] px-2 py-0.5 uppercase border', getPriorityBadgeClass(t.priority)]">
                  {{ t.priority }}
                </Badge>
              </td>
              <td class="py-3.5 px-4">
                <Badge :class="['text-[10px] font-extrabold uppercase px-2 py-0.5 border', getStatusBadgeClass(t.status)]">
                  {{ t.status }}
                </Badge>
              </td>
              <td class="py-3.5 px-4 text-[11px] font-mono text-gray-500">
                {{ new Date(t.created_at).toLocaleDateString() }}
              </td>
              <td class="py-3.5 px-4 text-right space-x-2">
                <Button
                  size="sm"
                  variant="outline"
                  class="text-xs font-bold bg-white hover:bg-gray-100 border-gray-300"
                  @click="openInspect(t)"
                >
                  🔍 Inspect / Reply
                </Button>
                <Button
                  v-if="t.status !== 'resolved'"
                  size="sm"
                  class="text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white"
                  @click="handleQuickResolve(t)"
                >
                  ✅ Resolve
                </Button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>

    <!-- Ticket Inspect & Reply Dialog -->
    <Dialog :open="isInspectOpen" @update:open="isInspectOpen = $event">
      <DialogContent class="max-w-xl max-h-[90vh] overflow-y-auto p-6 rounded-2xl bg-white border-2 border-gray-200 shadow-2xl">
        <DialogHeader v-if="selectedTicket">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <Badge class="bg-gray-900 text-white font-mono font-bold text-sm px-2.5 py-1">
                {{ selectedTicket.ticket_number }}
              </Badge>
              <Badge :class="['text-xs font-extrabold uppercase px-2.5 py-0.5 border', getStatusBadgeClass(selectedTicket.status)]">
                {{ selectedTicket.status }}
              </Badge>
            </div>
            <span class="text-xs font-mono text-gray-400">
              {{ new Date(selectedTicket.created_at).toLocaleString() }}
            </span>
          </div>
          <DialogTitle class="text-xl font-black text-gray-900 mt-3">
            {{ selectedTicket.subject }}
          </DialogTitle>
          <DialogDescription class="text-xs text-gray-500 flex items-center gap-2 mt-1">
            <span>From: <strong class="text-gray-700">{{ selectedTicket.sender_name || selectedTicket.sender_email }}</strong> (&lt;{{ selectedTicket.sender_email }}&gt;)</span>
          </DialogDescription>
        </DialogHeader>

        <div v-if="selectedTicket" class="space-y-5 my-2">
          <!-- User Profile Box -->
          <div v-if="selectedTicket.user" class="p-3.5 rounded-xl bg-teal-50/80 border border-teal-200 flex items-center justify-between text-xs">
            <div>
              <div class="font-bold text-teal-950 flex items-center gap-1.5">
                <span>👤</span> Linked RoadLancer Account:
                <Badge class="bg-teal-700 text-white text-[10px] uppercase font-bold px-1.5 py-0">
                  {{ selectedTicket.user.role }}
                </Badge>
              </div>
              <p class="text-teal-800 mt-0.5">
                {{ selectedTicket.user.name }} — <span class="font-mono">{{ selectedTicket.user.email }}</span>
              </p>
            </div>
            <a
              href="/admin"
              class="px-3 py-1.5 rounded-lg bg-white border border-teal-300 text-teal-900 font-bold hover:bg-teal-100 transition-colors text-xs shadow-sm"
            >
              Verify Profile →
            </a>
          </div>

          <!-- Message Body -->
          <div class="space-y-1">
            <Label class="text-xs font-bold uppercase tracking-wider text-gray-400">Message Content</Label>
            <div class="p-4 rounded-xl bg-gray-50 border border-gray-200 text-xs text-gray-800 leading-relaxed font-sans whitespace-pre-wrap">
              {{ selectedTicket.message }}
            </div>
          </div>

          <!-- Admin Management Box -->
          <div class="p-4 rounded-xl bg-gray-100/80 border border-gray-200 space-y-4">
            <div class="font-bold text-xs text-gray-900 flex items-center gap-1.5">
              <span>🛡️</span> Admin Status & Reply Management
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div class="space-y-1">
                <Label class="text-xs font-bold text-gray-700">Update Status</Label>
                <select
                  v-model="replyStatus"
                  class="w-full h-9 px-3 bg-white border border-gray-300 rounded-lg text-xs font-bold text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="open">Open / Pending</option>
                  <option value="in_progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                  <option value="closed">Closed</option>
                </select>
              </div>
              <div class="space-y-1">
                <Label class="text-xs font-bold text-gray-700">Priority</Label>
                <select
                  v-model="replyPriority"
                  class="w-full h-9 px-3 bg-white border border-gray-300 rounded-lg text-xs font-bold text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="low">Low</option>
                  <option value="normal">Normal</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
            </div>

            <div class="space-y-1">
              <Label class="text-xs font-bold text-gray-700">Admin Reply / Internal Notes</Label>
              <textarea
                v-model="replyNotes"
                rows="3"
                placeholder="Type your response or resolution note (e.g., 'Profile edit request approved and license updated')..."
                class="flex w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-xs placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-teal-500 leading-relaxed"
              />
            </div>
          </div>

          <div class="flex items-center justify-end gap-3 pt-2">
            <Button
              variant="outline"
              size="sm"
              class="text-xs font-bold"
              @click="isInspectOpen = false"
            >
              Cancel
            </Button>
            <Button
              size="sm"
              @click="handleSaveReply"
              :disabled="isUpdating"
              class="bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs px-5"
            >
              <span v-if="isUpdating">⏳ Saving...</span>
              <span v-else>💾 Save Status & Send Reply</span>
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  </div>
</template>
