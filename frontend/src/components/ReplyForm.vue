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
    try {
      const res = await api.post('/auth/ai/polish', {
        draft: message.value.trim(),
        senderName: finalSenderName,
        customerName: customerFirstName,
        senderEmail: props.senderEmail
      }, { timeout: 1200 })
      if (res.data?.polished) {
        message.value = res.data.polished.trim()
        aiStatus.value = null
        return
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
      // Otherwise server is offline or slow, fall through to client-side Vercel AI SDK
    }

    const { generateText } = await import('ai')
    const { createGoogleGenerativeAI } = await import('@ai-sdk/google')
    const apiKey = (import.meta as any).env?.VITE_GEMINI_API_KEY || (import.meta as any).env?.VITE_GOOGLE_API_KEY || (typeof process !== 'undefined' && (process.env?.GEMINI_API_KEY || process.env?.GOOGLE_GENERATIVE_AI_API_KEY)) || ''
    
    if (!apiKey) {
      aiStatus.value = {
        type: 'error',
        message: 'Missing Gemini API Key',
        details: 'No API key found in client environment (VITE_GEMINI_API_KEY). Please add it and restart Vite.'
      }
      return
    }

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

    const googleProvider = createGoogleGenerativeAI({ apiKey })
    const systemPrompt = `You are an AI writing assistant that polishes and improves customer support draft replies written by human agents.
Your ONLY task is to take the user's exact draft text and polish its grammar, tone, clarity, and professionalism so it sounds polite, empathetic, and well-structured.
CRITICAL RULES:
1. STRICTLY PRESERVE the exact meaning, facts, figures, dates, names, and decisions stated in the original draft.
2. DO NOT invent new facts, promises, or explanations that are not present in the original draft.
3. DO NOT write a completely different or generic customer service response. You must improve and rewrite the exact draft provided.
4. Output ONLY the final polished reply text directly, without any introductory words, notes, quotes, or markdown formatting around it.
5. SIGNATURE REQUIREMENT: Always conclude the polished reply with a clean, professional signature block in the exact following format at the bottom:

Best regards,
${finalSenderName}
RoadLancer Support Team
https://roadlancer.com

(If the original draft already contained an informal sign-off or name, replace it with this standardized signature block.)
6. GREETING REQUIREMENT: Always begin the polished reply by addressing the customer respectfully by their first name "${customerFirstName}" at the very top (for example: "Hi ${customerFirstName}," or "Dear ${customerFirstName},"). If the original draft already had a greeting with a different name or no name at all, update or prepend it so it starts cleanly by addressing "${customerFirstName}".`
    const promptText = `Please polish and improve the following support agent draft reply while preserving its exact facts and meaning:\n\n---\n${message.value.trim()}\n---`

    let text = ''
    try {
      const res = await generateText({
        model: googleProvider('gemini-3.1-flash-lite'),
        maxTokens: 350,
        temperature: 0.3,
        maxRetries: 0,
        system: systemPrompt,
        prompt: promptText,
      })
      text = res.text
    } catch (firstErr: any) {
      const firstMsg = (firstErr?.message || '').toLowerCase()
      if (firstMsg.includes('quota') || firstMsg.includes('rate') || firstMsg.includes('429') || firstErr?.status === 429 || firstMsg.includes('not found') || firstMsg.includes('404') || firstErr?.status === 404 || firstMsg.includes('is not supported') || firstMsg.includes('invalid model')) {
        const fallbackRes = await generateText({
          model: googleProvider('gemini-1.5-flash'),
          maxTokens: 350,
          temperature: 0.3,
          maxRetries: 0,
          system: systemPrompt,
          prompt: promptText,
        })
        text = fallbackRes.text
      } else {
        throw firstErr
      }
    }

    if (text) {
      let finalPolished = text.trim()
      if (customerFirstName && customerFirstName !== 'there') {
        const topSlice = finalPolished.slice(0, 80).toLowerCase()
        if (!topSlice.includes(customerFirstName.toLowerCase())) {
          finalPolished = `Hi ${customerFirstName},\n\n${finalPolished}`
        }
      }
      if (!finalPolished.includes('https://roadlancer.com')) {
        finalPolished += `\n\nBest regards,\n${finalSenderName}\nRoadLancer Support Team\nhttps://roadlancer.com`
      }
      message.value = finalPolished
      aiStatus.value = null
    }
  } catch (err: any) {
    console.error('Failed to polish draft:', err)
    const errMsg = err?.message || ''
    const errMsgUpper = errMsg.toUpperCase()
    if (errMsgUpper.includes('API_KEY_INVALID') || errMsgUpper.includes('KEY NOT VALID') || errMsgUpper.includes('401') || errMsgUpper.includes('UNAUTHORIZED') || err?.status === 401) {
      aiStatus.value = {
        type: 'error',
        message: 'Gemini API Key Incorrect / Unauthorized',
        details: 'The provided API key is rejected by Google Gemini. Please check your key.'
      }
    } else if (errMsgUpper.includes('QUOTA') || errMsgUpper.includes('RATE') || errMsgUpper.includes('RESOURCE_EXHAUSTED') || errMsgUpper.includes('429') || err?.status === 429) {
      aiStatus.value = {
        type: 'error',
        message: 'Model Rate Limit / Quota Exceeded',
        details: 'You have exceeded the free tier rate limit on Gemini 2.5 Flash (5 requests/minute). Please wait ~50 seconds before clicking Polish again.'
      }
    } else {
      aiStatus.value = {
        type: 'error',
        message: 'Polishing Failed',
        details: errMsg || 'Please check your network or ensure dependencies are installed via bun install.'
      }
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
