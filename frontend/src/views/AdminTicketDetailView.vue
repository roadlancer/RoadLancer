<script lang="ts" setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  useAdminTicket,
  useAdminTickets,
  type SupportTicket,
  parseAssignedAgent,
  formatAssignedAgentNotes,
  useSupportAgents,
} from '@/composables/useSupportTickets'
import { useAdminUsers } from '@/composables/useAdminUsers'
import { useAuth } from '@/composables/useAuth'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import ReplyForm from '@/components/ReplyForm.vue'
import TicketDetail from '@/components/TicketDetail.vue'
import UpdateTicket from '@/components/UpdateTicket.vue'
import ReplyThread from '@/components/ReplyThread.vue'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  ArrowLeft,
  Mail,
  Globe,
  Phone,
  User,
  CheckCircle,
  Clock,
  AlertTriangle,
  Send,
  Save,
  MessageSquare,
  ExternalLink,
  UserCheck,
  Reply,
  MessageCircle,
  ShieldCheck,
  UserCircle,
  CornerDownRight,
} from '@lucide/vue'

const route = useRoute()
const router = useRouter()

const ticketId = computed(() => route.params.id as string)
const { ticket, isLoading, isError, error, refetch, submitReply, isReplying } = useAdminTicket(ticketId)
const { updateStatus } = useAdminTickets()
const { data: adminUsers } = useAdminUsers()
const { user: authUser } = useAuth()

const replyNotes = ref('')
const replyStatus = ref<'open' | 'in_progress' | 'resolved' | 'closed'>('open')
const replyPriority = ref<'low' | 'normal' | 'high' | 'urgent'>('normal')
const replyCategory = ref<string>('general')
const replyAgentId = ref<string>('')
const replyAgentName = ref<string>('')
const isSaving = ref(false)

async function handleReplySubmit(payload: { message: string; senderName: string }) {
  if (!payload.message.trim() || !submitReply) return
  try {
    await submitReply({
      message: payload.message.trim(),
      senderName: payload.senderName.trim() || authUser.value?.name || replyAgentName.value || 'Sarah Jenkins (Support Lead)',
    })
  } catch (err) {
    console.error('Failed to submit reply:', err)
  }
}

const supportAgents = useSupportAgents()

function assignToMeInDetail() {
  replyAgentId.value = 'admin-lead'
  replyAgentName.value = 'Sarah Jenkins (Support Lead)'
}

const assignedInfo = computed(() => parseAssignedAgent(ticket.value?.admin_notes))

watch(ticket, (t) => {
  if (t) {
    const parsed = parseAssignedAgent(t.admin_notes)
    replyNotes.value = parsed.cleanNotes
    replyAgentId.value = parsed.agentId || ''
    replyAgentName.value = parsed.agentName || ''
    replyStatus.value = t.status
    replyPriority.value = t.priority
    replyCategory.value = t.category || 'general'
  }
}, { immediate: true })

function onAgentSelected(payload: { id: string; name: string }) {
  replyAgentId.value = payload.id
  replyAgentName.value = payload.name
}

function getPriorityBadgeClass(priority: string) {
  switch (priority) {
    case 'urgent':
      return 'bg-red-500/15 text-red-700 dark:text-red-400 border-red-500/30'
    case 'high':
      return 'bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/30'
    case 'normal':
      return 'bg-blue-500/15 text-blue-700 dark:text-blue-400 border-blue-500/30'
    case 'low':
    default:
      return 'bg-slate-500/15 text-slate-700 dark:text-slate-400 border-slate-500/30'
  }
}

function getStatusBadgeClass(status: string) {
  switch (status) {
    case 'new':
      return 'bg-purple-500/15 text-purple-700 dark:text-purple-400 border-purple-500/30 font-bold animate-pulse'
    case 'processing':
      return 'bg-cyan-500/15 text-cyan-700 dark:text-cyan-400 border-cyan-500/30 font-bold animate-pulse'
    case 'resolved':
      return 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border-emerald-500/30 font-semibold'
    case 'closed':
      return 'bg-slate-500/15 text-slate-700 dark:text-slate-400 border-slate-500/30'
    case 'in_progress':
      return 'bg-sky-500/15 text-sky-700 dark:text-sky-400 border-sky-500/30 font-semibold'
    case 'open':
    default:
      return 'bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/30 font-semibold'
  }
}

async function handleSave() {
  if (!ticket.value) return
  isSaving.value = true
  try {
    const formattedNotes = formatAssignedAgentNotes(
      replyAgentId.value || null,
      replyAgentName.value || null,
      replyNotes.value
    )
    const updated = await updateStatus({
      id: ticket.value.id,
      status: replyStatus.value,
      category: replyCategory.value,
      adminNotes: formattedNotes,
      priority: replyPriority.value,
    })
    ticket.value = updated
    alert(`Ticket #${updated.ticket_number} updated successfully!`)
    refetch()
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Failed to save updates.')
  } finally {
    isSaving.value = false
  }
}

