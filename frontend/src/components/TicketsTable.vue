<script lang="ts" setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  useVueTable,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  type SortingState,
  type ColumnDef,
  type VisibilityState,
} from '@tanstack/vue-table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  type SupportTicket,
  parseAssignedAgent,
  formatAssignedAgentNotes,
  useSupportAgents,
  type SupportAgent,
} from '@/composables/useSupportTickets'
import {
  MessageSquare,
  Mail,
  Globe,
  ArrowUp,
  ArrowDown,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  UserCheck,
  SlidersHorizontal,
} from '@lucide/vue'
import { useAuth } from '@/composables/useAuth'

const { user } = useAuth()

const props = defineProps<{
  tickets: SupportTicket[]
  loading?: boolean
  sorting: SortingState
}>()

const router = useRouter()
const agents = useSupportAgents()

const emit = defineEmits<{
  (e: 'inspect', ticket: SupportTicket): void
  (e: 'resolve', ticket: SupportTicket): void
  (e: 'update:sorting', sorting: SortingState): void
  (e: 'assign', payload: { ticket: SupportTicket; agentId: string | null; agentName: string | null; newNotes: string }): void
  (e: 'update-status', payload: { ticket: SupportTicket; status: string }): void
  (e: 'update-category', payload: { ticket: SupportTicket; category: string }): void
}>()

function handleRowAssign(ticket: SupportTicket, event: Event) {
  const select = event.target as HTMLSelectElement
  const agentId = select.value
  const foundAgent = agents.value.find((a) => a.id === agentId)
  const agentName = foundAgent && agentId ? foundAgent.name : null
  const parsed = parseAssignedAgent(ticket.admin_notes)
  const newNotes = formatAssignedAgentNotes(agentId || null, agentName, parsed.cleanNotes) || ''
  emit('assign', { ticket, agentId: agentId || null, agentName, newNotes })
}

function handleRowStatus(ticket: SupportTicket, event: Event) {
  const select = event.target as HTMLSelectElement
  emit('update-status', { ticket, status: select.value })
}

function handleRowCategory(ticket: SupportTicket, event: Event) {
  const select = event.target as HTMLSelectElement
  emit('update-category', { ticket, category: select.value })
}

function getCategoryBadgeClass(category?: string) {
  switch (category) {
    case 'verification':
    case 'verification_kyc':
      return 'bg-purple-100 text-purple-800 border-purple-200 dark:bg-purple-950/40 dark:text-purple-300'
    case 'billing':
    case 'billing_payment':
      return 'bg-emerald-100 text-emerald-800 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300'
    case 'shipments':
    case 'shipment_tracking':
      return 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300'
    case 'technical':
    case 'logistics_breakdown':
      return 'bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-950/40 dark:text-orange-300'
    case 'account':
    case 'account_access':
      return 'bg-indigo-100 text-indigo-800 border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-300'
    default:
      return 'bg-slate-100 text-slate-800 border-slate-200 dark:bg-slate-800 dark:text-slate-300'
  }
}

function getStatusBadgeClass(status: string) {
  switch (status) {
    case 'new':
      return 'bg-purple-100 text-purple-800 border-purple-200 dark:bg-purple-950/40 dark:text-purple-300 font-extrabold animate-pulse'
    case 'processing':
      return 'bg-cyan-100 text-cyan-800 border-cyan-200 dark:bg-cyan-950/40 dark:text-cyan-300 font-extrabold animate-pulse'
    case 'open':
      return 'bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300'
    case 'in_progress':
      return 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300'
    case 'resolved':
      return 'bg-green-100 text-green-800 border-green-200 dark:bg-green-950/40 dark:text-green-300'
    case 'closed':
      return 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-800 dark:text-gray-300'
    default:
      return 'bg-muted text-muted-foreground border-border'
  }
}

function getPriorityBadgeClass(priority: string) {
  switch (priority) {
    case 'urgent':
      return 'bg-red-500 text-white font-bold animate-pulse'
    case 'high':
      return 'bg-orange-100 text-orange-800 border-orange-200 font-semibold'
    case 'normal':
      return 'bg-blue-50 text-blue-700 border-blue-200'
    default:
      return 'bg-muted text-muted-foreground border-border'
  }
}

