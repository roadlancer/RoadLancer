<script lang="ts" setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Clock, User, Mail, Phone, ExternalLink, Sparkles, AlertTriangle, MessageSquare } from '@lucide/vue'
import type { SupportTicket } from '@/composables/useSupportTickets'
import api from '@/lib/api'
import { generateText } from 'ai'
import { createGoogleGenerativeAI } from '@ai-sdk/google'

const apiKey = import.meta.env.VITE_GEMINI_API_KEY || import.meta.env.VITE_GOOGLE_GENERATIVE_AI_API_KEY || ''

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

const isSummarizing = ref(false)
const summaryText = ref<string | null>(null)
const aiError = ref<{ title: string; message: string } | null>(null)

function handleInspect() {
  if (props.ticket?.user?.id) {
    emit('inspect-account', props.ticket.user.id)
  }
  router.push('/admin')
}

async function handleSummarize() {
  if (isSummarizing.value) return
  isSummarizing.value = true
  aiError.value = null

  const repliesList = Array.isArray(props.ticket?.replies) ? props.ticket.replies : []
  const repliesText = repliesList
    .map(r => `[${(r.sender_role || 'user').toUpperCase()} - ${r.sender_name || 'User'}]: ${r.message}`)
    .join('\n\n')

  const promptInput = `TICKET SUBJECT: ${props.ticket?.subject || 'N/A'}\n\nORIGINAL CUSTOMER MESSAGE:\n${props.ticket?.message || 'N/A'}\n\nCONVERSATION HISTORY (${repliesList.length} replies):\n${repliesText || 'No replies yet.'}`

  try {
    try {
      const res = await api.post('/auth/ai/summarize', {
        subject: props.ticket?.subject,
        message: props.ticket?.message,
        replies: repliesList,
      }, { timeout: 8000 })
      if (res.data?.summary) {
        summaryText.value = res.data.summary.trim()
        aiError.value = null
        isSummarizing.value = false
        return
      }
    } catch (serverErr: any) {
      if (serverErr?.response?.data?.code === 'API_KEY_INVALID' || serverErr?.response?.status === 401) {
        aiError.value = {
          title: 'Gemini API Key Incorrect / Unauthorized',
          message: 'The Google Generative AI API key configured on the server is missing or invalid.',
        }
        isSummarizing.value = false
        return
      }
      if (serverErr?.response?.data?.code === 'TOKEN_QUOTA_EXHAUSTED' || serverErr?.response?.status === 429) {
        aiError.value = {
          title: 'Model Rate Limit / Quota Exceeded',
          message: 'You have exceeded the free tier rate limit on Gemini. Please retry shortly.',
        }
        isSummarizing.value = false
        return
      }
    }

    const googleProvider = createGoogleGenerativeAI({ apiKey })
    const systemPrompt = `You are an AI support assistant for RoadLancer (a trucking and logistics platform).
Your task is to provide a concise, high-level summary of the support ticket and any subsequent conversation/replies.
Structure your summary cleanly with:
1. **Issue Overview**: A 1-2 sentence summary of the customer's core issue or request.
2. **Current Status & Key Updates**: What has been discussed or resolved in the replies so far (if any).
3. **Next Action Required**: What should the support agent do next to resolve or move this ticket forward.
Output ONLY the markdown summary directly without extra chatter or intro text.`

    let text = ''
    try {
      const res = await generateText({
        model: googleProvider('gemini-3.1-flash-lite'),
        maxTokens: 400,
        temperature: 0.3,
        maxRetries: 0,
        system: systemPrompt,
        prompt: promptInput,
      })
      text = res.text
    } catch (firstErr: any) {
      const firstMsg = (firstErr?.message || '').toLowerCase()
      if (firstMsg.includes('quota') || firstMsg.includes('rate') || firstMsg.includes('429') || firstErr?.status === 429 || firstMsg.includes('not found') || firstMsg.includes('404') || firstErr?.status === 404 || firstMsg.includes('is not supported') || firstMsg.includes('invalid model')) {
        const fallbackRes = await generateText({
          model: googleProvider('gemini-1.5-flash'),
          maxTokens: 400,
          temperature: 0.3,
          maxRetries: 0,
          system: systemPrompt,
          prompt: promptInput,
        })
        text = fallbackRes.text
      } else {
        throw firstErr
      }
    }

    if (text) {
      summaryText.value = text.trim()
      aiError.value = null
    }
  } catch (err: any) {
    console.error('Failed to summarize ticket:', err)
    const errMsg = (err?.message || '').toLowerCase()
    if (errMsg.includes('api key') || errMsg.includes('key not valid') || errMsg.includes('401') || err?.status === 401 || err?.status === 403) {
      aiError.value = {
        title: 'Gemini API Key Incorrect / Unauthorized',
        message: 'The Google Generative AI API key is missing or invalid.',
      }
    } else if (errMsg.includes('quota') || errMsg.includes('rate') || errMsg.includes('429') || err?.status === 429) {
      aiError.value = {
        title: 'Model Rate Limit / Quota Exceeded',
        message: 'You have exceeded the free tier rate limit. Please wait a moment and retry.',
      }
    } else {
      aiError.value = {
        title: 'Summarization Failed',
        message: err?.message || 'Could not generate summary at this time.',
      }
    }
  } finally {
    isSummarizing.value = false
  }
}
</script>