async function quickResolve() {
  replyStatus.value = 'resolved'
  await handleSave()
}
</script>

<template>
  <div class="flex-1 p-3 sm:p-4 bg-background">
    <div class="space-y-4 max-w-7xl mx-auto pb-8">
      <!-- Top Bar Navigation -->
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-border pb-3 pt-1">
        <div class="flex items-center gap-3 flex-wrap">
          <Button
            variant="outline"
            size="sm"
            class="h-9 gap-1.5 px-3.5 font-bold text-xs shadow-xs hover:bg-muted/80 border-border"
            @click="router.push('/admin/support')"
          >
            <ArrowLeft class="size-4" />
            Back to Support Desk
          </Button>
          <div class="h-6 w-px bg-border hidden sm:block"></div>
          <div v-if="ticket" class="flex items-center gap-2 flex-wrap">
            <span class="font-mono font-bold text-base text-foreground">
              #{{ ticket.ticket_number }}
          </span>
          <Badge :class="['text-xs uppercase px-2.5 py-0.5 border font-bold', getPriorityBadgeClass(ticket.priority)]">
            {{ ticket.priority }} Priority
          </Badge>
          <Badge variant="outline" class="bg-purple-500/15 text-purple-700 dark:text-purple-300 border-purple-500/30 text-xs px-2.5 py-0.5 font-bold uppercase">
            Category: {{ ticket.category || 'general' }}
          </Badge>
          <Badge :class="['text-xs uppercase px-2.5 py-0.5 border font-bold', getStatusBadgeClass(ticket.status)]">
            {{ ticket.status.replace('_', ' ') }}
          </Badge>
          <Badge v-if="assignedInfo.agentName" variant="outline" class="bg-indigo-500/15 text-indigo-700 dark:text-indigo-300 border-indigo-500/30 text-xs px-2.5 py-0.5 font-bold flex items-center gap-1.5">
            <UserCheck class="size-3 text-indigo-600 dark:text-indigo-400" /> Assigned: {{ assignedInfo.agentName }}
          </Badge>
        </div>
      </div>

      <div v-if="ticket" class="flex items-center gap-2">
        <Button
          v-if="ticket.status !== 'resolved' && ticket.status !== 'closed'"
          variant="default"
          size="sm"
          class="h-9 px-4 text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white shadow-2xs flex items-center gap-1.5"
          @click="quickResolve"
          :disabled="isSaving"
        >
          <CheckCircle class="size-4" />
          Mark as Resolved
        </Button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-pulse">
      <div class="lg:col-span-2 space-y-4">
        <Skeleton class="h-32 w-full rounded-2xl" />
        <Skeleton class="h-64 w-full rounded-2xl" />
      </div>
      <div class="lg:col-span-1 space-y-4">
        <Skeleton class="h-96 w-full rounded-2xl" />
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="isError || !ticket" class="p-12 text-center bg-card border rounded-2xl max-w-lg mx-auto">
      <AlertTriangle class="size-12 text-destructive mx-auto mb-3 opacity-80" />
      <h3 class="text-lg font-bold text-foreground">Ticket Not Found</h3>
      <p class="text-sm text-muted-foreground mt-1 mb-2">
        The support ticket you requested does not exist or has been deleted.
      </p>
      <p v-if="error" class="text-xs font-mono text-destructive/80 bg-destructive/10 p-2 rounded mb-6 max-w-sm mx-auto truncate">
        {{ (error as any)?.response?.data?.detail || (error as any)?.message || 'Unknown error' }}
      </p>
      <Button @click="router.push('/admin/support')">
        Return to Support Desk
      </Button>
    </div>

    <!-- Ticket Details Main Layout -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
      <!-- Left Column: Message & Sender Info -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Ticket Detail Component -->
        <TicketDetail :ticket="ticket" />

        <!-- Reply Thread Component -->
        <ReplyThread :replies="ticket.replies" />

        <!-- Submit New Reply Form Component -->
        <ReplyForm
          :sender-email="ticket.sender_email"
          :customer-name="ticket.sender_name || ticket.user?.name || ''"
          :default-sender-name="authUser?.name || replyAgentName || 'Sarah Jenkins (Support Lead)'"
          :is-submitting="isReplying"
          :show-status-notice="true"
          @submit="handleReplySubmit"
        />
      </div>

      <!-- Right Column: Resolution & Management Desk -->
      <div class="lg:col-span-1 space-y-6 sticky top-6">
        <UpdateTicket
          :status="replyStatus"
          :priority="replyPriority"
          :category="replyCategory"
          :agent-id="replyAgentId"
          :agent-name="replyAgentName"
          :notes="replyNotes"
          :is-saving="isSaving"
          :support-agents="supportAgents"
          @update:status="replyStatus = $event"
          @update:priority="replyPriority = $event"
          @update:category="replyCategory = $event"
          @update:notes="replyNotes = $event"
          @agent-selected="onAgentSelected"
          @assign-to-me="assignToMeInDetail"
          @save="handleSave"
        />
      </div>
    </div>
  </div>
</div>
</template>
