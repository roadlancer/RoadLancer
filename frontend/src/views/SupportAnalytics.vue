<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { BarChart3, Ticket, MailOpen, Bot, Percent, Clock, ArrowLeft, CalendarDays } from '@lucide/vue'

const router = useRouter()

interface Analytics {
  total: number
  open: number
  resolved: number
  ai_resolved: number
  ai_resolved_pct: number
  avg_resolution: string
  categories: Record<string, { total: number; open: number; resolved: number }>
}

interface DayData {
  date: string
  total: number
  ai_resolved: number
}

const data = ref<Analytics | null>(null)
const daily = ref<DayData[]>([])
const loading = ref(true)
const loadingDaily = ref(true)
const error = ref('')

const categoryLabels: Record<string, string> = {
  logistics_breakdown: 'Logistics Breakdown',
  billing_payment: 'Billing & Payment',
  verification_kyc: 'Verification & KYC',
  shipment_tracking: 'Shipment Tracking',
  account_access: 'Account & Access',
  general: 'General',
}

const categoryColors: Record<string, string> = {
  logistics_breakdown: 'bg-red-500',
  billing_payment: 'bg-amber-500',
  verification_kyc: 'bg-blue-500',
  shipment_tracking: 'bg-emerald-500',
  account_access: 'bg-violet-500',
  general: 'bg-slate-500',
}

const categoryIcons: Record<string, string> = {
  logistics_breakdown: '🔧',
  billing_payment: '💳',
  verification_kyc: '🪪',
  shipment_tracking: '📦',
  account_access: '🔐',
  general: '💬',
}

const maxDaily = computed(() => {
  if (!daily.value.length) return 1
  return Math.max(...daily.value.map(d => d.total), 1)
})

const barChartHeight = 200

