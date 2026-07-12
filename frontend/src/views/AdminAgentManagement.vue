<script setup lang="ts">
import { ref } from 'vue'
import { useAdminAgents } from '@/composables/useAdminAgents'
import { useAuth } from '@/composables/useAuth'
import AgentsTable from '@/components/AgentsTable.vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog, DialogContent, DialogDescription, DialogFooter,
  DialogHeader, DialogTitle,
} from '@/components/ui/dialog'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Shield, LoaderCircle, AlertCircle, Plus } from '@lucide/vue'
import type { SortingState } from '@tanstack/vue-table'

const { user } = useAuth()

const {
  data: agents,
  isLoading,
  deactivateAgent,
  activateAgent,
  createAgent,
} = useAdminAgents()

const agentSorting = ref<SortingState>([])
const searchQuery = ref('')

const filteredAgents = ref<any[]>([])
import { watch } from 'vue'

watch([agents, searchQuery], () => {
  const q = searchQuery.value.toLowerCase().trim()
  if (!agents.value) {
    filteredAgents.value = []
    return
  }
  if (!q) {
    filteredAgents.value = agents.value
    return
  }
  filteredAgents.value = agents.value.filter(
    (a: any) =>
      a.name?.toLowerCase().includes(q) ||
      a.email?.toLowerCase().includes(q) ||
      a.role?.toLowerCase().includes(q),
  )
}, { immediate: true })

const deactivateDialogOpen = ref(false)
const agentToDeactivate = ref<any>(null)

function openDeactivateDialog(userId: string) {
  const agent = agents.value?.find((a: any) => a.id === userId)
  agentToDeactivate.value = agent || { id: userId, name: userId }
  deactivateDialogOpen.value = true
}

function confirmDeactivate() {
  if (agentToDeactivate.value) {
    deactivateAgent.mutate(agentToDeactivate.value.id)
    deactivateDialogOpen.value = false
    agentToDeactivate.value = null
  }
}

function handleActivate(userId: string) {
  activateAgent.mutate(userId)
}

const createDialogOpen = ref(false)
const createForm = ref({ name: '', email: '', password: '' })
const createErrors = ref({ name: '', email: '', password: '' })

function openCreateDialog() {
  createForm.value = { name: '', email: '', password: '' }
  createErrors.value = { name: '', email: '', password: '' }
  createDialogOpen.value = true
}

function validateCreateForm(): boolean {
  let valid = true
  createErrors.value = { name: '', email: '', password: '' }

  if (!createForm.value.name || createForm.value.name.length < 2) {
    createErrors.value.name = 'Name must be at least 2 characters'
    valid = false
  }
  if (!createForm.value.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(createForm.value.email)) {
    createErrors.value.email = 'Valid email is required'
    valid = false
  }
  if (!createForm.value.password || createForm.value.password.length < 8) {
    createErrors.value.password = 'Password must be at least 8 characters'
    valid = false
  }
  return valid
}

function confirmCreate() {
  if (!validateCreateForm()) return
  createAgent.mutate(createForm.value, {
    onSuccess: () => {
      createDialogOpen.value = false
    },
  })
}

const stats = ref({ total: 0, active: 0, deactivated: 0, supreme: 0 })

import { onMounted } from 'vue'

onMounted(() => {
  if (agents.value) {
    stats.value.total = agents.value.length
    stats.value.active = agents.value.filter((a: any) => !a.suspended).length
    stats.value.deactivated = agents.value.filter((a: any) => a.suspended).length
    stats.value.supreme = agents.value.filter((a: any) => a.isSupreme).length
  }
})

watch(agents, (val) => {
  if (val) {
    stats.value.total = val.length
    stats.value.active = val.filter((a: any) => !a.suspended).length
    stats.value.deactivated = val.filter((a: any) => a.suspended).length
    stats.value.supreme = val.filter((a: any) => a.isSupreme).length
  }
}, { immediate: true })
</script>