const priorityOrder: Record<string, number> = { urgent: 4, high: 3, normal: 2, low: 1 }
const statusOrder: Record<string, number> = { open: 4, in_progress: 3, resolved: 2, closed: 1 }

const columns = computed<ColumnDef<SupportTicket, any>[]>(() => [
  {
    accessorKey: 'ticket_number',
    header: 'Ticket #',
    enableSorting: true,
  },
  {
    accessorKey: 'subject',
    header: 'Subject',
    enableSorting: true,
  },
  {
    accessorKey: 'source',
    header: 'Source',
    enableSorting: true,
  },
  {
    accessorKey: 'category',
    header: 'Category',
    enableSorting: true,
  },
  {
    accessorKey: 'priority',
    header: 'Priority',
    enableSorting: true,
    sortingFn: (rowA, rowB, columnId) => {
      const pA = priorityOrder[(rowA.getValue(columnId) as string) || 'normal'] ?? 0
      const pB = priorityOrder[(rowB.getValue(columnId) as string) || 'normal'] ?? 0
      return pA - pB
    },
  },
  {
    accessorKey: 'status',
    header: 'Status',
    enableSorting: true,
    sortingFn: (rowA, rowB, columnId) => {
      const sA = statusOrder[(rowA.getValue(columnId) as string) || 'open'] ?? 0
      const sB = statusOrder[(rowB.getValue(columnId) as string) || 'open'] ?? 0
      return sA - sB
    },
  },
  {
    id: 'assigned_to',
    header: 'Assigned Agent',
    enableSorting: false,
  },
  {
    accessorKey: 'created_at',
    header: 'Created At',
    enableSorting: true,
    sortingFn: (rowA, rowB, columnId) => {
      const dateA = new Date((rowA.getValue(columnId) as string) || 0).getTime()
      const dateB = new Date((rowB.getValue(columnId) as string) || 0).getTime()
      return dateA - dateB
    },
  },
  {
    id: 'actions',
    header: 'Actions',
    enableSorting: false,
  },
])

const toggleableColumns = [
  { id: 'ticket_number', label: 'Ticket #', required: true },
  { id: 'subject', label: 'Subject', required: true },
  { id: 'source', label: 'Source', required: false },
  { id: 'category', label: 'Category', required: false },
  { id: 'priority', label: 'Priority', required: false },
  { id: 'status', label: 'Status', required: false },
  { id: 'assigned_to', label: 'Assigned Agent', required: false },
  { id: 'created_at', label: 'Created At', required: false },
  { id: 'actions', label: 'Actions', required: false },
]

const columnVisibility = ref<VisibilityState>({
  ticket_number: true,
  subject: true,
  source: true,
  category: true,
  priority: true,
  status: true,
  assigned_to: true,
  created_at: false, // Hidden initially so exactly 8 columns are shown cleanly without horizontal overflow
  actions: true,
})

const isColumnMenuOpen = ref(false)

const visibleColumnCount = computed(() => {
  return Object.values(columnVisibility.value).filter((v) => v !== false).length
})

function isColumnVisible(colId: string): boolean {
  return columnVisibility.value[colId] !== false
}

function toggleColumn(colId: string) {
  const col = toggleableColumns.find((c) => c.id === colId)
  if (col?.required) return

  const currentlyVisible = isColumnVisible(colId)
  if (!currentlyVisible && visibleColumnCount.value >= 8) {
    alert('Maximum 8 columns allowed to prevent horizontal table overflow. Please uncheck another column first.')
    return
  }

  columnVisibility.value = {
    ...columnVisibility.value,
    [colId]: !currentlyVisible,
  }
}

function resetColumnsToDefault() {
  columnVisibility.value = {
    ticket_number: true,
    subject: true,
    source: true,
    category: true,
    priority: true,
    status: true,
    assigned_to: true,
    created_at: false,
    actions: true,
  }
}

