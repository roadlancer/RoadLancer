<script lang="ts" setup>
import { ref, watch } from 'vue'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Reply, CheckCircle, CornerDownRight, Sparkles } from '@lucide/vue'
import { sanitize, sanitizeText } from '@/lib/sanitize'
import api from '@/lib/api'

export interface ReplyFormProps {
  senderEmail?: string
  customerName?: string
  defaultSenderName?: string
  isSubmitting?: boolean
  showStatusNotice?: boolean
}

const props = withDefaults(defineProps<ReplyFormProps>(), {
  senderEmail: 'user@example.com',
  customerName: '',
  defaultSenderName: '',
  isSubmitting: false,
  showStatusNotice: true,
})

const emit = defineEmits<{
  (e: 'submit', payload: { message: string; senderName: string }): void
}>()

const senderName = ref('')
const message = ref('')
const isPolishing = ref(false)
const aiStatus = ref<{
  type: 'error'
  message: string
  details?: string
} | null>(null)

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

async function handlePolish() {
  if (!message.value.trim() || isPolishing.value || props.isSubmitting) return
  isPolishing.value = true
  aiStatus.value = null
  const finalSenderName = senderName.value.trim() || props.defaultSenderName || 'Sarah Jenkins (Support Lead)'
  let customerFirstName = 'there'
  if (props.customerName && props.customerName.trim()) {
    const first = props.customerName.trim().split(/\s+/)[0]
    customerFirstName = first.charAt(0).toUpperCase() + first.slice(1)
  } else if (props.senderEmail && props.senderEmail.includes('@')) {
    const prefix = props.senderEmail.split('@')[0].replace(/[._+-].*/, '')
    if (prefix && prefix.length > 1) {
      customerFirstName = prefix.charAt(0).toUpperCase() + prefix.slice(1)
    }
  }

  try {
    const res = await api.post('/auth/ai/polish', {
      draft: message.value.trim(),
      senderName: finalSenderName,
      customerName: customerFirstName,
      senderEmail: props.senderEmail
    }, { timeout: 30000 })

    if (res.data?.polished) {
      message.value = res.data.polished.trim()
      aiStatus.value = null
      return
    }

    aiStatus.value = {
      type: 'error',
      message: 'AI Polish Failed',
      details: 'The server did not return a polished response. Please try again.'
    }
  } catch (serverErr: any) {
    if (serverErr?.response?.data?.code === 'API_KEY_INVALID' || serverErr?.response?.status === 401) {
      aiStatus.value = {
        type: 'error',
        message: 'Gemini API Key Incorrect / Unauthorized',
        details: 'Your Gemini API key on the backend server is invalid or unauthorized. Please check your .env.'
      }
      return
    }
    if (serverErr?.response?.data?.code === 'TOKEN_QUOTA_EXHAUSTED' || serverErr?.response?.status === 429) {
      aiStatus.value = {
        type: 'error',
        message: 'Model Token Quota Exceeded',
        details: 'You have reached your Gemini API token limit or rate quota for this key.'
      }
      return
    }
    aiStatus.value = {
      type: 'error',
      message: 'AI Polish Unavailable',
      details: serverErr?.message || 'Could not reach the AI polish server. Please try again later.'
    }
  } finally {
    isPolishing.value = false
  }
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

      <div
        v-if="aiStatus"
        class="mx-5 mb-3 p-3 rounded-xl border text-xs flex items-start gap-2.5 transition-all bg-destructive/10 border-destructive/30 text-destructive"
        data-testid="ai-validation-banner"
      >
        <span class="text-sm font-bold shrink-0">⚠️</span>
        <div class="flex-1 min-w-0">
          <div class="font-bold">{{ aiStatus.message }}</div>
          <p v-if="aiStatus.details" class="mt-0.5 opacity-90 leading-relaxed break-words">{{ aiStatus.details }}</p>
        </div>
      </div>

      <CardFooter class="px-5 py-3.5 bg-muted/20 border-t border-border/50 flex items-center justify-between">
        <span class="text-xs text-muted-foreground hidden sm:inline">
          Press <kbd class="px-1.5 py-0.5 rounded bg-muted border border-border font-mono text-[10px]">Submit Reply</kbd> when ready.
        </span>
        <div class="flex items-center gap-2 ml-auto">
          <Button
            type="button"
            variant="outline"
            :disabled="!message.trim() || isPolishing || isSubmitting"
            @click="handlePolish"
            class="font-bold shadow-sm px-4 h-10 gap-2 border-border hover:bg-purple-500/10 hover:text-purple-600 dark:hover:text-purple-400 transition-colors"
            data-testid="reply-polish-button"
          >
            <Sparkles class="size-4 text-purple-500 shrink-0" />
            <span v-if="isPolishing">Polishing...</span>
            <span v-else>Polish</span>
          </Button>
          <Button
            type="submit"
            :disabled="!message.trim() || isSubmitting || isPolishing"
            class="font-bold shadow-sm px-6 h-10 gap-2"
            data-testid="reply-submit-button"
          >
            <CornerDownRight v-if="!isSubmitting" class="size-4" />
            <span v-if="isSubmitting">Sending Reply...</span>
            <span v-else>Send Reply</span>
          </Button>
        </div>
      </CardFooter>
    </form>
  </Card>
</template>
