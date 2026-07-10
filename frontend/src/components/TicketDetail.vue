<script lang="ts" setup>
import { useRouter } from 'vue-router'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Clock, User, Mail, Phone, ExternalLink } from '@lucide/vue'
import type { SupportTicket } from '@/composables/useSupportTickets'

export interface TicketDetailProps {
  ticket: SupportTicket
  showSenderCard?: boolean
  showInspectButton?: boolean
}

const props = withDefaults(defineProps<TicketDetailProps>(), {
  showSenderCard: true,
  showInspectButton: true,
})

const emit = defineEmits<{
  (e: 'inspect-account', userId: string): void
}>()

const router = useRouter()

function handleInspect() {
  if (props.ticket?.user?.id) {
    emit('inspect-account', props.ticket.user.id)
  }
  router.push('/admin')
}
</script>

<template>
  <div class="space-y-6">
    <!-- Subject Card -->
    <Card class="border-border/80 shadow-xs overflow-hidden rounded-2xl" data-testid="ticket-detail-subject-card">
      <CardHeader class="bg-muted/30 pb-4 border-b border-border/50">
        <div class="flex items-center justify-between text-xs text-muted-foreground mb-1.5 font-medium">
          <span class="flex items-center gap-1.5" data-testid="ticket-created-date">
            <Clock class="size-3.5" /> Created on {{ ticket.created_at ? new Date(ticket.created_at).toLocaleString() : 'N/A' }}
          </span>
          <span class="flex items-center gap-1.5 font-mono">
            Source:
            <Badge variant="outline" class="text-[11px] font-semibold uppercase px-2 py-0" data-testid="ticket-source-badge">
              {{ ticket.source || 'email' }}
            </Badge>
          </span>
        </div>
        <CardTitle class="text-xl sm:text-2xl font-bold text-foreground tracking-tight" data-testid="ticket-subject-title">
          {{ ticket.subject }}
        </CardTitle>
      </CardHeader>
      <CardContent class="p-6">
        <div class="prose prose-sm dark:prose-invert max-w-none text-foreground/90 font-sans leading-relaxed whitespace-pre-line text-sm sm:text-base" data-testid="ticket-message-content">
          {{ ticket.message }}
        </div>
      </CardContent>
    </Card>

    <!-- Sender & Linked User Account Card -->
    <Card v-if="showSenderCard" class="border-border/80 shadow-xs rounded-2xl overflow-hidden" data-testid="ticket-detail-sender-card">
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
            <p class="font-mono font-medium text-foreground text-sm truncate flex items-center gap-2" data-testid="ticket-sender-email">
              <Mail class="size-3.5 text-muted-foreground shrink-0" />
              <a :href="`mailto:${ticket.sender_email}`" class="hover:text-primary">
                {{ ticket.sender_email }}
              </a>
            </p>
          </div>

          <div class="p-3.5 rounded-xl bg-card border border-border/60 space-y-1">
            <span class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Sender Name</span>
            <p class="font-semibold text-foreground text-sm truncate" data-testid="ticket-sender-name">
              {{ ticket.sender_name || 'Not Provided' }}
            </p>
          </div>
        </div>

        <!-- Linked Profile Box -->
        <div v-if="ticket.user" class="mt-4 p-4 rounded-xl bg-primary/5 border border-primary/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3" data-testid="ticket-linked-user-box">
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <Badge variant="secondary" class="text-[10px] uppercase font-bold px-2 py-0.5 bg-primary/10 text-primary" data-testid="ticket-linked-role-badge">
                Linked {{ ticket.user.role }} Profile
              </Badge>
              <span class="font-bold text-foreground text-sm" data-testid="ticket-linked-user-name">{{ ticket.user.name }}</span>
            </div>
            <div class="flex items-center gap-3 text-xs text-muted-foreground font-mono">
              <span data-testid="ticket-linked-user-email">{{ ticket.user.email }}</span>
              <span v-if="ticket.user.phone" class="flex items-center gap-1" data-testid="ticket-linked-user-phone">
                • <Phone class="size-3" /> {{ ticket.user.phone }}
              </span>
            </div>
          </div>
          <Button
            v-if="showInspectButton"
            variant="outline"
            size="sm"
            class="h-8 text-xs font-bold shadow-2xs gap-1.5 shrink-0"
            @click="handleInspect"
            data-testid="ticket-inspect-button"
          >
            Inspect Account <ExternalLink class="size-3.5" />
          </Button>
        </div>
        <div v-else class="mt-4 p-3.5 rounded-xl bg-muted/40 border border-border/60 text-xs text-muted-foreground italic text-center" data-testid="ticket-no-linked-user">
          No registered RoadLancer account matched directly with sender email address (`{{ ticket.sender_email }}`).
        </div>
      </CardContent>
    </Card>
  </div>
</template>