const table = useVueTable({
  get data() {
    return props.tickets ?? []
  },
  get columns() {
    return columns.value
  },
  state: {
    get sorting() {
      return props.sorting
    },
    get columnVisibility() {
      return columnVisibility.value
    },
  },
  onSortingChange: (updaterOrValue) => {
    const newSorting =
      typeof updaterOrValue === 'function'
        ? updaterOrValue(props.sorting)
        : updaterOrValue
    emit('update:sorting', newSorting)
  },
  onColumnVisibilityChange: (updaterOrValue) => {
    columnVisibility.value =
      typeof updaterOrValue === 'function'
        ? updaterOrValue(columnVisibility.value)
        : updaterOrValue
  },
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
  initialState: {
    pagination: {
      pageSize: 10,
    },
  },
})
</script>

<template>
  <div>
    <div
      v-if="!loading && tickets"
      class="pb-3 mb-3 border-b border-border flex items-center justify-between text-xs text-muted-foreground flex-wrap gap-2"
    >
      <div class="flex items-center gap-3">
        <span class="font-medium">
          Showing <strong class="text-foreground font-semibold">{{ tickets.length }}</strong> support ticket{{ tickets.length === 1 ? '' : 's' }}
        </span>
        <span
          v-if="sorting.length > 0"
          class="font-mono text-[11px] text-primary font-semibold bg-primary/5 px-2 py-0.5 rounded-md border border-primary/20"
        >
          Sorted by: {{ sorting[0].id.replace('_', ' ') }} {{ sorting[0].desc ? '↓' : '↑' }}
        </span>
      </div>

      <!-- Column Chooser Button & Menu -->
      <div class="relative inline-block text-left">
        <Button
          variant="outline"
          size="sm"
          class="h-8 px-3 text-xs font-semibold bg-background border-border hover:bg-muted flex items-center gap-2 shadow-2xs cursor-pointer"
          @click.stop="isColumnMenuOpen = !isColumnMenuOpen"
          title="Customize visible table columns"
        >
          <SlidersHorizontal class="size-3.5 text-primary" />
          <span>Columns</span>
          <Badge variant="secondary" class="text-[10px] px-1.5 py-0 font-mono font-bold bg-primary/10 text-primary">
            {{ visibleColumnCount }}/8
          </Badge>
        </Button>

        <!-- Column Visibility Popover -->
        <div
          v-if="isColumnMenuOpen"
          @click.stop
          class="absolute right-0 mt-2 w-64 rounded-xl bg-card border border-border shadow-2xl z-50 p-3.5 animate-in fade-in-80 zoom-in-95"
        >
          <div class="flex items-center justify-between pb-2.5 mb-2.5 border-b border-border">
            <div>
              <h4 class="text-xs font-bold text-foreground">Customize Columns</h4>
              <p class="text-[10px] text-muted-foreground mt-0.5">Select up to 8 columns to show</p>
            </div>
            <button
              type="button"
              @click="isColumnMenuOpen = false"
              class="text-muted-foreground hover:text-foreground text-xs font-bold px-1.5 py-0.5 rounded"
            >
              ✕
            </button>
          </div>

          <div class="space-y-1.5 max-h-60 overflow-y-auto pr-1 text-xs">
            <label
              v-for="col in toggleableColumns.filter(c => user?.isSupreme || c.id !== 'assigned_to')"
              :key="col.id"
              class="flex items-center justify-between p-1.5 rounded-lg hover:bg-muted/60 transition-colors select-none"
              :class="col.required || (!isColumnVisible(col.id) && visibleColumnCount >= 8) ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'"
            >
              <div class="flex items-center gap-2.5">
                <input
                  type="checkbox"
                  :checked="isColumnVisible(col.id)"
                  :disabled="col.required || (!isColumnVisible(col.id) && visibleColumnCount >= 8)"
                  @change="toggleColumn(col.id)"
                  class="size-3.5 rounded border-input text-primary focus:ring-1 focus:ring-primary cursor-pointer disabled:cursor-not-allowed"
                />
                <span class="font-medium text-foreground">{{ col.label }}</span>
              </div>
              <span v-if="col.required" class="text-[9px] uppercase font-bold text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                Required
              </span>
            </label>
          </div>

          <div class="pt-2.5 mt-2.5 border-t border-border flex items-center justify-between gap-2">
            <Button
              variant="ghost"
              size="sm"
              class="h-7 text-[11px] font-semibold text-muted-foreground hover:text-foreground px-2"
              @click="resetColumnsToDefault"
            >
              Reset (7 Cols)
            </Button>
            <span v-if="visibleColumnCount >= 8" class="text-[10px] font-bold text-amber-600 dark:text-amber-400">
              Max 8 reached
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="space-y-4 py-2">
      <div v-for="i in 5" :key="i" class="flex items-center gap-4 p-3">
        <Skeleton class="w-8 h-8 rounded-full shrink-0" />
        <div class="flex-1 space-y-2">
          <Skeleton class="h-4 w-32" />
          <Skeleton class="h-3 w-48" />
        </div>
        <Skeleton class="h-6 w-16" />
        <Skeleton class="h-6 w-20" />
      </div>
    </div>

    <div v-else-if="!tickets || tickets.length === 0" class="text-center py-12">
      <MessageSquare class="size-12 text-muted-foreground/50 mx-auto mb-3" />
      <p class="text-muted-foreground font-medium">No support tickets found</p>
      <p class="text-xs text-muted-foreground/80 mt-1">
        Try adjusting your status, source, or search filters.
      </p>
    </div>

    <div v-else class="overflow-x-auto border rounded-xl bg-card shadow-xs">
      <table class="w-full text-left text-xs border-collapse">
        <thead>
          <tr
            v-for="headerGroup in table.getHeaderGroups()"
            :key="headerGroup.id"
            class="border-b border-border bg-muted/30"
          >
            <th
              v-for="header in headerGroup.headers"
              :key="header.id"
              class="py-3 px-2.5 sm:px-3 font-bold text-muted-foreground uppercase tracking-wider text-[11px] select-none transition-colors whitespace-nowrap"
              :class="[
                header.id === 'actions' ? 'text-right' : 'text-left',
                header.column.getCanSort()
                  ? 'cursor-pointer hover:text-foreground hover:bg-muted/60 group'
                  : '',
              ]"
              @click="header.column.getToggleSortingHandler()?.($event)"
            >
              <div
                class="flex items-center gap-1.5"
                :class="header.id === 'actions' ? 'justify-end' : 'justify-start'"
              >
                <span>{{ header.column.columnDef.header }}</span>
                <template v-if="header.column.getCanSort()">
                  <ArrowUp
                    v-if="header.column.getIsSorted() === 'asc'"
                    class="size-3.5 shrink-0 text-primary"
                  />
                  <ArrowDown
                    v-else-if="header.column.getIsSorted() === 'desc'"
                    class="size-3.5 shrink-0 text-primary"
                  />
                  <ArrowUpDown
                    v-else
                    class="size-3.5 shrink-0 opacity-30 group-hover:opacity-100 transition-opacity"
                  />
                </template>
              </div>
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border/60">
          <tr
            v-for="row in table.getRowModel().rows"
            :key="row.id"
            class="hover:bg-muted/40 transition-colors group"
          >
            <!-- Ticket # -->
            <td v-if="isColumnVisible('ticket_number')" class="py-3.5 px-2.5 sm:px-3 font-mono font-bold text-foreground whitespace-nowrap">
              {{ row.original.ticket_number }}
            </td>
            <!-- Subject -->
            <td
              v-if="isColumnVisible('subject')"
              class="py-3.5 px-2.5 sm:px-3 font-bold text-foreground max-w-[220px] sm:max-w-[320px] truncate hover:text-primary cursor-pointer transition-colors"
              @click="router.push(`/admin/support/${row.original.id}`)"
              title="Click to view ticket details in separate page"
            >
              {{ row.original.subject }}
            </td>
            <!-- Source -->
            <td v-if="isColumnVisible('source')" class="py-3.5 px-2.5 sm:px-3 whitespace-nowrap">
              <Badge
                v-if="row.original.source === 'email'"
                variant="outline"
                class="bg-blue-50/50 text-blue-700 border-blue-200/80 font-semibold text-xs flex items-center gap-1.5 w-fit"
              >
                <Mail class="size-3 text-blue-600" /> Email
              </Badge>
              <Badge
                v-else
                variant="outline"
                class="bg-purple-50/50 text-purple-700 border-purple-200/80 font-semibold text-xs flex items-center gap-1.5 w-fit"
              >
                <Globe class="size-3 text-purple-600" /> Web
              </Badge>
            </td>
            <!-- Category (Interactive Inline Dropdown) -->
            <td v-if="isColumnVisible('category')" class="py-2.5 px-2.5 sm:px-3 whitespace-nowrap" @click.stop>
              <select
                aria-label="Change category"
                :value="row.original.category || 'general'"
                @change="handleRowCategory(row.original, $event)"
                :class="[
                  'h-7 px-2 rounded-md text-[11px] font-bold border capitalize shadow-2xs focus:outline-none focus:ring-2 focus:ring-primary/40 cursor-pointer transition-colors max-w-[130px] truncate',
                  getCategoryBadgeClass(row.original.category || 'general'),
                ]"
                title="Change category right from the table"
              >
                <option value="general">General</option>
                <option value="logistics_breakdown">Logistics Breakdown</option>
                <option value="billing_payment">Billing & Payment</option>
                <option value="verification_kyc">Verification & KYC</option>
                <option value="shipment_tracking">Shipment Tracking</option>
                <option value="account_access">Account Access</option>
                <option value="verification">Verification (Legacy)</option>
                <option value="billing">Billing (Legacy)</option>
                <option value="shipments">Shipments (Legacy)</option>
                <option value="technical">Technical (Legacy)</option>
                <option value="account">Account (Legacy)</option>
              </select>
            </td>
            <!-- Priority -->
            <td v-if="isColumnVisible('priority')" class="py-3.5 px-2.5 sm:px-3 whitespace-nowrap">
              <Badge
                :class="[
                  'text-[10px] px-2 py-0.5 uppercase border capitalize font-bold',
                  getPriorityBadgeClass(row.original.priority),
                ]"
              >
                {{ row.original.priority }}
              </Badge>
            </td>
            <!-- Status (Interactive Inline Dropdown) -->
            <td v-if="isColumnVisible('status')" class="py-2.5 px-2.5 sm:px-3 whitespace-nowrap" @click.stop>
              <select
                aria-label="Change status"
                :value="row.original.status"
                @change="handleRowStatus(row.original, $event)"
                :class="[
                  'h-7 px-2 rounded-md text-[11px] font-bold border capitalize shadow-2xs focus:outline-none focus:ring-2 focus:ring-primary/40 cursor-pointer transition-colors',
                  getStatusBadgeClass(row.original.status),
                ]"
                title="Change status right from the table"
              >
                <option value="new">New</option>
                <option value="processing">Processing</option>
                <option value="open">Open</option>
                <option value="in_progress">In Progress</option>
                <option value="resolved">Resolved</option>
                <option value="closed">Closed</option>
              </select>
            </td>
            <!-- Assigned Agent (Interactive Inline Assignment) -->
            <td v-if="user?.isSupreme && isColumnVisible('assigned_to')" class="py-2.5 px-2.5 sm:px-3 whitespace-nowrap" @click.stop>
              <div class="relative flex items-center">
                <UserCheck
                  v-if="parseAssignedAgent(row.original.admin_notes).agentName"
                  class="absolute left-2.5 size-3.5 text-indigo-600 dark:text-indigo-400 pointer-events-none z-10"
                />
                <select
                  aria-label="Change assigned agent"
                  :value="parseAssignedAgent(row.original.admin_notes).agentId || ''"
                  @change="handleRowAssign(row.original, $event)"
                  class="h-8 pr-6 rounded-lg text-xs font-semibold border shadow-2xs focus:outline-none focus:ring-2 focus:ring-primary/40 transition-colors cursor-pointer max-w-[185px] truncate"
                  :class="parseAssignedAgent(row.original.admin_notes).agentName ? 'bg-indigo-500/15 text-indigo-700 dark:text-indigo-300 border-indigo-500/30 pl-7 hover:bg-indigo-500/25' : 'bg-muted/40 text-muted-foreground border-border hover:bg-muted pl-2.5'"
                  title="Change assigned agent right from the table"
                >
                  <option value="">+ Assign Agent (Unassigned)</option>
                  <option v-for="agent in agents.filter(a => a.id !== '')" :key="agent.id" :value="agent.id">
                    {{ agent.name.split(' (')[0] }}
                  </option>
                </select>
              </div>
            </td>
            <!-- Created At -->
            <td
              v-if="isColumnVisible('created_at')"
              class="py-3.5 px-2.5 sm:px-3 text-xs text-muted-foreground font-mono whitespace-nowrap"
            >
              {{ new Date(row.original.created_at).toLocaleDateString() }}
            </td>
            <!-- Actions -->
            <td v-if="isColumnVisible('actions')" class="py-3 px-2.5 sm:px-3 text-right">
              <div class="flex items-center justify-end gap-1.5 flex-wrap min-w-[130px]">
                <Button
                  variant="outline"
                  size="sm"
                  class="h-7 px-2.5 text-[11px] font-bold shadow-2xs"
                  @click="router.push(`/admin/support/${row.original.id}`)"
                >
                  Inspect
                </Button>
                <Button
                  v-if="
                    row.original.status !== 'resolved' &&
                    row.original.status !== 'closed'
                  "
                  size="sm"
                  class="h-7 px-2.5 text-[11px] font-bold bg-primary hover:bg-primary/90 text-primary-foreground shadow-2xs"
                  @click="emit('resolve', row.original)"
                >
                  Resolve
                </Button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination Controls -->
      <div
        v-if="table.getPageCount() > 1 || tickets.length > 10"
        class="flex flex-col sm:flex-row items-center justify-between gap-3 px-4 py-3 bg-muted/20 border-t border-border text-xs"
      >
        <div class="flex items-center gap-2 text-muted-foreground font-medium">
          <span>Rows per page:</span>
          <select
            :value="table.getState().pagination.pageSize"
            @change="table.setPageSize(Number(($event.target as HTMLSelectElement).value))"
            class="h-7 px-2 bg-background border border-input rounded text-xs font-semibold text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option :value="10">10</option>
            <option :value="15">15</option>
            <option :value="25">25</option>
            <option :value="50">50</option>
            <option :value="100">100</option>
          </select>
          <span class="ml-2">
            Showing {{ table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1 }} -
            {{ Math.min((table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize, tickets.length) }}
            of {{ tickets.length }}
          </span>
        </div>

        <div class="flex items-center gap-3">
          <span class="text-xs font-semibold text-foreground">
            Page {{ table.getState().pagination.pageIndex + 1 }} of {{ table.getPageCount() }}
          </span>
          <div class="flex items-center gap-1">
            <Button
              variant="outline"
              size="sm"
              class="h-7 w-7 p-0"
              :disabled="!table.getCanPreviousPage()"
              @click="table.setPageIndex(0)"
              title="First Page"
            >
              <ChevronsLeft class="size-3.5" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              class="h-7 w-7 p-0"
              :disabled="!table.getCanPreviousPage()"
              @click="table.previousPage()"
              title="Previous Page"
            >
              <ChevronLeft class="size-3.5" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              class="h-7 w-7 p-0"
              :disabled="!table.getCanNextPage()"
              @click="table.nextPage()"
              title="Next Page"
            >
              <ChevronRight class="size-3.5" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              class="h-7 w-7 p-0"
              :disabled="!table.getCanNextPage()"
              @click="table.setPageIndex(table.getPageCount() - 1)"
              title="Last Page"
            >
              <ChevronsRight class="size-3.5" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
