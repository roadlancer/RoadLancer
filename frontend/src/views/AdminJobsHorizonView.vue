<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import api from '@/lib/api'
import { useAuth } from '@/composables/useAuth'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import {
  Activity,
  CheckCircle2,
  Clock,
  LoaderCircle,
  XCircle,
  RefreshCw,
  Terminal,
  Server,
  Cpu,
  Layers,
  ArrowUpRight,
  Trash2
} from '@lucide/vue'

const { user } = useAuth()

const isLoading = ref(true)
const isRefreshing = ref(false)
const isClearing = ref(false)
const autoRefresh = ref(true)
const intervalId = ref<any>(null)

const stats = ref({
  total: 0,
  created: 0,
  active: 0,
  completed: 0,
  failed: 0,
})

const jobs = ref<any[]>([])
const selectedJob = ref<any | null>(null)
const isInspectOpen = ref(false)

async function fetchJobs(quiet = false) {
  if (!quiet) isLoading.value = true
  else isRefreshing.value = true
  try {
    const { data } = await api.get('/support/admin/jobs/horizon')
    if (data && data.stats) {
      stats.value = data.stats
      jobs.value = data.jobs || []
    }
  } catch (err) {
    console.error('Failed to fetch Horizon queue stats:', err)
  } finally {
    isLoading.value = false
    isRefreshing.value = false
  }
}

async function clearFailedJobs() {
  if (!confirm('Are you sure you want to clear all failed/expired diagnostic jobs from the pg-boss queue history?')) return
  isClearing.value = true
  try {
    const { data } = await api.delete('/support/admin/jobs/clear-failed')
    if (data && data.success === false) {
      alert('Error clearing jobs: ' + data.error)
    }
    await fetchJobs(false)
  } catch (err: any) {
    console.error('Failed to clear failed jobs:', err)
    alert('Failed to clear jobs: ' + (err?.response?.data?.error || err?.message))
  } finally {
    isClearing.value = false
  }
}

function toggleAutoRefresh() {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    intervalId.value = setInterval(() => fetchJobs(true), 3000)
  } else if (intervalId.value) {
    clearInterval(intervalId.value)
  }
}

function openInspect(job: any) {
  selectedJob.value = job
  isInspectOpen.value = true
}

function getJobStateBadgeClass(state: string) {
  switch (state) {
    case 'created':
      return 'bg-purple-500/15 text-purple-700 dark:text-purple-300 border-purple-500/30 font-bold'
    case 'active':
      return 'bg-cyan-500/15 text-cyan-700 dark:text-cyan-300 border-cyan-500/30 font-extrabold animate-pulse'
    case 'completed':
      return 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border-emerald-500/30 font-semibold'
    case 'failed':
    case 'cancelled':
    case 'expired':
      return 'bg-rose-500/15 text-rose-700 dark:text-rose-400 border-rose-500/30 font-bold'
    default:
      return 'bg-muted text-muted-foreground border-border'
  }
}

function formatJson(data: any) {
  if (!data) return 'null'
  if (typeof data === 'string') {
    try {
      return JSON.stringify(JSON.parse(data), null, 2)
    } catch {
      return data
    }
  }
  return JSON.stringify(data, null, 2)
}

onMounted(() => {
  fetchJobs()
  intervalId.value = setInterval(() => {
    if (autoRefresh.value) fetchJobs(true)
  }, 3000)
})

onUnmounted(() => {
  if (intervalId.value) clearInterval(intervalId.value)
})
</script>

