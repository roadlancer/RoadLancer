import { ref, computed } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import api from '@/lib/api'
import { useAuth } from './useAuth'

export interface SupportTicket {
  id: string
  ticket_number: string
  sender_email: string
  sender_name: string | null
  subject: string
  message: string
  status: 'open' | 'in_progress' | 'resolved' | 'closed'
  priority: 'low' | 'normal' | 'high' | 'urgent'
  source: 'email' | 'web' | 'profile_edit'
  user_id: string | null
  user: {
    id: string
    name: string
    email: string
    role: string
    phone: string | null
  } | null
  admin_notes: string | null
  created_at: string
  updated_at: string
}

export function useMyTickets() {
  const { user } = useAuth()
  const searchQuery = ref('')
  const statusFilter = ref('all')
  const sortBy = ref('newest')
  const sortField = ref<string | null>(null)
  const sortOrder = ref<'asc' | 'desc'>('desc')

  const queryKey = computed(() => [
    'my-support-tickets',
    user.value?.id,
    {
      search: searchQuery.value,
      status: statusFilter.value,
      sort_by: sortBy.value,
      sort_field: sortField.value,
      sort_order: sortOrder.value,
    },
  ])

  const query = useQuery({
    queryKey,
    queryFn: async () => {
      const params: Record<string, string> = {}
      // When sort_field is set (TanStack column click), use it; otherwise fall back to legacy sort_by
      if (sortField.value) {
        params.sort_field = sortField.value
        params.sort_order = sortOrder.value
      } else {
        params.sort_by = sortBy.value
      }
      if (statusFilter.value !== 'all') params.status = statusFilter.value
      if (searchQuery.value) params.search = searchQuery.value
      const { data } = await api.get('/support/tickets/my', { params })
      return data as SupportTicket[]
    },
    enabled: computed(() => !!user.value),
  })

  return {
    data: query.data,
    tickets: query.data,
    isLoading: query.isLoading,
    refetch: query.refetch,
    searchQuery,
    statusFilter,
    sortBy,
    sortField,
    sortOrder,
  }
}

export function useAdminTickets() {
  const queryClient = useQueryClient()
  const searchQuery = ref('')
  const statusFilter = ref('all')
  const sourceFilter = ref('all')
  const sortBy = ref('newest')
  const sortField = ref<string | null>(null)
  const sortOrder = ref<'asc' | 'desc'>('desc')

  const queryKey = computed(() => [
    'admin-support-tickets',
    {
      search: searchQuery.value,
      status: statusFilter.value,
      source: sourceFilter.value,
      sort_by: sortBy.value,
      sort_field: sortField.value,
      sort_order: sortOrder.value,
    },
  ])

  const query = useQuery({
    queryKey,
    queryFn: async () => {
      const params: Record<string, string> = {}
      // When sort_field is set (TanStack column click), use it; otherwise fall back to legacy sort_by
      if (sortField.value) {
        params.sort_field = sortField.value
        params.sort_order = sortOrder.value
      } else {
        params.sort_by = sortBy.value
      }
      if (statusFilter.value !== 'all') params.status = statusFilter.value
      if (sourceFilter.value !== 'all') params.source = sourceFilter.value
      if (searchQuery.value) params.search = searchQuery.value
      const { data } = await api.get('/support/admin/list', { params })
      return data as SupportTicket[]
    },
  })

  const countsQuery = useQuery({
    queryKey: ['admin-support-counts'],
    queryFn: async () => {
      const { data } = await api.get('/support/admin/count')
      return data as {
        total: number
        open: number
        in_progress: number
        resolved: number
        closed: number
        inbound_email: number
        web: number
      }
    },
  })

  const updateStatusMutation = useMutation({
    mutationFn: async ({
      id,
      status,
      adminNotes,
      priority,
    }: {
      id: string
      status: string
      adminNotes?: string
      priority?: string
    }) => {
      const { data } = await api.put(`/support/admin/${id}/status`, {
        status,
        admin_notes: adminNotes,
        priority,
      })
      return data as SupportTicket
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-support-tickets'] })
      queryClient.invalidateQueries({ queryKey: ['admin-support-counts'] })
      queryClient.invalidateQueries({ queryKey: ['my-support-tickets'] })
    },
  })

  return {
    tickets: query.data,
    isLoading: query.isLoading,
    refetch: query.refetch,
    counts: countsQuery.data,
    isLoadingCounts: countsQuery.isLoading,
    searchQuery,
    statusFilter,
    sourceFilter,
    sortBy,
    sortField,
    sortOrder,
    updateStatus: updateStatusMutation.mutateAsync,
    isUpdating: updateStatusMutation.isPending,
  }
}

export function useSupportMutations() {
  const queryClient = useQueryClient()

  const simulateEmailMutation = useMutation({
    mutationFn: async (payload: {
      from_email: string
      from_name?: string
      subject: string
      body: string
      priority?: string
      source?: string
      secret?: string
    }) => {
      const secret = payload.secret || import.meta.env.VITE_SUPPORT_WEBHOOK_SECRET || "roadlancer-webhook-secret-2026"
      const { data } = await api.post(
        '/support/inbound-email',
        { ...payload, secret },
        { headers: { 'x-webhook-secret': secret } }
      )
      return data as {
        success: boolean
        ticket_number: string
        ticket: SupportTicket
        message: string
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-support-tickets'] })
      queryClient.invalidateQueries({ queryKey: ['admin-support-tickets'] })
      queryClient.invalidateQueries({ queryKey: ['admin-support-counts'] })
    },
  })

  const createTicketMutation = useMutation({
    mutationFn: async (payload: {
      subject: string
      message: string
      priority?: string
      source?: string
    }) => {
      const { data } = await api.post('/support/tickets', payload)
      return data as SupportTicket
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-support-tickets'] })
      queryClient.invalidateQueries({ queryKey: ['admin-support-tickets'] })
      queryClient.invalidateQueries({ queryKey: ['admin-support-counts'] })
    },
  })

  return {
    simulateEmail: simulateEmailMutation.mutateAsync,
    isSimulatingEmail: simulateEmailMutation.isPending,
    createTicket: createTicketMutation.mutateAsync,
    isCreatingTicket: createTicketMutation.isPending,
  }
}
