<script lang="ts" setup>
import { computed } from 'vue'
import {
  useVueTable,
  getCoreRowModel,
  getSortedRowModel,
  type SortingState,
  type ColumnDef,
} from '@tanstack/vue-table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Users,
  LoaderCircle,
  ArrowUp,
  ArrowDown,
  ArrowUpDown,
} from '@lucide/vue'

const props = defineProps<{
  users: any[]
  loading?: boolean
  suspendPending?: boolean
  sorting?: SortingState
}>()

const emit = defineEmits<{
  (e: 'suspend', user: any): void
  (e: 'unsuspend', userId: string): void
  (e: 'viewVerification', user: any): void
  (e: 'update:sorting', sorting: SortingState): void
}>()

const columns = computed<ColumnDef<any, any>[]>(() => [
  {
    accessorKey: 'name',
    header: 'User',
    enableSorting: true,
  },
  {
    accessorKey: 'role',
    header: 'Role',
    enableSorting: true,
  },
  {
    accessorKey: 'phone',
    header: 'Phone',
    enableSorting: false,
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
    return props.users ?? []
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
})
</script>

<template>
  <div v-if="loading && (!users || users.length === 0)" class="space-y-3 p-4">
    <div v-for="i in 6" :key="i" class="flex items-center justify-between p-3.5 border rounded-xl bg-card/40 animate-pulse">
      <div class="flex items-center gap-3 w-1/3">
        <Skeleton class="w-9 h-9 rounded-full shrink-0" />
        <div class="space-y-1.5 flex-1 min-w-0">
          <Skeleton class="h-4 w-32" />
          <Skeleton class="h-3 w-48" />
        </div>
      </div>
      <Skeleton class="h-6 w-20 rounded-md" />
      <Skeleton class="h-6 w-24 rounded-md" />
      <Skeleton class="h-8 w-24 rounded-lg" />
    </div>
  </div>

  <div v-else-if="!users || users.length === 0" class="text-center py-16 px-4 border rounded-2xl bg-card/20">
    <div class="w-16 h-16 rounded-2xl bg-muted/60 flex items-center justify-center mx-auto mb-4 text-muted-foreground">
      <Users class="size-8 opacity-60" />
    </div>
    <h3 class="text-base font-bold text-foreground mb-1">No users found</h3>
    <p class="text-xs text-muted-foreground max-w-sm mx-auto">
      There are no users matching your filter or search query right now.
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
          <!-- User Info -->
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

          <!-- Role -->
          <td class="py-3.5 px-2.5 sm:px-3 whitespace-nowrap">
            <Badge variant="secondary" class="capitalize font-bold text-xs px-2.5 py-0.5">
              {{ row.original.role }}
            </Badge>
          </td>

          <!-- Phone -->
          <td class="py-3.5 px-2.5 sm:px-3 font-mono text-muted-foreground text-xs whitespace-nowrap">
            {{ row.original.phone || '—' }}
          </td>

          <!-- Status -->
          <td class="py-3.5 px-2.5 sm:px-3 whitespace-nowrap">
            <div class="flex flex-wrap items-center gap-1.5">
              <Badge :variant="row.original.suspended ? 'destructive' : 'default'" class="font-semibold text-[11px]">
                {{ row.original.suspended ? 'Suspended' : 'Active' }}
              </Badge>
              <Badge v-if="row.original.verification_status === 'approved'" class="bg-green-100 text-green-800 border border-green-300 dark:bg-green-950/40 dark:text-green-300 font-semibold text-[11px]">
                Verified
              </Badge>
              <Badge v-else-if="row.original.verification_status === 'pending'" class="bg-amber-100 text-amber-800 border border-amber-300 dark:bg-amber-950/40 dark:text-amber-300 font-semibold text-[11px]">
                Pending
              </Badge>
              <Badge v-else-if="row.original.verification_status === 'rejected'" class="bg-red-100 text-red-800 border border-red-300 dark:bg-red-950/40 dark:text-red-300 font-semibold text-[11px]">
                Rejected
              </Badge>
            </div>
          </td>

          <!-- Created At -->
          <td class="py-3.5 px-2.5 sm:px-3 font-mono text-muted-foreground text-xs whitespace-nowrap">
            {{ row.original.created_at ? new Date(row.original.created_at).toLocaleDateString() : '—' }}
          </td>

          <!-- Actions -->
          <td class="py-3 px-2.5 sm:px-3 text-right">
            <div class="flex items-center justify-end gap-1.5 flex-wrap min-w-[130px]">
              <Button
                v-if="row.original.verification_status === 'pending'"
                variant="outline"
                size="sm"
                class="border-amber-500/30 text-amber-600 dark:text-amber-400 hover:bg-amber-500/10 font-bold h-7 px-2.5 text-[11px] shadow-2xs"
                @click="emit('viewVerification', row.original)"
              >
                Review Docs
              </Button>
              <Button
                v-if="row.original.role !== 'admin' && !row.original.suspended"
                variant="destructive"
                size="sm"
                class="h-7 px-2.5 text-[11px] font-bold shadow-2xs"
                @click="emit('suspend', row.original)"
              >
                Suspend
              </Button>
              <Button
                v-else-if="row.original.role !== 'admin' && row.original.suspended"
                variant="outline"
                size="sm"
                class="h-7 px-2.5 text-[11px] font-bold shadow-2xs"
                @click="emit('unsuspend', row.original.id)"
              >
                Unsuspend
              </Button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
