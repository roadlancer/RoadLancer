<script lang="ts" setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAdminTicket, useAdminTickets, type SupportTicket } from '@/composables/useSupportTickets'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
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
} from '@lucide/vue'

const route = useRoute()
const router = useRouter()

const ticketId = computed(() => route.params.id as string)
const { ticket, isLoading, isError, error, refetch } = useAdminTicket(ticketId)
const { updateStatus } = useAdminTickets()

const replyNotes = ref('')
const replyStatus = ref<'open' | 'in_progress' | 'resolved' | 'closed'>('open')
const replyPriority = ref<'low' | 'normal' | 'high' | 'urgent'>('normal')
const isSaving = ref(false)

watch(ticket, (t) => {
  if (t) {
    replyNotes.value = t.admin_notes || ''
    replyStatus.value = t.status
    replyPriority.value = t.priority
  }
}, { immediate: true })

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
    case 'resolved':
      return 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border-emerald-500/30 font-semibold'
    case 'closed':
      return 'bg-slate-500/15 text-slate-700 dark:text-slate-400 border-slate-500/30'
    case 'in_progress':
      return 'bg-sky-500/15 text-sky-700 dark:text-sky-400 border-sky-500/30 font-semibold'
    case 'open':
    default:
      return 'bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/30 font-semibold animate-pulse'
  }
}

