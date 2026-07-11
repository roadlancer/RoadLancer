<script lang="ts" setup>
import { computed } from 'vue'
import {
  useVueTable,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  type SortingState,
  type ColumnDef,
} from '@tanstack/vue-table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Shield,
  LoaderCircle,
  ArrowUp,
  ArrowDown,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from '@lucide/vue'

const props = defineProps<{
  agents: any[]
  loading?: boolean
  isSupreme?: boolean
  deactivatePending?: boolean
  activatePending?: boolean
  sorting?: SortingState
}>()

const emit = defineEmits<{
  (e: 'deactivate', userId: string): void
  (e: 'activate', userId: string): void
  (e: 'update:sorting', sorting: SortingState): void
}>()

const columns = computed<ColumnDef<any, any>[]>(() => [
  {
    accessorKey: 'name',
    header: 'Agent',
    enableSorting: true,
  },
  {
    accessorKey: 'role',
    header: 'Role',
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
    return props.agents ?? []
  },
  columns: columns.value,
  state: {
    get sorting() {
      return props.sorting ?? []
    },
  },
  onSortingChange: (updaterOrValue) => {
    const nextSorting =
      typeof updaterOrValue === 'function'
        ? updaterOrValue(props.sorting ?? [])
        : updaterOrValue
    emit('update:sorting', nextSorting)
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
  <div v-if="loading && (!agents || agents.length === 0)" class="space-y-3 p-4">
    <div v-for="i in 4" :key="i" class="flex items-center justify-between p-3.5 border rounded-xl bg-card/40 animate-pulse">
      <div class="flex items-center gap-3 w-1/3">
        <Skeleton class="w-9 h-9 rounded-full shrink-0" />
        <div class="space-y-1.5 flex-1 min-w-0">
          <Skeleton class="h-4 w-32" />
          <Skeleton class="h-3 w-48" />
        </div>
      </div>
      <Skeleton class="h-6 w-20 rounded-md" />
      <Skeleton class="h-8 w-24 rounded-lg" />
    </div>
  </div>

  <div v-else-if="!agents || agents.length === 0" class="text-center py-16 px-4 border rounded-2xl bg-card/20">
    <div class="w-16 h-16 rounded-2xl bg-muted/60 flex items-center justify-center mx-auto mb-4 text-muted-foreground">
      <Shield class="size-8 opacity-60" />
    </div>
    <h3 class="text-base font-bold text-foreground mb-1">No agents found</h3>
    <p class="text-xs text-muted-foreground max-w-sm mx-auto">
      There are no admin agents in the system.
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
              header.column.getCanSort() ? 'cursor-pointer hover:text-foreground hover:bg-muted/60 group' : '',
            ]"
            @click="header.column.getToggleSortingHandler()?.($event)"
          >
            <div class="flex items-center gap-1.5" :class="header.id === 'actions' ? 'justify-end' : 'justify-start'">
              <span>{{ header.column.columnDef.header }}</span>
              <template v-if="header.column.getCanSort()">
                <ArrowUp v-if="header.column.getIsSorted() === 'asc'" class="size-3.5 shrink-0 text-primary" />
                <ArrowDown v-else-if="header.column.getIsSorted() === 'desc'" class="size-3.5 shrink-0 text-primary" />
                <ArrowUpDown v-else class="size-3.5 shrink-0 opacity-30 group-hover:opacity-100 transition-opacity" />
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
          <td class="py-3.5 px-2.5 sm:px-3 max-w-[200px]">
            <div class="min-w-0">
              <p class="font-bold text-foreground text-sm truncate group-hover:text-primary transition-colors">
                {{ row.original.name }}
              </p>
              <p class="text-xs text-muted-foreground truncate font-mono">
                {{ row.original.email }}
              </p>
            </div>
          </td>

          <td class="py-3.5 px-2.5 sm:px-3 whitespace-nowrap">
            <Badge variant="secondary" class="capitalize font-bold text-xs px-2.5 py-0.5">
              {{ row.original.isSupreme ? 'Supreme Admin' : 'Admin' }}
            </Badge>
          </td>

          <td class="py-3.5 px-2.5 sm:px-3 whitespace-nowrap">
            <Badge :variant="row.original.suspended ? 'destructive' : 'default'" class="font-semibold text-[11px]">
              {{ row.original.suspended ? 'Deactivated' : 'Active' }}
            </Badge>
          </td>

          <td class="py-3.5 px-2.5 sm:px-3 font-mono text-muted-foreground text-xs whitespace-nowrap">
            {{ row.original.created_at ? new Date(row.original.created_at).toLocaleDateString() : '—' }}
          </td>

          <td class="py-3 px-2.5 sm:px-3 text-right">
            <div v-if="isSupreme" class="flex items-center justify-end gap-1.5 min-w-[130px]">
              <Button
                v-if="!row.original.suspended && !row.original.isSupreme"
                variant="destructive"
                size="sm"
                class="h-7 px-2.5 text-[11px] font-bold shadow-2xs"
                :disabled="deactivatePending"
                @click="emit('deactivate', row.original.id)"
              >
                <LoaderCircle v-if="deactivatePending" class="size-3 animate-spin mr-1" />
                Deactivate
              </Button>
              <Button
                v-else-if="row.original.suspended && !row.original.isSupreme"
                variant="outline"
                size="sm"
                class="h-7 px-2.5 text-[11px] font-bold shadow-2xs"
                :disabled="activatePending"
                @click="emit('activate', row.original.id)"
              >
                <LoaderCircle v-if="activatePending" class="size-3 animate-spin mr-1" />
                Activate
              </Button>
              <span v-else-if="row.original.isSupreme" class="text-xs text-muted-foreground italic">
                Supreme
              </span>
            </div>
            <div v-else class="min-w-[130px] text-right">
              <span class="text-xs text-muted-foreground italic">—</span>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <div
      v-if="table.getPageCount() > 1 || agents.length > 10"
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
        </select>
        <span class="ml-2">
          Showing {{ table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1 }} -
          {{ Math.min((table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize, agents.length) }}
          of {{ agents.length }}
        </span>
      </div>

      <div class="flex items-center gap-3">
        <span class="text-xs font-semibold text-foreground">
          Page {{ table.getState().pagination.pageIndex + 1 }} of {{ table.getPageCount() }}
        </span>
        <div class="flex items-center gap-1">
          <Button variant="outline" size="sm" class="h-7 w-7 p-0" :disabled="!table.getCanPreviousPage()" @click="table.setPageIndex(0)">
            <ChevronsLeft class="size-3.5" />
          </Button>
          <Button variant="outline" size="sm" class="h-7 w-7 p-0" :disabled="!table.getCanPreviousPage()" @click="table.previousPage()">
            <ChevronLeft class="size-3.5" />
          </Button>
          <Button variant="outline" size="sm" class="h-7 w-7 p-0" :disabled="!table.getCanNextPage()" @click="table.nextPage()">
            <ChevronRight class="size-3.5" />
          </Button>
          <Button variant="outline" size="sm" class="h-7 w-7 p-0" :disabled="!table.getCanNextPage()" @click="table.setPageIndex(table.getPageCount() - 1)">
            <ChevronsRight class="size-3.5" />
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>
