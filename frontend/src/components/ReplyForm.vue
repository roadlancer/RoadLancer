<script lang="ts" setup>
import { ref, watch } from 'vue'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Reply, CheckCircle, CornerDownRight } from '@lucide/vue'
import { sanitize, sanitizeText } from '@/lib/sanitize'

export interface ReplyFormProps {
  senderEmail?: string
  defaultSenderName?: string
  isSubmitting?: boolean
  showStatusNotice?: boolean
}

const props = withDefaults(defineProps<ReplyFormProps>(), {
  senderEmail: 'user@example.com',
  defaultSenderName: '',
  isSubmitting: false,
  showStatusNotice: true,
})

const emit = defineEmits<{
  (e: 'submit', payload: { message: string; senderName: string }): void
}>()

const senderName = ref('')
const message = ref('')

watch(
  () => props.defaultSenderName,
  (newVal) => {
    if (!senderName.value || senderName.value === 'Sarah Jenkins (Support Lead)') {
      senderName.value = newVal || 'Sarah Jenkins (Support Lead)'
    }
  },
  { immediate: true }
)

function handleSubmit() {
  if (!message.value.trim() || props.isSubmitting) return
  const finalSenderName = senderName.value.trim() || props.defaultSenderName || 'Sarah Jenkins (Support Lead)'
  emit('submit', {
    message: sanitize(message.value.trim()),
    senderName: sanitizeText(finalSenderName),
  })
  message.value = ''
}
</script>

<template>
  <Card class="border-border/80 shadow-sm rounded-2xl overflow-hidden bg-card border-t-2 border-t-primary">
    <CardHeader class="pb-3 border-b border-border/50 bg-primary/5">
      <CardTitle class="text-base font-bold text-foreground flex items-center gap-2">
        <Reply class="size-4 text-primary" />
        Post a Reply to Sender
      </CardTitle>
      <CardDescription class="text-xs text-muted-foreground">
        Your response will be recorded in the thread and sent directly to {{ senderEmail }}.
      </CardDescription>
    </CardHeader>

    <form @submit.prevent="handleSubmit">
      <CardContent class="p-5 space-y-4">
        <!-- Optional Agent Name Override -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="space-y-1.5">
            <label class="text-xs font-bold text-foreground uppercase tracking-wider block">
              Replying As (Display Name)
            </label>
            <input
              type="text"
              v-model="senderName"
              :placeholder="defaultSenderName || 'Sarah Jenkins (Support Lead)'"
              maxlength="100"
              class="w-full h-10 px-3 bg-background border border-input rounded-xl text-sm font-medium text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/40 transition-shadow"
              data-testid="reply-sender-name-input"
            />
          </div>
          <div v-if="showStatusNotice" class="space-y-1.5 flex flex-col justify-end">
            <div class="p-2.5 rounded-xl bg-muted/40 border border-border/60 text-xs text-muted-foreground flex items-center gap-2 h-10">
              <CheckCircle class="size-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
              <span>Auto-updates ticket status from Open to In Progress.</span>
            </div>
          </div>
        </div>

        <!-- Reply Message Textarea -->
        <div class="space-y-1.5">
          <label class="text-xs font-bold text-foreground uppercase tracking-wider block">
            Reply Message <span class="text-destructive">*</span>
          </label>
          <textarea
            v-model="message"
            rows="4"
            required
            maxlength="5000"
            placeholder="Type your detailed resolution response or instructions here..."
            class="w-full p-3.5 bg-background border border-input rounded-xl text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/40 transition-shadow resize-y font-sans"
            data-testid="reply-message-textarea"
          ></textarea>
          <span class="text-[10px] text-muted-foreground font-mono">{{ message.length }}/5000</span>
        </div>
      </CardContent>

      <CardFooter class="px-5 py-3.5 bg-muted/20 border-t border-border/50 flex items-center justify-between">
        <span class="text-xs text-muted-foreground hidden sm:inline">
          Press <kbd class="px-1.5 py-0.5 rounded bg-muted border border-border font-mono text-[10px]">Submit Reply</kbd> when ready.
        </span>
        <Button
          type="submit"
          :disabled="!message.trim() || isSubmitting"
          class="font-bold shadow-sm px-6 h-10 gap-2 ml-auto"
          data-testid="reply-submit-button"
        >
          <CornerDownRight v-if="!isSubmitting" class="size-4" />
          <span v-if="isSubmitting">Sending Reply...</span>
          <span v-else>Send Reply</span>
        </Button>
      </CardFooter>
    </form>
  </Card>
</template>