function formatDate(dateStr: string) {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function isWeekend(dateStr: string) {
  const d = new Date(dateStr + 'T00:00:00')
  const day = d.getDay()
  return day === 0 || day === 6
}

onMounted(async () => {
  try {
    const [analyticsRes, dailyRes] = await Promise.all([
      api.get('/support/admin/analytics'),
      api.get('/support/admin/analytics/daily'),
    ])
    data.value = analyticsRes.data
    daily.value = dailyRes.data
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e.message || 'Failed to load analytics'
  } finally {
    loading.value = false
    loadingDaily.value = false
  }
})
</script>

<template>
  <div class="flex-1 p-6 sm:p-8">
    <div class="max-w-7xl mx-auto space-y-6">
      <!-- Header -->
      <div class="p-5 rounded-2xl bg-gradient-to-r from-gray-900 to-teal-950 text-white flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl">
        <div class="flex items-center gap-3">
          <div class="size-10 rounded-xl bg-teal-500/20 border border-teal-500/30 flex items-center justify-center">
            <BarChart3 class="size-5 text-teal-300" />
          </div>
          <div>
            <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-teal-500/20 border border-teal-500/30 text-[10px] font-bold uppercase tracking-wider text-teal-300 mb-1">
              <span>📊</span> AI Support Analytics
            </div>
            <h1 class="text-xl font-black text-white">Support Analytics Dashboard</h1>
            <p class="text-xs text-teal-200/70 mt-0.5">Real-time AI-powered ticket resolution metrics</p>
          </div>
        </div>
        <Button variant="outline" size="sm" class="bg-white/10 hover:bg-white/20 border-white/20 text-white font-bold text-xs h-9 px-4 rounded-xl" @click="router.push('/admin/support')">
          <ArrowLeft class="size-3.5 mr-1.5" />
          Back to Support Desk
        </Button>
      </div>

      <!-- Error -->
      <div v-if="error" class="p-4 rounded-xl bg-destructive/10 border border-destructive/20 text-sm text-destructive font-medium">
        {{ error }}
      </div>

      <!-- Loading Skeleton -->
      <div v-if="loading" class="space-y-6">
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          <Card v-for="i in 5" :key="i">
            <CardContent class="p-4">
              <div class="flex items-center gap-3">
                <Skeleton class="w-10 h-10 rounded-xl shrink-0" />
                <div class="space-y-1.5 min-w-0">
                  <Skeleton class="h-3 w-20" />
                  <Skeleton class="h-6 w-12" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        <Card>
          <CardContent class="p-5">
            <Skeleton class="h-[240px] w-full rounded-lg" />
          </CardContent>
        </Card>
      </div>

      <!-- KPI Cards -->
      <div v-else-if="data" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        <Card class="border-border/80 shadow-sm hover:shadow-md transition-shadow">
          <CardContent class="p-4 flex items-center gap-3">
            <div class="size-10 rounded-xl bg-primary/10 flex items-center justify-center shrink-0">
              <Ticket class="size-5 text-primary" />
            </div>
            <div class="min-w-0">
              <p class="text-[11px] text-muted-foreground font-semibold uppercase tracking-wide truncate">Total Tickets</p>
              <p class="text-2xl font-black text-foreground leading-tight">{{ data.total }}</p>
            </div>
          </CardContent>
        </Card>

        <Card class="border-border/80 shadow-sm hover:shadow-md transition-shadow">
          <CardContent class="p-4 flex items-center gap-3">
            <div class="size-10 rounded-xl bg-blue-500/10 flex items-center justify-center shrink-0">
              <MailOpen class="size-5 text-blue-500" />
            </div>
            <div class="min-w-0">
              <p class="text-[11px] text-muted-foreground font-semibold uppercase tracking-wide truncate">Open Tickets</p>
              <p class="text-2xl font-black text-foreground leading-tight">{{ data.open }}</p>
            </div>
          </CardContent>
        </Card>

        <Card class="border-border/80 shadow-sm hover:shadow-md transition-shadow">
          <CardContent class="p-4 flex items-center gap-3">
            <div class="size-10 rounded-xl bg-emerald-500/10 flex items-center justify-center shrink-0">
              <Bot class="size-5 text-emerald-500" />
            </div>
            <div class="min-w-0">
              <p class="text-[11px] text-muted-foreground font-semibold uppercase tracking-wide truncate">AI Resolved</p>
              <p class="text-2xl font-black text-foreground leading-tight">{{ data.ai_resolved }}</p>
            </div>
          </CardContent>
        </Card>

        <Card class="border-border/80 shadow-sm hover:shadow-md transition-shadow">
          <CardContent class="p-4 flex items-center gap-3">
            <div class="size-10 rounded-xl bg-violet-500/10 flex items-center justify-center shrink-0">
              <Percent class="size-5 text-violet-500" />
            </div>
            <div class="min-w-0">
              <p class="text-[11px] text-muted-foreground font-semibold uppercase tracking-wide truncate">AI Resolution %</p>
              <p class="text-2xl font-black text-foreground leading-tight">{{ data.ai_resolved_pct }}%</p>
            </div>
          </CardContent>
        </Card>

        <Card class="border-border/80 shadow-sm hover:shadow-md transition-shadow">
          <CardContent class="p-4 flex items-center gap-3">
            <div class="size-10 rounded-xl bg-amber-500/10 flex items-center justify-center shrink-0">
              <Clock class="size-5 text-amber-500" />
            </div>
            <div class="min-w-0">
              <p class="text-[11px] text-muted-foreground font-semibold uppercase tracking-wide truncate">Avg Resolution</p>
              <p class="text-2xl font-black text-foreground leading-tight">{{ data.avg_resolution }}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Tickets Per Day Bar Chart -->
      <Card v-if="!loadingDaily" class="border-border/80 shadow-sm">
        <CardHeader class="py-4 px-5 border-b border-border/50 bg-muted/20">
          <div class="flex items-center justify-between">
            <CardTitle class="text-sm font-bold text-foreground flex items-center gap-2">
              <CalendarDays class="size-4 text-primary" />
              Tickets Per Day (Last 30 Days)
            </CardTitle>
            <div class="flex items-center gap-3 text-[10px] font-semibold text-muted-foreground">
              <span class="flex items-center gap-1"><span class="size-2 rounded-full bg-primary inline-block" /> Total</span>
              <span class="flex items-center gap-1"><span class="size-2 rounded-full bg-emerald-500 inline-block" /> AI Resolved</span>
            </div>
          </div>
        </CardHeader>
        <CardContent class="p-5">
          <!-- Empty state -->
          <div v-if="!daily.length || daily.every(d => d.total === 0)" class="h-[200px] flex items-center justify-center text-muted-foreground text-sm">
            No ticket activity in the last 30 days.
          </div>

          <!-- Bar chart -->
          <div v-else class="relative" :style="{ height: barChartHeight + 40 + 'px' }">
            <!-- Y-axis grid lines -->
            <div class="absolute inset-x-0 bottom-10 top-0 flex flex-col justify-between pointer-events-none">
              <div v-for="i in 4" :key="i" class="border-b border-border/30 w-full" />
            </div>

            <!-- Bars container -->
            <div class="absolute inset-x-0 bottom-10 top-0 flex items-end gap-[2px] px-1">
              <div
                v-for="(day, idx) in daily"
                :key="day.date"
                class="flex-1 flex flex-col items-center justify-end relative group cursor-pointer"
                :style="{ height: '100%' }"
              >
                <!-- Tooltip -->
                <div class="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 bg-foreground text-white text-[10px] font-bold px-2 py-1 rounded-md whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 shadow-lg">
                  {{ day.total }} total, {{ day.ai_resolved }} AI
                  <div class="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-foreground" />
                </div>

                <!-- Stacked bars -->
                <div class="w-full flex flex-col justify-end" :style="{ height: barChartHeight + 'px' }">
                  <!-- AI resolved portion -->
                  <div
                    v-if="day.ai_resolved > 0"
                    class="w-full bg-emerald-500 rounded-t-sm transition-all duration-300"
                    :style="{ height: (day.ai_resolved / maxDaily * barChartHeight) + 'px' }"
                  />
                  <!-- Remaining total portion -->
                  <div
                    v-if="day.total > day.ai_resolved"
                    class="w-full bg-primary transition-all duration-300"
                    :class="day.ai_resolved === 0 ? 'rounded-t-sm' : ''"
                    :style="{ height: ((day.total - day.ai_resolved) / maxDaily * barChartHeight) + 'px' }"
                  />
                  <!-- Empty day placeholder -->
                  <div
                    v-if="day.total === 0"
                    class="w-full bg-muted/40 rounded-t-sm transition-all duration-300"
                    style="height: 2px"
                  />
                </div>
              </div>
            </div>

            <!-- X-axis labels (show every 5th day) -->
            <div class="absolute bottom-0 inset-x-0 h-10 flex items-start px-1">
              <div
                v-for="(day, idx) in daily"
                :key="'label-' + day.date"
                class="flex-1 text-center"
              >
                <span
                  v-if="idx % 5 === 0 || idx === daily.length - 1"
                  class="text-[9px] font-mono text-muted-foreground"
                  :class="{ 'text-foreground/70 font-semibold': isWeekend(day.date) }"
                >
                  {{ formatDate(day.date) }}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Category Breakdown Card -->
      <Card v-if="data && data.categories && Object.keys(data.categories).length > 0" class="border-border/80 shadow-sm">
        <CardHeader class="py-4 px-5 border-b border-border/50 bg-muted/20">
          <CardTitle class="text-sm font-bold text-foreground flex items-center gap-2">
            <span class="size-6 rounded-md bg-primary/10 flex items-center justify-center text-xs">📋</span>
            Category Breakdown
          </CardTitle>
        </CardHeader>
        <CardContent class="p-5">
          <div class="space-y-5">
            <div
              v-for="(stats, cat) in data.categories"
              :key="cat"
              class="group"
            >
              <div class="flex items-center gap-3 mb-2">
                <span class="text-sm">{{ categoryIcons[cat] || '📁' }}</span>
                <span class="text-sm font-semibold text-foreground flex-1 truncate">
                  {{ categoryLabels[cat] || cat }}
                </span>
                <span class="text-xs font-mono font-bold text-muted-foreground bg-muted/60 px-2 py-0.5 rounded-md">
                  {{ stats.total }}
                </span>
              </div>
              <div class="h-2.5 bg-muted/60 rounded-full overflow-hidden flex ml-6">
                <div
                  v-if="stats.resolved > 0"
                  class="h-full bg-emerald-500 transition-all duration-500 rounded-l-full"
                  :style="{ width: (stats.resolved / stats.total * 100) + '%' }"
                />
                <div
                  v-if="stats.open > 0"
                  class="h-full bg-blue-500 transition-all duration-500"
                  :class="stats.resolved === 0 ? 'rounded-l-full' : ''"
                  :style="{ width: (stats.open / stats.total * 100) + '%' }"
                />
              </div>
              <div class="flex gap-4 mt-1.5 ml-6">
                <span class="text-[11px] text-emerald-600 font-semibold">{{ stats.resolved }} resolved</span>
                <span class="text-[11px] text-blue-600 font-semibold">{{ stats.open }} open</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Empty State -->
      <Card v-if="!loading && data && (!data.categories || Object.keys(data.categories).length === 0)" class="border-border/80 shadow-sm">
        <CardContent class="p-12 text-center">
          <BarChart3 class="size-10 text-muted-foreground/40 mx-auto mb-3" />
          <p class="text-sm font-semibold text-foreground">No data yet</p>
          <p class="text-xs text-muted-foreground mt-1">Analytics will appear once tickets are created.</p>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
