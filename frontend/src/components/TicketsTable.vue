<script lang="ts" setup>
import { computed } from 'vue'
import {
  useVueTable,
  getCoreRowModel,
  type SortingState,
  type ColumnDef,
} from '@tanstack/vue-table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import type { SupportTicket } from '@/composables/useSupportTickets'
import {
  MessageSquare,
  Mail,
  Globe,
  Phone,
  ArrowUp,
  ArrowDown,
  ArrowUpDown,
} from '@lucide/vue'

const props = defineProps<{
  tickets: SupportTicket[]
  loading?: boolean
  sorting: SortingState
}>()

const emit = defineEmits<{
  (e: 'inspect', ticket: SupportTicket): void
  (e: 'resolve', ticket: SupportTicket): void
  (e: 'update:sorting', sorting: SortingState): void
}>()

function getStatusBadgeClass(status: string) {
  switch (status) {
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

const columns = computed<ColumnDef<SupportTicket, any>[]>(() => [
  {
    accessorKey: 'ticket_number',
    header: 'Ticket #',
    enableSorting: true,
  },
  {
    accessorKey: 'sender_email',
    header: 'Sender & Account',
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
    accessorKey: 'priority',
    header: 'Priority',
    enableSorting: true,
  },
  {
    accessorKey: 'status',
    header: 'Status',
    enableSorting: true,
  },
  {
    accessorKey: 'created_at',
    header: 'Created At',
    enableSorting: true,
  },
  {
    id: 'actions',
    header: 'Actions',
    enableSorting: false,
  },
])

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
  },
  onSortingChange: (updaterOrValue) => {
    const newSorting =
      typeof updaterOrValue === 'function'
        ? updaterOrValue(props.sorting)
        : updaterOrValue
    emit('update:sorting', newSorting)
  },
  getCoreRowModel: getCoreRowModel(),
  manualSorting: true,
})
</script>

<template>
  <div>
    <div
      v-if="!loading && tickets && tickets.length > 0"
      class="pb-3 mb-3 border-b border-border flex items-center justify-between text-xs text-muted-foreground"
    >
      <span class="font-medium"
        >Showing
        <strong class="text-foreground font-semibold">{{ tickets.length }}</strong>
        support ticket{{ tickets.length === 1 ? '' : 's' }}</span
      >
      <span
        v-if="sorting.length > 0"
        class="font-mono text-[11px] text-primary font-semibold bg-primary/5 px-2.5 py-1 rounded-md border border-primary/20"
      >
        Sorted by: {{ sorting[0].id.replace('_', ' ') }}
        {{ sorting[0].desc ? '↓' : '↑' }}
      </span>
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
            <td class="py-3.5 px-2.5 sm:px-3 font-mono font-bold text-foreground whitespace-nowrap">
              {{ row.original.ticket_number }}
            </td>
            <!-- Sender & Account -->
            <td class="py-3.5 px-2.5 sm:px-3 max-w-[200px]">
              <div>
                <p class="font-bold text-foreground text-sm leading-tight group-hover:text-primary transition-colors truncate">
                  {{ row.original.sender_name || row.original.sender_email }}
                </p>
                <p class="text-xs font-mono text-muted-foreground mt-0.5 truncate">
                  {{ row.original.sender_email }}
                </p>
                <div
                  v-if="row.original.user"
                  class="mt-1.5 flex items-center gap-1.5 flex-wrap"
                >
                  <Badge
                    variant="secondary"
                    class="text-[10px] px-1.5 py-0 uppercase font-semibold"
                  >
                    {{ row.original.user.role }}
                  </Badge>
                  <span
                    v-if="row.original.user.phone"
                    class="text-[11px] text-muted-foreground font-mono flex items-center gap-1 truncate"
                  >
                    <Phone class="size-3 text-muted-foreground shrink-0" />
                    {{ row.original.user.phone }}
                  </span>
                </div>
              </div>
            </td>
            <!-- Subject -->
            <td class="py-3.5 px-2.5 sm:px-3 font-bold text-foreground max-w-[180px] sm:max-w-[220px] truncate">
              {{ row.original.subject }}
            </td>
            <!-- Source -->
            <td class="py-3.5 px-2.5 sm:px-3 whitespace-nowrap">
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
            <!-- Priority -->
            <td class="py-3.5 px-2.5 sm:px-3 whitespace-nowrap">
              <Badge
                :class="[
                  'text-[10px] px-2 py-0.5 uppercase border capitalize font-bold',
                  getPriorityBadgeClass(row.original.priority),
                ]"
              >
                {{ row.original.priority }}
              </Badge>
            </td>
            <!-- Status -->
            <td class="py-3.5 px-2.5 sm:px-3 whitespace-nowrap">
              <Badge
                :class="[
                  'text-xs font-bold px-2.5 py-0.5 border capitalize',
                  getStatusBadgeClass(row.original.status),
                ]"
              >
                {{ row.original.status.replace('_', ' ') }}
              </Badge>
            </td>
            <!-- Created At -->
            <td
              class="py-3.5 px-2.5 sm:px-3 text-xs text-muted-foreground font-mono whitespace-nowrap"
            >
              {{ new Date(row.original.created_at).toLocaleDateString() }}
            </td>
            <!-- Actions -->
            <td class="py-3 px-2.5 sm:px-3 text-right">
              <div class="flex items-center justify-end gap-1.5 flex-wrap min-w-[130px]">
                <Button
                  variant="outline"
                  size="sm"
                  class="h-7 px-2.5 text-[11px] font-bold shadow-2xs"
                  @click="emit('inspect', row.original)"
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
    </div>
  </div>
</template>