<template>
  <div class="flex-1 p-6 sm:p-8">
    <div class="max-w-7xl mx-auto">
      <!-- Admin Portal Navigation Header -->
      <div class="mb-6 p-5 rounded-2xl bg-gradient-to-r from-gray-900 to-teal-950 text-white flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl">
        <div>
          <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-teal-500/20 border border-teal-500/30 text-[10px] font-bold uppercase tracking-wider text-teal-300">
            <span>🛡️</span> RoadLancer Admin Portal
          </div>
          <h2 class="text-xl font-black text-white mt-1">System Administration & Helpdesk</h2>
        </div>
        <div class="flex items-center gap-2 flex-wrap">
          <a
            href="/admin"
            class="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white font-extrabold text-xs transition-all flex items-center gap-1.5"
          >
            <span>👥</span> User Management
          </a>
          <a
            href="/admin/agents"
            class="px-4 py-2 rounded-xl bg-teal-600 text-white font-extrabold text-xs shadow-md hover:bg-teal-500 transition-all flex items-center gap-1.5"
          >
            <span>🤖</span> Agent Management
          </a>
          <a
            href="/admin/support"
            class="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white font-extrabold text-xs transition-all flex items-center gap-1.5"
          >
            <span>🎧</span> Support Desk & Inbound Emails
          </a>
          <a
            href="/admin/jobs"
            class="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white font-extrabold text-xs transition-all flex items-center gap-1.5"
          >
            <span>⚡</span> pg-boss Queue Monitor
          </a>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 mb-6">
        <Card class="border shadow-sm">
          <CardContent class="p-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-primary/10 rounded-md flex items-center justify-center shrink-0">
                <Shield class="size-4 text-primary" />
              </div>
              <div>
                <p class="text-lg font-bold leading-none mb-1">{{ stats.total }}</p>
                <p class="text-[11px] text-muted-foreground">Total Agents</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card class="border shadow-sm">
          <CardContent class="p-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-emerald-500/10 rounded-md flex items-center justify-center shrink-0">
                <Shield class="size-4 text-emerald-600" />
              </div>
              <div>
                <p class="text-lg font-bold leading-none mb-1">{{ stats.active }}</p>
                <p class="text-[11px] text-muted-foreground">Active</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card class="border shadow-sm">
          <CardContent class="p-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-red-500/10 rounded-md flex items-center justify-center shrink-0">
                <Shield class="size-4 text-red-600" />
              </div>
              <div>
                <p class="text-lg font-bold leading-none mb-1">{{ stats.deactivated }}</p>
                <p class="text-[11px] text-muted-foreground">Deactivated</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card class="border shadow-sm">
          <CardContent class="p-3">
            <div class="flex items-center gap-2.5">
              <div class="w-8 h-8 bg-amber-500/10 rounded-md flex items-center justify-center shrink-0">
                <Shield class="size-4 text-amber-600" />
              </div>
              <div>
                <p class="text-lg font-bold leading-none mb-1">{{ stats.supreme }}</p>
                <p class="text-[11px] text-muted-foreground">Supreme Admins</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Search -->
      <div class="mb-4 flex items-center gap-2">
        <div class="relative flex-1 max-w-sm">
          <Input
            v-model="searchQuery"
            placeholder="Search agents by name, email, or role..."
            autocomplete="off"
            class="pl-9 h-9 text-sm"
          />
        </div>
        <Button
          v-if="user?.isSupreme"
          @click="openCreateDialog"
          size="sm"
          class="h-9"
        >
          <Plus class="size-4 mr-1" />
          Create Agent
        </Button>
      </div>

      <!-- Access Denied -->
      <Alert v-if="user && !user.isSupreme" variant="destructive" class="mb-6">
        <AlertCircle class="size-4" />
        <AlertDescription>
          You need supreme admin privileges to manage agents.
        </AlertDescription>
      </Alert>

      <!-- Agent Table -->
      <Card v-else class="border shadow-sm">
        <CardHeader class="pb-3 border-b border-border bg-card/50">
          <CardTitle class="text-lg font-bold text-foreground">Agent Management</CardTitle>
          <p class="text-xs text-muted-foreground">Deactivate agents to unassign their support tickets. Only supreme admins can manage agents.</p>
        </CardHeader>
        <CardContent class="p-4">
          <AgentsTable
            :agents="filteredAgents"
            :loading="isLoading"
            :is-supreme="user?.isSupreme"
            :deactivate-pending="deactivateAgent.isPending.value"
            :activate-pending="activateAgent.isPending.value"
            v-model:sorting="agentSorting"
            @deactivate="openDeactivateDialog"
            @activate="handleActivate"
          />
        </CardContent>
      </Card>

      <!-- Deactivate Confirmation Dialog -->
      <Dialog v-model:open="deactivateDialogOpen">
        <DialogContent class="sm:max-w-md">
          <DialogHeader>
            <DialogTitle class="flex items-center gap-2">
              <Shield class="size-5 text-destructive" />
              Deactivate Agent
            </DialogTitle>
            <DialogDescription>
              This will deactivate <strong>{{ agentToDeactivate?.name }}</strong> and unassign all support tickets assigned to them. Their sessions will also be revoked.
            </DialogDescription>
          </DialogHeader>

          <Alert variant="destructive">
            <AlertCircle class="size-4" />
            <AlertDescription>
              This action is reversible. You can reactivate the agent later using the Activate button.
            </AlertDescription>
          </Alert>

          <DialogFooter>
            <Button variant="outline" @click="deactivateDialogOpen = false">Cancel</Button>
            <Button
              variant="destructive"
              @click="confirmDeactivate"
              :disabled="deactivateAgent.isPending.value"
            >
              <LoaderCircle v-if="deactivateAgent.isPending.value" class="size-4 animate-spin mr-1" />
              Deactivate Agent
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <!-- Create Agent Dialog -->
      <Dialog v-model:open="createDialogOpen">
        <DialogContent class="sm:max-w-md">
          <DialogHeader>
            <DialogTitle class="flex items-center gap-2">
              <Plus class="size-5 text-primary" />
              Create New Agent
            </DialogTitle>
            <DialogDescription>
              Create a new admin/agent account. They will be able to log in immediately.
            </DialogDescription>
          </DialogHeader>

          <div class="space-y-4">
            <div class="space-y-2">
              <Label for="agent-name">Full Name</Label>
              <Input
                id="agent-name"
                v-model="createForm.name"
                placeholder="John Doe"
                :class="createErrors.name ? 'border-destructive' : ''"
              />
              <p v-if="createErrors.name" class="text-sm text-destructive">{{ createErrors.name }}</p>
            </div>

            <div class="space-y-2">
              <Label for="agent-email">Email</Label>
              <Input
                id="agent-email"
                v-model="createForm.email"
                type="email"
                placeholder="agent@roadlancer.com"
                :class="createErrors.email ? 'border-destructive' : ''"
              />
              <p v-if="createErrors.email" class="text-sm text-destructive">{{ createErrors.email }}</p>
            </div>

            <div class="space-y-2">
              <Label for="agent-password">Password</Label>
              <Input
                id="agent-password"
                v-model="createForm.password"
                type="password"
                autocomplete="new-password"
                placeholder="Min 8 characters"
                :class="createErrors.password ? 'border-destructive' : ''"
              />
              <p v-if="createErrors.password" class="text-sm text-destructive">{{ createErrors.password }}</p>
            </div>
          </div>

          <Alert v-if="createAgent.error.value" variant="destructive">
            <AlertCircle class="size-4" />
            <AlertDescription>{{ (createAgent.error.value as any)?.response?.data?.detail || 'Failed to create agent' }}</AlertDescription>
          </Alert>

          <DialogFooter>
            <Button variant="outline" @click="createDialogOpen = false">Cancel</Button>
            <Button
              @click="confirmCreate"
              :disabled="createAgent.isPending.value"
            >
              <LoaderCircle v-if="createAgent.isPending.value" class="size-4 animate-spin mr-1" />
              Create Agent
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  </div>
</template>