<template>
  <div class="flex-1 p-6 sm:p-8 bg-background min-h-screen">
    <div class="max-w-7xl mx-auto">
      <!-- Admin Portal Navigation Header -->
      <div class="mb-6 p-5 rounded-2xl bg-gradient-to-r from-gray-900 to-indigo-950 text-white flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl border border-indigo-900/30">
        <div>
          <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-[10px] font-bold uppercase tracking-wider text-indigo-300">
            <span>⚡</span> RoadLancer pg-boss Queue Engine
          </div>
          <h2 class="text-xl font-black text-white mt-1 flex items-center gap-2">
            <span>Real-Time pg-boss Queue Dashboard</span>
            <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-300 text-xs font-mono font-bold border border-emerald-500/30">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span> Live PostgreSQL
            </span>
          </h2>
        </div>
        <div class="flex items-center gap-2 flex-wrap">
          <a
            href="/admin"
            class="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white font-extrabold text-xs transition-all flex items-center gap-1.5"
          >
            <span>👥</span> User Management
          </a>
          <a
            v-if="user?.isSupreme"
            href="/admin/agents"
            class="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white font-extrabold text-xs transition-all flex items-center gap-1.5"
          >
            <span>🤖</span> Agent Management
          </a>
          <a
            href="/admin/support"
            class="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white font-extrabold text-xs transition-all flex items-center gap-1.5"
          >
            <span>🎧</span> Support Desk
          </a>
          <a
            href="/admin/jobs"
            class="px-4 py-2 rounded-xl bg-indigo-600 text-white font-extrabold text-xs shadow-md hover:bg-indigo-500 transition-all flex items-center gap-1.5 border border-indigo-400"
          >
            <span>⚡</span> pg-boss Queue Monitor
          </a>
        </div>
      </div>

      <!-- Queue Engine System Banner -->
      <div class="mb-6 p-4 rounded-2xl bg-card border border-border shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="p-3 rounded-xl bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20">
            <Server class="size-6" />
          </div>
          <div>
            <h4 class="text-sm font-bold text-foreground">PostgreSQL Multi-Worker Orchestration</h4>
            <p class="text-xs text-muted-foreground mt-0.5">
              Monitoring <code class="font-mono bg-muted px-1 py-0.5 rounded text-foreground font-semibold">pgboss.job</code> across Bun Worker Threads (`auth-server`) and Python FastAPI tasks (`backend`).
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2.5">
          <Button
            type="button"
            variant="outline"
            size="sm"
            @click="toggleAutoRefresh"
            :class="[
              'h-9 text-xs font-semibold border transition-all flex items-center gap-1.5 shadow-2xs cursor-pointer',
              autoRefresh ? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-500/30 ring-1 ring-emerald-500/40' : 'bg-background hover:bg-muted text-muted-foreground'
            ]"
          >
            <RefreshCw :class="['size-3.5', autoRefresh ? 'animate-spin' : '']" />
            <span>{{ autoRefresh ? 'Live Auto-Refresh: 3s' : 'Auto-Refresh Paused' }}</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            class="h-9 text-xs font-semibold"
            @click="fetchJobs()"
            :disabled="isLoading || isRefreshing"
          >
            <LoaderCircle v-if="isLoading || isRefreshing" class="size-3.5 animate-spin mr-1.5" />
            <span>Refresh Now</span>
          </Button>
          <Button
            v-if="stats.failed > 0"
            variant="destructive"
            size="sm"
            class="h-9 text-xs font-semibold flex items-center gap-1.5 cursor-pointer shadow-2xs"
            @click="clearFailedJobs"
            :disabled="isClearing"
          >
            <LoaderCircle v-if="isClearing" class="size-3.5 animate-spin mr-1" />
            <Trash2 v-else class="size-3.5" />
            <span>Clear Failed ({{ stats.failed }})</span>
          </Button>
        </div>
      </div>

      <!-- KPI Metrics Grid (Horizon Style) -->
      <div class="grid grid-cols-2 sm:grid-cols-5 gap-3.5 mb-6">
        <!-- Total Jobs -->
        <Card class="border shadow-2xs hover:border-indigo-500/40 transition-all bg-card/60">
          <CardContent class="p-4 flex items-center justify-between">
            <div>
              <p class="text-xs font-bold text-muted-foreground uppercase tracking-wider">Total Dispatched</p>
              <h3 class="text-2xl font-black text-foreground mt-1">{{ stats.total }}</h3>
            </div>
            <div class="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
              <Layers class="size-5" />
            </div>
          </CardContent>
        </Card>

        <!-- Queued / Created -->
        <Card class="border shadow-2xs hover:border-purple-500/40 transition-all bg-card/60">
          <CardContent class="p-4 flex items-center justify-between">
            <div>
              <p class="text-xs font-bold text-muted-foreground uppercase tracking-wider">Waiting in Queue</p>
              <h3 class="text-2xl font-black text-purple-600 dark:text-purple-400 mt-1">{{ stats.created }}</h3>
            </div>
            <div class="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-600 dark:text-purple-400">
              <Clock class="size-5" />
            </div>
          </CardContent>
        </Card>

        <!-- Active / Processing -->
        <Card class="border shadow-2xs hover:border-cyan-500/40 transition-all bg-card/60">
          <CardContent class="p-4 flex items-center justify-between">
            <div>
              <p class="text-xs font-bold text-muted-foreground uppercase tracking-wider">Active Executing</p>
              <h3 class="text-2xl font-black text-cyan-600 dark:text-cyan-400 mt-1">{{ stats.active }}</h3>
            </div>
            <div class="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-600 dark:text-cyan-400">
              <Activity class="size-5 animate-pulse" />
            </div>
          </CardContent>
        </Card>

        <!-- Completed Successfully -->
        <Card class="border shadow-2xs hover:border-emerald-500/40 transition-all bg-card/60">
          <CardContent class="p-4 flex items-center justify-between">
            <div>
              <p class="text-xs font-bold text-muted-foreground uppercase tracking-wider">Completed Jobs</p>
              <h3 class="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-1">{{ stats.completed }}</h3>
            </div>
            <div class="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
              <CheckCircle2 class="size-5" />
            </div>
          </CardContent>
        </Card>

        <!-- Failed / Dead Letter -->
        <Card class="border shadow-2xs hover:border-rose-500/40 transition-all bg-card/60">
          <CardContent class="p-4 flex items-center justify-between">
            <div>
              <p class="text-xs font-bold text-muted-foreground uppercase tracking-wider">Failed / Expired</p>
              <h3 class="text-2xl font-black text-rose-600 dark:text-rose-400 mt-1">{{ stats.failed }}</h3>
            </div>
            <div class="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-600 dark:text-rose-400">
              <XCircle class="size-5" />
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Live Job Queue Table -->
      <Card class="border shadow-sm">
        <CardHeader class="pb-4 border-b border-border bg-card/50">
          <div class="flex items-center justify-between">
            <div>
              <CardTitle class="text-lg font-bold text-foreground flex items-center gap-2">
                <Terminal class="size-5 text-indigo-600 dark:text-indigo-400" />
                <span>Job Execution Trajectory (`pgboss.job`)</span>
              </CardTitle>
              <CardDescription class="text-xs mt-0.5">
                Displays the 100 most recent background tasks dispatched to Google Gemini AI and database sync queues.
              </CardDescription>
            </div>
            <div class="text-xs font-mono text-muted-foreground">
              {{ jobs.length }} records loaded
            </div>
          </div>
        </CardHeader>
        <CardContent class="p-0">
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs border-collapse">
              <thead>
                <tr class="border-b border-border bg-muted/40 font-bold uppercase tracking-wider text-[11px] text-muted-foreground">
                  <th class="py-3 px-4">Job ID</th>
                  <th class="py-3 px-4">Queue Name</th>
                  <th class="py-3 px-4">State</th>
                  <th class="py-3 px-4">Priority</th>
                  <th class="py-3 px-4">Dispatched On</th>
                  <th class="py-3 px-4">Started / Completed</th>
                  <th class="py-3 px-4 text-right">Payload Diagnostics</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-border font-sans">
                <tr v-if="isLoading && jobs.length === 0">
                  <td colspan="7" class="py-12 text-center text-muted-foreground">
                    <LoaderCircle class="size-6 animate-spin mx-auto mb-2 text-indigo-500" />
                    Connecting to PostgreSQL queue storage...
                  </td>
                </tr>
                <tr v-else-if="jobs.length === 0">
                  <td colspan="7" class="py-12 text-center text-muted-foreground">
                    No background jobs found in <code class="font-mono bg-muted px-1.5 py-0.5 rounded">pgboss.job</code> yet.
                  </td>
                </tr>
                <tr
                  v-for="job in jobs"
                  :key="job.id"
                  class="hover:bg-muted/30 transition-colors cursor-pointer group"
                  @click="openInspect(job)"
                >
                  <td class="py-3 px-4 font-mono font-bold text-foreground">
                    #{{ job.id?.slice(0, 8) }}...
                  </td>
                  <td class="py-3 px-4">
                    <Badge variant="outline" class="font-mono font-bold text-[11px] bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border-indigo-500/20">
                      {{ job.name }}
                    </Badge>
                  </td>
                  <td class="py-3 px-4">
                    <Badge :class="['uppercase text-[10px] px-2 py-0.5 border', getJobStateBadgeClass(job.state)]">
                      {{ job.state }}
                    </Badge>
                  </td>
                  <td class="py-3 px-4 font-semibold text-muted-foreground">
                    {{ job.priority ?? 0 }}
                  </td>
                  <td class="py-3 px-4 font-mono text-muted-foreground">
                    {{ job.createdOn ? new Date(job.createdOn).toLocaleTimeString() : 'N/A' }}
                  </td>
                  <td class="py-3 px-4 font-mono text-[11px] text-muted-foreground">
                    <div v-if="job.completedOn" class="text-emerald-600 dark:text-emerald-400 font-bold">
                      ✓ {{ new Date(job.completedOn).toLocaleTimeString() }}
                    </div>
                    <div v-else-if="job.startedOn" class="text-cyan-600 dark:text-cyan-400 animate-pulse font-bold">
                      ⚙ Executing since {{ new Date(job.startedOn).toLocaleTimeString() }}
                    </div>
                    <div v-else class="text-muted-foreground italic">Queued</div>
                  </td>
                  <td class="py-3 px-4 text-right">
                    <Button variant="ghost" size="sm" class="h-7 px-2.5 text-xs font-semibold group-hover:bg-indigo-500/10 group-hover:text-indigo-600 dark:group-hover:text-indigo-400">
                      <span>Inspect JSON</span>
                      <ArrowUpRight class="size-3.5 ml-1" />
                    </Button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <!-- Job Inspect Modal -->
      <Dialog :open="isInspectOpen" @update:open="isInspectOpen = $event">
        <DialogContent class="max-w-3xl max-h-[90vh] overflow-y-auto p-6 rounded-2xl bg-card border border-border shadow-2xl">
          <DialogHeader v-if="selectedJob">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <Badge class="bg-foreground text-background font-mono font-bold text-xs px-2.5 py-1">
                  Job #{{ selectedJob.id }}
                </Badge>
                <Badge :class="['uppercase text-xs font-bold px-2.5 py-0.5 border', getJobStateBadgeClass(selectedJob.state)]">
                  {{ selectedJob.state }}
                </Badge>
              </div>
              <span class="text-xs font-mono text-muted-foreground">
                Dispatched: {{ new Date(selectedJob.createdOn).toLocaleString() }}
              </span>
            </div>
            <DialogTitle class="text-xl font-bold text-foreground mt-3 flex items-center gap-2">
              <span>Queue Topic:</span>
              <code class="font-mono bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/20">{{ selectedJob.name }}</code>
            </DialogTitle>
            <DialogDescription class="text-xs text-muted-foreground">
              Complete input payload (`data`) and execution result output (`output`) recorded in PostgreSQL.
            </DialogDescription>
          </DialogHeader>

          <div v-if="selectedJob" class="space-y-4 my-2">
            <!-- Input Data Section -->
            <div class="space-y-1.5">
              <div class="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                <span>📥</span> Input Arguments & Payload (`data`)
              </div>
              <pre class="p-4 rounded-xl bg-muted/70 border border-border text-xs font-mono text-foreground overflow-x-auto leading-relaxed max-h-60">{{ formatJson(selectedJob.data) }}</pre>
            </div>

            <!-- Output / Error Section -->
            <div class="space-y-1.5">
              <div class="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                <span>📤</span> Worker Execution Result (`output` / Diagnostics)
              </div>
              <pre
                :class="[
                  'p-4 rounded-xl border text-xs font-mono overflow-x-auto leading-relaxed max-h-60',
                  selectedJob.state === 'failed' ? 'bg-rose-500/10 border-rose-500/30 text-rose-300' : 'bg-muted/70 border-border text-foreground'
                ]"
              >{{ formatJson(selectedJob.output || (selectedJob.state === 'completed' ? { status: 'Success', note: 'Worker finished without error return.' } : { status: selectedJob.state })) }}</pre>
            </div>

            <div class="flex items-center justify-end pt-2">
              <Button size="sm" @click="isInspectOpen = false" class="font-semibold text-xs px-5">
                Close Inspector
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  </div>
</template>