async function handleSave() {
  if (!ticket.value) return
  isSaving.value = true
  try {
    const updated = await updateStatus({
      id: ticket.value.id,
      status: replyStatus.value,
      adminNotes: replyNotes.value || undefined,
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
          <Badge :class="['text-xs uppercase px-2.5 py-0.5 border font-bold', getStatusBadgeClass(ticket.status)]">
            {{ ticket.status.replace('_', ' ') }}
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
        <!-- Subject Card -->
        <Card class="border-border/80 shadow-xs overflow-hidden rounded-2xl">
          <CardHeader class="bg-muted/30 pb-4 border-b border-border/50">
            <div class="flex items-center justify-between text-xs text-muted-foreground mb-1.5 font-medium">
              <span class="flex items-center gap-1.5">
                <Clock class="size-3.5" /> Created on {{ new Date(ticket.created_at).toLocaleString() }}
              </span>
              <span class="flex items-center gap-1.5 font-mono">
                Source:
                <Badge variant="outline" class="text-[11px] font-semibold uppercase px-2 py-0">
                  {{ ticket.source }}
                </Badge>
              </span>
            </div>
            <CardTitle class="text-xl sm:text-2xl font-bold text-foreground tracking-tight">
              {{ ticket.subject }}
            </CardTitle>
          </CardHeader>
          <CardContent class="p-6">
            <div class="prose prose-sm dark:prose-invert max-w-none text-foreground/90 font-sans leading-relaxed whitespace-pre-line text-sm sm:text-base">
              {{ ticket.message }}
            </div>
          </CardContent>
        </Card>

        <!-- Sender & Linked User Account Card -->
        <Card class="border-border/80 shadow-xs rounded-2xl overflow-hidden">
          <CardHeader class="pb-3 border-b border-border/50 bg-muted/20">
            <CardTitle class="text-base font-bold text-foreground flex items-center gap-2">
              <User class="size-4 text-primary" />
              Sender Information
            </CardTitle>
          </CardHeader>
          <CardContent class="p-5">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <div class="p-3.5 rounded-xl bg-card border border-border/60 space-y-1">
                <span class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Sender Email</span>
                <p class="font-mono font-medium text-foreground text-sm truncate flex items-center gap-2">
                  <Mail class="size-3.5 text-muted-foreground shrink-0" />
                  <a :href="`mailto:${ticket.sender_email}`" class="hover:text-primary">
                    {{ ticket.sender_email }}
                  </a>
                </p>
              </div>

              <div class="p-3.5 rounded-xl bg-card border border-border/60 space-y-1">
                <span class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Sender Name</span>
                <p class="font-semibold text-foreground text-sm truncate">
                  {{ ticket.sender_name || 'Not Provided' }}
                </p>
              </div>
            </div>

            <!-- Linked Profile Box -->
            <div v-if="ticket.user" class="mt-4 p-4 rounded-xl bg-primary/5 border border-primary/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div class="space-y-1">
                <div class="flex items-center gap-2">
                  <Badge variant="secondary" class="text-[10px] uppercase font-bold px-2 py-0.5 bg-primary/10 text-primary">
                    Linked {{ ticket.user.role }} Profile
                  </Badge>
                  <span class="font-bold text-foreground text-sm">{{ ticket.user.name }}</span>
                </div>
                <div class="flex items-center gap-3 text-xs text-muted-foreground font-mono">
                  <span>{{ ticket.user.email }}</span>
                  <span v-if="ticket.user.phone" class="flex items-center gap-1">
                    • <Phone class="size-3" /> {{ ticket.user.phone }}
                  </span>
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                class="h-8 text-xs font-bold shadow-2xs gap-1.5 shrink-0"
                @click="router.push('/admin')"
              >
                Inspect Account <ExternalLink class="size-3.5" />
              </Button>
            </div>
            <div v-else class="mt-4 p-3.5 rounded-xl bg-muted/40 border border-border/60 text-xs text-muted-foreground italic text-center">
              No registered RoadLancer account matched directly with sender email address (`{{ ticket.sender_email }}`).
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Right Column: Resolution & Management Desk -->
      <div class="lg:col-span-1 space-y-6 sticky top-6">
        <Card class="border-border/80 shadow-sm rounded-2xl overflow-hidden bg-card">
          <CardHeader class="pb-3 border-b border-border/50 bg-muted/30">
            <CardTitle class="text-base font-bold text-foreground flex items-center gap-2">
              <MessageSquare class="size-4 text-primary" />
              Ticket Resolution Desk
            </CardTitle>
            <CardDescription class="text-xs text-muted-foreground">
              Update status, priority, and internal resolution logs.
            </CardDescription>
          </CardHeader>

          <CardContent class="p-5 space-y-5">
            <!-- Status Select -->
            <div class="space-y-2">
              <label class="text-xs font-bold text-foreground uppercase tracking-wider block">
                Workflow Status
              </label>
              <select
                v-model="replyStatus"
                class="w-full h-10 px-3 bg-background border border-input rounded-xl text-sm font-semibold text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 transition-shadow"
              >
                <option value="open">Open (Needs Attention)</option>
                <option value="in_progress">In Progress (Investigating)</option>
                <option value="resolved">Resolved (Complete)</option>
                <option value="closed">Closed (Archived)</option>
              </select>
            </div>

            <!-- Priority Select -->
            <div class="space-y-2">
              <label class="text-xs font-bold text-foreground uppercase tracking-wider block">
                Priority Ranking
              </label>
              <select
                v-model="replyPriority"
                class="w-full h-10 px-3 bg-background border border-input rounded-xl text-sm font-semibold text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 transition-shadow"
              >
                <option value="low">Low Priority</option>
                <option value="normal">Normal Priority</option>
                <option value="high">High Priority</option>
                <option value="urgent">Urgent Priority</option>
              </select>
            </div>

            <!-- Admin Notes / Internal Resolution Log -->
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <label class="text-xs font-bold text-foreground uppercase tracking-wider block">
                  Internal Resolution Notes
                </label>
                <span class="text-[10px] text-muted-foreground font-mono">Visible to Admin Only</span>
              </div>
              <textarea
                v-model="replyNotes"
                rows="6"
                placeholder="Document resolution actions, root cause analysis, or follow-up notes..."
                class="w-full p-3.5 bg-background border border-input rounded-xl text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/40 transition-shadow resize-y font-sans leading-relaxed"
              ></textarea>
            </div>
          </CardContent>

          <CardFooter class="p-5 bg-muted/20 border-t border-border/50 flex flex-col gap-2.5">
            <Button
              @click="handleSave"
              :disabled="isSaving"
              class="w-full h-10 font-bold shadow-sm"
            >
              <Save v-if="!isSaving" class="size-4 mr-1.5" />
              {{ isSaving ? 'Saving Resolution...' : 'Save Ticket Resolution' }}
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  </div>
</div>
</template>