<template>
  <Card class="border-border/80 shadow-xs overflow-hidden rounded-2xl bg-card" data-testid="ticket-detail-subject-card">
    <!-- Top Integrated Ticket Header -->
    <CardHeader class="bg-muted/30 pb-4 pt-5 px-6 border-b border-border/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div class="flex items-center gap-3.5 min-w-0">
        <Avatar class="size-11 border border-border/80 shadow-2xs shrink-0">
          <AvatarFallback class="bg-primary/10 text-primary font-bold text-sm">
            {{ (ticket.sender_name || ticket.user?.name || 'U').charAt(0).toUpperCase() }}
          </AvatarFallback>
        </Avatar>
        <div class="min-w-0 space-y-1">
          <div class="flex items-center gap-2 flex-wrap">
            <h3 class="text-base font-bold text-foreground tracking-tight truncate" data-testid="ticket-sender-name">
              {{ ticket.sender_name || ticket.user?.name || 'Not Provided' }}
            </h3>
            <Badge variant="outline" class="text-[10px] font-semibold uppercase px-2 py-0 bg-background/80" data-testid="ticket-source-badge">
              {{ ticket.source || 'email' }}
            </Badge>
          </div>
          <p class="text-xs text-muted-foreground font-mono truncate flex items-center gap-1.5" data-testid="ticket-sender-email">
            <Mail class="size-3.5 shrink-0 text-muted-foreground/80" />
            <a :href="`mailto:${ticket.sender_email}`" class="hover:text-primary transition-colors">
              {{ ticket.sender_email }}
            </a>
          </p>
        </div>
      </div>

      <div class="flex items-center gap-3 self-start sm:self-center shrink-0 text-xs text-muted-foreground font-medium">
        <span class="flex items-center gap-1.5 bg-background/60 px-2.5 py-1 rounded-lg border border-border/50" data-testid="ticket-created-date">
          <Clock class="size-3.5 text-muted-foreground/80" /> Created on {{ ticket.created_at ? new Date(ticket.created_at).toLocaleString() : 'N/A' }}
        </span>
      </div>
    </CardHeader>

    <!-- Integrated Tabs Desk -->
    <Tabs defaultValue="message" class="w-full">
      <div class="bg-muted/20 border-b border-border/50 px-6 pt-2">
        <TabsList class="bg-transparent p-0 h-10 gap-6 border-b border-transparent justify-start">
          <TabsTrigger
            value="message"
            class="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-primary rounded-none px-1 pb-2.5 text-xs font-bold gap-2 text-muted-foreground transition-all cursor-pointer flex items-center"
          >
            <MessageSquare class="size-3.5" />
            <span>Ticket Message & Summary</span>
          </TabsTrigger>

          <TabsTrigger
            v-if="showSenderCard"
            value="sender"
            class="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-primary rounded-none px-1 pb-2.5 text-xs font-bold gap-2 text-muted-foreground transition-all cursor-pointer flex items-center"
            data-testid="ticket-sender-tab"
          >
            <User class="size-3.5" />
            <span>Sender Account & Profile</span>
            <Badge v-if="ticket.user" variant="secondary" class="text-[9px] uppercase px-1.5 py-0 bg-primary/10 text-primary font-extrabold ml-0.5">
              Linked
            </Badge>
          </TabsTrigger>
        </TabsList>
      </div>

      <!-- Tab 1: Ticket Message & AI Summary -->
      <TabsContent value="message" class="p-6 space-y-6 m-0 outline-none">
        <div class="space-y-2">
          <h2 class="text-xl sm:text-2xl font-extrabold text-foreground tracking-tight" data-testid="ticket-subject-title">
            {{ ticket.subject }}
          </h2>
          <div class="prose prose-sm dark:prose-invert max-w-none text-foreground/90 font-sans leading-relaxed whitespace-pre-line text-sm sm:text-base pt-2" data-testid="ticket-message-content">
            {{ ticket.message }}
          </div>
        </div>

        <!-- AI Summarize Section -->
        <div class="mt-6 pt-5 border-t border-border/60 flex flex-col items-start gap-4" data-testid="ticket-summarize-section">
          <Button
            variant="outline"
            size="sm"
            class="h-9 px-3.5 gap-2 font-semibold text-primary border-primary/30 hover:bg-primary/10 shadow-2xs transition-all flex items-center cursor-pointer"
            :disabled="isSummarizing"
            @click="handleSummarize"
            data-testid="ticket-summarize-button"
          >
            <Sparkles class="size-4 text-amber-500 animate-pulse" />
            <span>{{ isSummarizing ? 'Generating Summary...' : (summaryText ? 'Regenerate Summary' : 'Summarize Ticket & Conversation') }}</span>
          </Button>

          <!-- Error Alert -->
          <div v-if="aiError" class="w-full p-3.5 rounded-xl bg-destructive/10 border border-destructive/30 text-destructive text-xs space-y-1" data-testid="ticket-summarize-error">
            <div class="font-bold flex items-center gap-1.5">
              <AlertTriangle class="size-4 shrink-0" />
              <span>{{ aiError.title }}</span>
            </div>
            <p class="text-destructive/90">{{ aiError.message }}</p>
          </div>

          <!-- Summary Display Box -->
          <div v-if="summaryText" class="w-full p-5 rounded-2xl bg-gradient-to-br from-primary/5 via-primary/10 to-amber-500/10 border border-primary/20 shadow-xs space-y-3 animate-in fade-in duration-300" data-testid="ticket-summary-box">
            <div class="flex items-center justify-between border-b border-primary/15 pb-2.5">
              <div class="flex items-center gap-2">
                <Sparkles class="size-4 text-amber-500" />
                <h4 class="text-sm font-bold text-foreground tracking-tight">AI Ticket & Conversation Summary</h4>
              </div>
              <Badge variant="outline" class="text-[10px] uppercase font-bold text-primary border-primary/30 px-2 py-0.5 bg-primary/5">
                RoadLancer AI
              </Badge>
            </div>
            <div class="prose prose-sm dark:prose-invert max-w-none text-foreground/90 font-sans leading-relaxed text-xs sm:text-sm whitespace-pre-line" data-testid="ticket-summary-content">
              {{ summaryText }}
            </div>
          </div>
        </div>
      </TabsContent>

      <!-- Tab 2: Sender Account & Profile Details -->
      <TabsContent v-if="showSenderCard" value="sender" :force-mount="true" class="p-6 m-0 outline-none data-[state=inactive]:hidden" data-testid="ticket-detail-sender-card">
        <div class="space-y-6">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
            <div class="p-4 rounded-xl bg-muted/30 border border-border/60 space-y-1.5">
              <span class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Sender Email</span>
              <p class="font-mono font-medium text-foreground text-sm truncate flex items-center gap-2">
                <Mail class="size-3.5 text-muted-foreground shrink-0" />
                <a :href="`mailto:${ticket.sender_email}`" class="hover:text-primary">
                  {{ ticket.sender_email }}
                </a>
              </p>
            </div>

            <div class="p-4 rounded-xl bg-muted/30 border border-border/60 space-y-1.5">
              <span class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Sender Name</span>
              <p class="font-semibold text-foreground text-sm truncate">
                {{ ticket.sender_name || 'Not Provided' }}
              </p>
            </div>
          </div>

          <!-- Linked Profile Box -->
          <div v-if="ticket.user" class="p-5 rounded-2xl bg-primary/5 border border-primary/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4" data-testid="ticket-linked-user-box">
            <div class="space-y-1.5">
              <div class="flex items-center gap-2.5">
                <Badge variant="secondary" class="text-[10px] uppercase font-bold px-2.5 py-0.5 bg-primary/15 text-primary" data-testid="ticket-linked-role-badge">
                  Linked {{ ticket.user.role }} Profile
                </Badge>
                <span class="font-bold text-foreground text-base" data-testid="ticket-linked-user-name">{{ ticket.user.name }}</span>
              </div>
              <div class="flex items-center gap-3 text-xs text-muted-foreground font-mono">
                <span data-testid="ticket-linked-user-email">{{ ticket.user.email }}</span>
                <span v-if="ticket.user.phone" class="flex items-center gap-1.5" data-testid="ticket-linked-user-phone">
                  • <Phone class="size-3" /> {{ ticket.user.phone }}
                </span>
              </div>
            </div>
            <Button
              v-if="showInspectButton"
              variant="outline"
              size="sm"
              class="h-9 text-xs font-bold shadow-2xs gap-1.5 shrink-0 border-primary/30 hover:bg-primary/10 cursor-pointer"
              @click="handleInspect"
              data-testid="ticket-inspect-button"
            >
              Inspect Account <ExternalLink class="size-3.5" />
            </Button>
          </div>
          <div v-else class="p-4 rounded-xl bg-muted/40 border border-border/60 text-xs text-muted-foreground italic text-center" data-testid="ticket-no-linked-user">
            No registered RoadLancer account matched directly with sender email address (`{{ ticket.sender_email }}`).
          </div>
        </div>
      </TabsContent>
    </Tabs>
  </Card>
</template>
