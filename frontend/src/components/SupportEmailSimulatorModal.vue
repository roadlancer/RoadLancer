<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useMyTickets, useSupportMutations } from '@/composables/useSupportTickets'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

const props = defineProps<{
  open: boolean
  defaultTab?: string
  defaultSubject?: string
}>()

const emit = defineEmits<{
  (e: 'update:open', val: boolean): void
  (e: 'ticket-created', ticketNum: string): void
}>()

const { user } = useAuth()
const {
  data: myTickets,
  isLoading: isLoadingTickets,
  refetch: refetchMyTickets,
  searchQuery,
  statusFilter,
  sortBy,
} = useMyTickets()
const { simulateEmail, isSimulatingEmail, createTicket, isCreatingTicket } = useSupportMutations()

const sortedMyTickets = computed(() => {
  const list = [...(myTickets.value || [])]
  const priorityMap: Record<string, number> = { urgent: 4, high: 3, normal: 2, low: 1 }
  const statusMap: Record<string, number> = { open: 4, in_progress: 3, resolved: 2, closed: 1 }

  return list.sort((a, b) => {
    const timeA = new Date(a.created_at).getTime() || 0
    const timeB = new Date(b.created_at).getTime() || 0

    if (sortBy.value === 'oldest') {
      return timeA - timeB
    }
    if (sortBy.value === 'priority') {
      const diff = (priorityMap[b.priority || 'normal'] || 0) - (priorityMap[a.priority || 'normal'] || 0)
      return diff !== 0 ? diff : timeB - timeA
    }
    if (sortBy.value === 'status') {
      const diff = (statusMap[b.status || 'open'] || 0) - (statusMap[a.status || 'open'] || 0)
      return diff !== 0 ? diff : timeB - timeA
    }
    return timeB - timeA
  })
})

const activeTab = ref(props.defaultTab || 'email')
const lastCreatedTicket = ref<{ number: string; message: string } | null>(null)
const copySuccess = ref(false)

// Email simulation form state
const emailForm = ref({
  from_email: '',
  from_name: '',
  subject: '',
  body: '',
  priority: 'normal',
})

// Web ticket form state
const webForm = ref({
  subject: '',
  message: '',
  priority: 'normal',
})

watch(() => props.open, (newVal) => {
  if (newVal) {
    if (props.defaultTab) activeTab.value = props.defaultTab
    if (user.value) {
      emailForm.value.from_email = user.value.email
      emailForm.value.from_name = user.value.name || ''
    }
    if (props.defaultSubject) {
      emailForm.value.subject = props.defaultSubject
      webForm.value.subject = props.defaultSubject
    }
    refetchMyTickets()
  }
})

async function handleSimulateEmail() {
  if (!emailForm.value.from_email || !emailForm.value.subject || !emailForm.value.body) {
    alert('Please fill in From Email, Subject, and Message Body.')
    return
  }
  try {
    const res = await simulateEmail({
      from_email: emailForm.value.from_email,
      from_name: emailForm.value.from_name || undefined,
      subject: emailForm.value.subject,
      body: emailForm.value.body,
      priority: emailForm.value.priority,
      source: 'email',
    })
    lastCreatedTicket.value = {
      number: res.ticket_number,
      message: res.message,
    }
    emit('ticket-created', res.ticket_number)
    emailForm.value.subject = ''
    emailForm.value.body = ''
    refetchMyTickets()
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Failed to send simulated email.')
  }
}

async function handleCreateWebTicket() {
  if (!webForm.value.subject || !webForm.value.message) {
    alert('Please fill in Subject and Message.')
    return
  }
  try {
    const res = await createTicket({
      subject: webForm.value.subject,
      message: webForm.value.message,
      priority: webForm.value.priority,
      source: 'web',
    })
    lastCreatedTicket.value = {
      number: res.ticket_number,
      message: `Web ticket #${res.ticket_number} created successfully!`,
    }
    emit('ticket-created', res.ticket_number)
    webForm.value.subject = ''
    webForm.value.message = ''
    refetchMyTickets()
  } catch (err: any) {
    alert(err?.response?.data?.detail || 'Failed to create support ticket.')
  }
}

function copyTicketNumber() {
  if (!lastCreatedTicket.value) return
  navigator.clipboard.writeText(lastCreatedTicket.value.number)
  copySuccess.value = true
  setTimeout(() => {
    copySuccess.value = false
  }, 2000)
}

