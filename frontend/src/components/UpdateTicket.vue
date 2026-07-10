<script lang="ts" setup>
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { MessageSquare, Save } from '@lucide/vue'

export interface SupportAgent {
  id: string
  name: string
}

export interface UpdateTicketProps {
  status?: 'open' | 'in_progress' | 'resolved' | 'closed'
  priority?: 'low' | 'normal' | 'high' | 'urgent'
  category?: string
  agentId?: string
  agentName?: string
  notes?: string
  isSaving?: boolean
  supportAgents?: SupportAgent[]
}

const props = withDefaults(defineProps<UpdateTicketProps>(), {
  status: 'open',
  priority: 'normal',
  category: 'general',
  agentId: '',
  agentName: '',
  notes: '',
  isSaving: false,
  supportAgents: () => [],
})

const emit = defineEmits<{
  (e: 'update:status', value: 'open' | 'in_progress' | 'resolved' | 'closed'): void
  (e: 'update:priority', value: 'low' | 'normal' | 'high' | 'urgent'): void
  (e: 'update:category', value: string): void
  (e: 'update:notes', value: string): void
  (e: 'agent-selected', payload: { id: string; name: string }): void
  (e: 'assign-to-me'): void
  (e: 'save'): void
}>()

function onAgentChange(e: Event) {
  const target = e.target as HTMLSelectElement
  const selId = target.value
  const found = props.supportAgents.find((a) => a.id === selId)
  emit('agent-selected', {
    id: selId,
    name: found && selId ? found.name : '',
  })
}
</script>

<template>
  <Card class="border-border/80 shadow-sm rounded-2xl overflow-hidden bg-card" data-testid="update-ticket-card">
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
      <!-- Assigned Agent Select -->
      <div class="space-y-2">
        <div class="flex items-center justify-between">
          <label class="text-xs font-bold text-foreground uppercase tracking-wider block">
            Assigned Support Agent
          </label>
          <span v-if="agentName" class="text-[10px] font-mono text-indigo-600 dark:text-indigo-400 font-bold truncate max-w-[140px]" data-testid="assigned-agent-notice">
            ✓ Assigned to {{ agentName.split(' (')[0] }}
          </span>
        </div>
        <div class="flex items-center gap-2">
          <select
            :value="agentId"
            @change="onAgentChange"
            class="w-full h-10 px-3 bg-background border border-input rounded-xl text-sm font-semibold text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 transition-shadow"
            data-testid="agent-select"
          >
            <option v-for="agent in supportAgents" :key="agent.id" :value="agent.id">
              {{ agent.name }}
            </option>
          </select>
          <Button
            type="button"
            variant="outline"
            size="sm"
            class="h-10 px-3.5 text-xs font-semibold shrink-0 bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 shadow-2xs"
            @click="emit('assign-to-me')"
            title="Quick assign to current logged in admin"
            data-testid="assign-to-me-btn"
          >
            Assign to Me
          </Button>
        </div>
      </div>

      <!-- Status Select -->
      <div class="space-y-2">
        <label class="text-xs font-bold text-foreground uppercase tracking-wider block">
          Workflow Status
        </label>
        <select
          :value="status"
          @change="emit('update:status', ($event.target as HTMLSelectElement).value as any)"
          class="w-full h-10 px-3 bg-background border border-input rounded-xl text-sm font-semibold text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 transition-shadow"
          data-testid="status-select"
        >
          <option value="open">Open (Needs Attention)</option>
          <option value="in_progress">In Progress (Investigating)</option>
          <option value="resolved">Resolved (Complete)</option>
          <option value="closed">Closed (Archived)</option>
        </select>
      </div>

      <!-- Category Select -->
      <div class="space-y-2">
        <label class="text-xs font-bold text-foreground uppercase tracking-wider block">
          Ticket Category
        </label>
        <select
          :value="category"
          @change="emit('update:category', ($event.target as HTMLSelectElement).value)"
          class="w-full h-10 px-3 bg-background border border-input rounded-xl text-sm font-semibold text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 transition-shadow"
          data-testid="category-select"
        >
          <option value="general">General Inquiry</option>
          <option value="verification">KYC & Verification</option>
          <option value="billing">Billing & Payments</option>
          <option value="shipments">Shipment & Delivery</option>
          <option value="technical">Technical & App Issue</option>
          <option value="account">Profile & Account</option>
        </select>
      </div>

      <!-- Priority Select -->
      <div class="space-y-2">
        <label class="text-xs font-bold text-foreground uppercase tracking-wider block">
          Priority Ranking
        </label>
        <select
          :value="priority"
          @change="emit('update:priority', ($event.target as HTMLSelectElement).value as any)"
          class="w-full h-10 px-3 bg-background border border-input rounded-xl text-sm font-semibold text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 transition-shadow"
          data-testid="priority-select"
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
          :value="notes"
          @input="emit('update:notes', ($event.target as HTMLTextAreaElement).value)"
          rows="6"
          placeholder="Document resolution actions, root cause analysis, or follow-up notes..."
          class="w-full p-3.5 bg-background border border-input rounded-xl text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/40 transition-shadow resize-y font-sans leading-relaxed"
          data-testid="notes-textarea"
        ></textarea>
      </div>
    </CardContent>

    <CardFooter class="p-5 bg-muted/20 border-t border-border/50 flex flex-col gap-2.5">
      <Button
        @click="emit('save')"
        :disabled="isSaving"
        class="w-full h-10 font-bold shadow-sm"
        data-testid="save-resolution-btn"
      >
        <Save v-if="!isSaving" class="size-4 mr-1.5" />
        {{ isSaving ? 'Saving Resolution...' : 'Save Ticket Resolution' }}
      </Button>
    </CardFooter>
  </Card>
</template>
