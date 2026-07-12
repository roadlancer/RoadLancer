<script lang="ts" setup>
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { MessageCircle, MessageSquare, Clock, ShieldCheck, UserCircle } from '@lucide/vue'

export interface ReplyItem {
  id: string
  message: string
  sender_name: string
  sender_type?: 'agent' | 'user' | string
  sender_role?: string
  created_at: string
}

export interface ReplyThreadProps {
  replies?: ReplyItem[]
}

withDefaults(defineProps<ReplyThreadProps>(), {
  replies: () => [],
})
</script>

<template>
  <Card class="border-border/80 shadow-xs rounded-2xl overflow-hidden bg-card" data-testid="reply-thread-card">
    <CardHeader class="pb-3 border-b border-border/50 bg-muted/20 flex flex-row items-center justify-between">
      <div>
        <CardTitle class="text-base font-bold text-foreground flex items-center gap-2">
          <MessageCircle class="size-4 text-primary" />
          Discussion & Reply Thread
        </CardTitle>
        <CardDescription class="text-xs text-muted-foreground mt-0.5">
          Full chronological communication history for this support ticket.
        </CardDescription>
      </div>
      <Badge variant="secondary" class="text-xs font-mono font-bold px-2.5 py-1" data-testid="reply-count-badge">
        {{ replies?.length || 0 }} {{ (replies?.length === 1) ? 'Reply' : 'Replies' }}
      </Badge>
    </CardHeader>

    <CardContent class="p-5 sm:p-6 space-y-4">
      <!-- No Replies Empty State -->
      <div
        v-if="!replies || replies.length === 0"
        class="py-8 px-4 text-center bg-muted/30 border border-dashed border-border/70 rounded-xl space-y-2"
        data-testid="no-replies-empty-state"
      >
        <MessageSquare class="size-8 text-muted-foreground/60 mx-auto" />
        <h4 class="text-sm font-semibold text-foreground">No Replies Yet</h4>
        <p class="text-xs text-muted-foreground max-w-sm mx-auto">
          No communication messages have been sent on this ticket yet. Use the reply box below to start the conversation with the user.
        </p>
      </div>

      <!-- Replies List -->
      <div v-else class="space-y-4" data-testid="replies-list">
        <div
          v-for="reply in replies"
          :key="reply.id"
          class="p-4 sm:p-5 rounded-2xl border transition-all"
          :class="(reply.sender_type === 'agent' || reply.sender_role === 'admin')
            ? 'bg-primary/5 border-primary/25 ml-0 sm:ml-6 shadow-2xs'
            : 'bg-card border-border/80 mr-0 sm:mr-6 shadow-2xs'"
          :data-testid="`reply-item-${reply.id}`"
        >
          <div class="flex items-center justify-between gap-2 pb-3 mb-3 border-b border-border/50">
            <div class="flex items-center gap-2.5 min-w-0">
              <div
                class="size-8 rounded-full flex items-center justify-center shrink-0 font-bold text-xs"
                :class="(reply.sender_type === 'agent' || reply.sender_role === 'admin')
                  ? 'bg-primary text-primary-foreground shadow-xs'
                  : 'bg-muted text-foreground border border-border'"
              >
                <ShieldCheck v-if="reply.sender_type === 'agent' || reply.sender_role === 'admin'" class="size-4" />
                <UserCircle v-else class="size-4 text-muted-foreground" />
              </div>
              <div class="min-w-0">
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="font-bold text-sm text-foreground truncate" :data-testid="`reply-sender-${reply.id}`">
                    {{ reply.sender_name }}
                  </span>
                  <Badge
                    size="sm"
                    class="text-[10px] uppercase font-bold px-1.5 py-0"
                    :variant="(reply.sender_type === 'agent' || reply.sender_role === 'admin') ? 'default' : 'outline'"
                    :data-testid="`reply-badge-${reply.id}`"
                  >
                    {{ (reply.sender_type === 'agent' || reply.sender_role === 'admin') ? 'Agent' : 'Customer' }}
                  </Badge>
                </div>
                <span class="text-[11px] text-muted-foreground flex items-center gap-1 font-mono">
                  <Clock class="size-3 inline" />
                  {{ new Date(reply.created_at).toLocaleString() }}
                </span>
              </div>
            </div>
          </div>

          <div
            v-if="reply.sender_type === 'agent' || reply.sender_role === 'admin'"
            class="text-sm text-foreground/90 leading-relaxed font-sans [&_p]:mb-2 [&_p:last-child]:mb-0 [&_ul]:my-2 [&_ul]:pl-5 [&_ul]:list-disc [&_li]:mb-1 [&_strong]:font-bold"
            :data-testid="`reply-message-${reply.id}`"
            v-html="reply.message"
          />
          <div
            v-else
            class="text-sm text-foreground/90 leading-relaxed whitespace-pre-line font-sans"
            :data-testid="`reply-message-${reply.id}`"
          >
            {{ reply.message }}
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
</template>