function getStatusBadgeClass(status: string) {
  switch (status) {
    case 'open':
      return 'bg-amber-100 text-amber-800 border-amber-300'
    case 'in_progress':
      return 'bg-blue-100 text-blue-800 border-blue-300'
    case 'resolved':
      return 'bg-emerald-100 text-emerald-800 border-emerald-300'
    default:
      return 'bg-gray-100 text-gray-800 border-gray-300'
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="max-w-2xl max-h-[90vh] overflow-y-auto p-6 sm:p-8 rounded-2xl border-2 border-teal-500/20 shadow-2xl bg-white">
      <DialogHeader class="mb-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-teal-500/10 flex items-center justify-center text-teal-600 text-xl font-bold">
            📧
          </div>
          <div>
            <DialogTitle class="text-2xl font-black tracking-tight text-gray-900">
              RoadLancer Help & Support Desk
            </DialogTitle>
            <DialogDescription class="text-xs text-gray-500">
              Simulate inbound email parsing or track your existing support & profile edit requests.
            </DialogDescription>
          </div>
        </div>
      </DialogHeader>

      <!-- Success Alert Banner if ticket just created -->
      <div v-if="lastCreatedTicket" class="mb-6 p-4 rounded-xl bg-gradient-to-r from-teal-500/10 to-blue-500/10 border-2 border-teal-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 animate-in fade-in slide-in-from-top-2 duration-300">
        <div class="flex items-center gap-3">
          <span class="text-2xl">🎉</span>
          <div>
            <div class="font-extrabold text-sm text-teal-950 flex items-center gap-2">
              Ticket Generated: <Badge class="bg-teal-600 text-white font-mono text-xs px-2 py-0.5">{{ lastCreatedTicket.number }}</Badge>
            </div>
            <p class="text-xs text-gray-600 mt-0.5">{{ lastCreatedTicket.message }}</p>
          </div>
        </div>
        <Button
          size="sm"
          variant="outline"
          class="bg-white hover:bg-teal-50 border-teal-300 text-teal-800 font-bold text-xs shrink-0"
          @click="copyTicketNumber"
        >
          {{ copySuccess ? '✅ Copied!' : '📋 Copy Ticket #' }}
        </Button>
      </div>

      <Tabs v-model="activeTab" class="w-full">
        <TabsList class="grid w-full grid-cols-3 mb-6 bg-gray-100/80 p-1 rounded-xl">
          <TabsTrigger value="email" class="rounded-lg text-xs font-bold py-2 data-[state=active]:bg-white data-[state=active]:text-teal-900 shadow-sm">
            📧 Simulate Inbound Email
          </TabsTrigger>
          <TabsTrigger value="tickets" class="rounded-lg text-xs font-bold py-2 data-[state=active]:bg-white data-[state=active]:text-teal-900 shadow-sm">
            📋 My Tickets <span v-if="myTickets?.length" class="ml-1 px-1.5 py-0.2 bg-teal-100 text-teal-800 rounded-full text-[10px]">{{ myTickets.length }}</span>
          </TabsTrigger>
          <TabsTrigger value="web" class="rounded-lg text-xs font-bold py-2 data-[state=active]:bg-white data-[state=active]:text-teal-900 shadow-sm">
            🌐 Web Form
          </TabsTrigger>
        </TabsList>

        <!-- Tab 1: Simulate Inbound Email -->
        <TabsContent value="email" class="space-y-4">
          <div class="p-3.5 rounded-xl bg-blue-50/70 border border-blue-200 text-xs text-blue-900 space-y-1">
            <div class="font-bold flex items-center gap-1.5">
              <span>💡</span> How Inbound Email Webhook Parsing Works:
            </div>
            <p class="text-blue-800/90 leading-relaxed">
              In production, sending an email to <strong class="font-mono underline">support@roadlancer.com</strong> triggers a webhook from our mail provider. Here, you can simulate sending an email. If your <strong class="font-mono">From Email</strong> matches your RoadLancer account, the ticket is automatically linked to your user profile!
            </p>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="space-y-1.5">
              <Label class="text-xs font-bold text-gray-700">From Email Address *</Label>
              <Input
                v-model="emailForm.from_email"
                placeholder="e.g. driver@roadlancer.com"
                maxlength="255"
                class="bg-gray-50 border-gray-300 font-mono text-xs"
              />
            </div>
            <div class="space-y-1.5">
              <Label class="text-xs font-bold text-gray-700">Sender Name</Label>
              <Input
                v-model="emailForm.from_name"
                placeholder="e.g. Dave Driver"
                maxlength="100"
                class="bg-gray-50 border-gray-300 text-xs"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div class="sm:col-span-2 space-y-1.5">
              <Label class="text-xs font-bold text-gray-700">Email Subject *</Label>
              <Input
                v-model="emailForm.subject"
                placeholder="e.g. [PROFILE EDIT REQUEST] Update DL Number"
                maxlength="200"
                class="bg-gray-50 border-gray-300 text-xs font-medium"
              />
              <span class="text-[10px] text-muted-foreground font-mono">{{ emailForm.subject.length }}/200</span>
            </div>
            <div class="space-y-1.5">
              <Label class="text-xs font-bold text-gray-700">Priority</Label>
              <select
                v-model="emailForm.priority"
                class="w-full h-10 px-3 py-2 bg-gray-50 border border-gray-300 rounded-md text-xs font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                <option value="low">Low</option>
                <option value="normal">Normal</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
          </div>

          <div class="space-y-1.5">
            <Label class="text-xs font-bold text-gray-700">Email Body / Explanation *</Label>
            <textarea
              v-model="emailForm.body"
              rows="4"
              maxlength="5000"
              placeholder="Type your message as if writing an email to support@roadlancer.com..."
              class="flex w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-xs placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-teal-500 leading-relaxed"
            />
            <span class="text-[10px] text-muted-foreground font-mono">{{ emailForm.body.length }}/5000</span>
          </div>

          <div class="pt-2 flex justify-end">
            <Button
              @click="handleSimulateEmail"
              :disabled="isSimulatingEmail"
              class="bg-gradient-to-r from-teal-600 to-blue-600 hover:from-teal-700 hover:to-blue-700 text-white font-extrabold px-6 py-2.5 rounded-xl shadow-lg shadow-teal-500/20 text-xs"
            >
              <span v-if="isSimulatingEmail" class="flex items-center gap-2">
                <span class="animate-spin">⏳</span> Relaying via Mail Server...
              </span>
              <span v-else class="flex items-center gap-2">
                🚀 Send Email to support@roadlancer.com
              </span>
            </Button>
          </div>
        </TabsContent>

        <!-- Tab 2: My Tickets -->
        <TabsContent value="tickets" class="space-y-4">
          <div v-if="!user" class="text-center py-8 text-gray-500 text-xs">
            Please log in to view your personal support ticket history.
          </div>
          <div v-else-if="isLoadingTickets" class="text-center py-8 text-gray-500 text-xs">
            Loading your tickets...
          </div>
          <div v-else class="space-y-3">
            <!-- Filter & Sort Bar for My Tickets -->
            <div class="flex flex-col sm:flex-row items-center justify-between gap-2 bg-gray-50 p-3 rounded-xl border border-gray-200">
              <div class="w-full sm:flex-1">
                <Input
                  v-model="searchQuery"
                  placeholder="Search subject, #, or message..."
                  class="h-8 text-xs bg-white border-gray-300 rounded-lg"
                />
              </div>
              <div class="flex items-center gap-2 w-full sm:w-auto">
                <select
                  v-model="statusFilter"
                  class="h-8 px-2.5 bg-white border border-gray-300 rounded-lg text-xs font-bold text-gray-700 focus:outline-none focus:ring-1 focus:ring-teal-500"
                >
                  <option value="all">All Statuses</option>
                  <option value="open">Open / Pending</option>
                  <option value="in_progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                  <option value="closed">Closed</option>
                </select>
                <select
                  v-model="sortBy"
                  class="h-8 px-2.5 bg-white border border-gray-300 rounded-lg text-xs font-bold text-teal-800 focus:outline-none focus:ring-1 focus:ring-teal-500"
                >
                  <option value="newest">Newest First</option>
                  <option value="oldest">Oldest First</option>
                  <option value="priority">Priority</option>
                  <option value="status">Status</option>
                </select>
              </div>
            </div>

            <div v-if="sortedMyTickets && sortedMyTickets.length > 0" class="flex items-center justify-between px-1 text-[11px] text-gray-500 font-medium">
              <span>Showing <span class="font-bold text-gray-900">{{ sortedMyTickets.length }}</span> ticket{{ sortedMyTickets.length === 1 ? '' : 's' }}</span>
              <span class="font-mono text-teal-700 font-bold bg-teal-50 px-2 py-0.5 rounded-md border border-teal-200">Sorted by: {{ sortBy === 'newest' ? 'Newest First' : sortBy === 'oldest' ? 'Oldest First' : sortBy === 'priority' ? 'Priority' : 'Status' }}</span>
            </div>

            <div v-if="!sortedMyTickets || sortedMyTickets.length === 0" class="text-center py-8 bg-gray-50 rounded-xl border border-dashed border-gray-300">
              <p class="text-xs font-bold text-gray-600">No support tickets found.</p>
              <p class="text-[11px] text-gray-400 mt-1">Try adjusting your filters or submit a new ticket!</p>
            </div>
            <div v-else class="space-y-3 max-h-[350px] overflow-y-auto pr-1">
              <div
                v-for="t in sortedMyTickets"
                :key="t.id"
                class="p-4 rounded-xl border border-gray-200 bg-gray-50/50 hover:bg-white hover:shadow-md transition-all duration-200 space-y-2"
              >
              <div class="flex items-center justify-between gap-2 flex-wrap">
                <div class="flex items-center gap-2">
                  <Badge class="bg-gray-900 text-white font-mono text-xs font-bold px-2 py-0.5">
                    {{ t.ticket_number }}
                  </Badge>
                  <Badge :class="['text-[10px] font-extrabold uppercase px-2 py-0.5 border', getStatusBadgeClass(t.status)]">
                    {{ t.status }}
                  </Badge>
                  <Badge v-if="t.source === 'email'" class="bg-blue-100 text-blue-800 text-[10px] border border-blue-200">
                    📧 Email
                  </Badge>
                  <Badge v-else class="bg-purple-100 text-purple-800 text-[10px] border border-purple-200">
                    🌐 Web
                  </Badge>
                </div>
                <span class="text-[10px] font-mono text-gray-400">
                  {{ new Date(t.created_at).toLocaleDateString() }} {{ new Date(t.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}
                </span>
              </div>

              <div class="font-bold text-xs text-gray-900">
                {{ t.subject }}
              </div>
              <div class="text-xs text-gray-600 bg-white p-2.5 rounded-lg border border-gray-150 leading-relaxed font-sans">
                {{ t.message }}
              </div>

              <div v-if="t.admin_notes" class="mt-2 p-2.5 rounded-lg bg-teal-50 border border-teal-200 text-xs">
                <div class="font-bold text-teal-900 text-[11px] flex items-center gap-1 mb-1">
                  <span>🛡️</span> Admin Reply / Note:
                </div>
                <p class="text-teal-800 leading-relaxed">{{ t.admin_notes }}</p>
              </div>
            </div>
          </div>
        </div>
        </TabsContent>

        <!-- Tab 3: Direct Web Ticket -->
        <TabsContent value="web" class="space-y-4">
          <div v-if="!user" class="text-center py-8 text-gray-500 text-xs">
            Please log in to submit a direct web ticket.
          </div>
          <div v-else class="space-y-4">
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div class="sm:col-span-2 space-y-1.5">
                <Label class="text-xs font-bold text-gray-700">Subject *</Label>
                <Input
                  v-model="webForm.subject"
                  placeholder="e.g. Question regarding AI pricing estimate"
                  maxlength="200"
                  class="bg-gray-50 border-gray-300 text-xs font-medium"
                />
                <span class="text-[10px] text-muted-foreground font-mono">{{ webForm.subject.length }}/200</span>
              </div>
              <div class="space-y-1.5">
                <Label class="text-xs font-bold text-gray-700">Priority</Label>
                <select
                  v-model="webForm.priority"
                  class="w-full h-10 px-3 py-2 bg-gray-50 border border-gray-300 rounded-md text-xs font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="low">Low</option>
                  <option value="normal">Normal</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
            </div>

            <div class="space-y-1.5">
              <Label class="text-xs font-bold text-gray-700">Message / Inquiry *</Label>
              <textarea
                v-model="webForm.message"
                rows="4"
                maxlength="5000"
                placeholder="Describe your issue or question in detail..."
                class="flex w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-xs placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-teal-500 leading-relaxed"
              />
              <span class="text-[10px] text-muted-foreground font-mono">{{ webForm.message.length }}/5000</span>
            </div>

            <div class="pt-2 flex justify-end">
              <Button
                @click="handleCreateWebTicket"
                :disabled="isCreatingTicket"
                class="bg-gray-900 hover:bg-black text-white font-extrabold px-6 py-2.5 rounded-xl shadow-md text-xs"
              >
                <span v-if="isCreatingTicket" class="flex items-center gap-2">
                  <span class="animate-spin">⏳</span> Submitting...
                </span>
                <span v-else>
                  Submit Web Ticket
                </span>
              </Button>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </DialogContent>
  </Dialog>
</template>
