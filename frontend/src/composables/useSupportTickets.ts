import { ref, computed } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import api from '@/lib/api'
import { useAuth } from './useAuth'
import { useAdminUsers } from './useAdminUsers'
import { sanitize, sanitizeText } from '@/lib/sanitize'

export interface PolishReplyRequest {
  draft: string
  message?: string
}

export interface PolishReplyResponse {
  polished: string
  success: boolean
  source?: string
  usage?: { promptTokens: number; completionTokens: number; totalTokens: number }
}

export interface SupportTicketReply {
  id: string
  ticket_id: string
  sender_name: string
  sender_role: 'admin' | 'user' | string
  sender_type: 'agent' | 'customer' | string
  message: string
  created_at: string
}

export interface SupportTicket {
  id: string
  ticket_number: string
  sender_email: string
  sender_name: string | null
  subject: string
  message: string
  category?: string
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
  replies?: SupportTicketReply[]
}

export interface AssignedAgentInfo {
  agentId: string | null
  agentName: string | null
  cleanNotes: string
}

export interface SupportAgent {
  id: string
  name: string
}

export function parseAssignedAgent(notes: string | null | undefined): AssignedAgentInfo {
  if (!notes) {
    return { agentId: null, agentName: null, cleanNotes: '' }
  }
  const match = notes.match(/^\[ASSIGNED_TO:(.*?)\|(.*?)\]\r?\n?\s*(.*)$/s)
  if (match) {
    return {
      agentId: match[1] || null,
      agentName: match[2] || null,
      cleanNotes: (match[3] || '').trim(),
    }
  }
  return { agentId: null, agentName: null, cleanNotes: notes.trim() }
}

export function formatAssignedAgentNotes(agentId: string | null, agentName: string | null, cleanNotes: string): string | undefined {
  const trimmed = cleanNotes.trim()
  if (!agentId || !agentName) {
    return trimmed || undefined
  }
  return trimmed ? `[ASSIGNED_TO:${agentId}|${agentName}]\n${trimmed}` : `[ASSIGNED_TO:${agentId}|${agentName}]`
}

export function sanitizeTicket(ticket: SupportTicket): SupportTicket {
  if (!ticket) return ticket
  return {
    ...ticket,
    subject: sanitizeText(ticket.subject),
    message: sanitize(ticket.message),
    sender_name: ticket.sender_name ? sanitizeText(ticket.sender_name) : null,
    admin_notes: ticket.admin_notes ? sanitize(ticket.admin_notes) : null,
    replies: ticket.replies ? ticket.replies.map((r) => ({
      ...r,
      sender_name: r.sender_name ? sanitizeText(r.sender_name) : null,
      message: sanitize(r.message),
    })) : []
  }
}

export function useSupportAgents() {
  const { data: adminUsers } = useAdminUsers()
  return computed<SupportAgent[]>(() => {
    const base: SupportAgent[] = [
      { id: '', name: 'Unassigned (No Agent)' },
    ]
    if (adminUsers.value) {
      const dbAdmins = adminUsers.value
        .filter((u) => u.role === 'admin' && !u.suspended)
        .map((u) => ({ id: u.id, name: `${u.name} (${u.email})` }))
      return [...base, ...dbAdmins]
    }
    return base
  })
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
      return (data as SupportTicket[]).map(sanitizeTicket)
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
      return (data as SupportTicket[]).map(sanitizeTicket)
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
      category,
      adminNotes,
      priority,
    }: {
      id: string
      status?: string
      category?: string
      adminNotes?: string
      priority?: string
    }) => {
      const { data } = await api.put(`/support/admin/${id}/status`, {
        status,
        category,
        admin_notes: adminNotes ? sanitize(adminNotes) : undefined,
        priority,
      })
      return sanitizeTicket(data as SupportTicket)
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
      return {
        ...data,
        ticket: sanitizeTicket(data.ticket)
      } as {
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
      const { data } = await api.post('/support/tickets', {
        ...payload,
        subject: sanitizeText(payload.subject),
        message: sanitize(payload.message),
      })
      return sanitizeTicket(data as SupportTicket)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-support-tickets'] })
      queryClient.invalidateQueries({ queryKey: ['admin-support-tickets'] })
      queryClient.invalidateQueries({ queryKey: ['admin-support-counts'] })
    },
  })

  const replyTicketMutation = useMutation({
    mutationFn: async ({ ticketId, message }: { ticketId: string; message: string }) => {
      const { data } = await api.post(`/support/tickets/${ticketId}/replies`, { message: sanitize(message) })
      return sanitizeTicket(data as SupportTicket)
    },
    onSuccess: (data, variables) => {
      queryClient.setQueryData(['admin-support-ticket', variables.ticketId], data)
      queryClient.invalidateQueries({ queryKey: ['my-support-tickets'] })
      queryClient.invalidateQueries({ queryKey: ['admin-support-tickets'] })
    },
  })

  return {
    simulateEmail: simulateEmailMutation.mutateAsync,
    isSimulatingEmail: simulateEmailMutation.isPending,
    createTicket: createTicketMutation.mutateAsync,
    isCreatingTicket: createTicketMutation.isPending,
    replyTicket: replyTicketMutation.mutateAsync,
    isReplyingTicket: replyTicketMutation.isPending,
  }
}

export function useAdminTicket(ticketId: Ref<string>) {
  const queryClient = useQueryClient()

  const query = useQuery({
    queryKey: computed(() => ['admin-support-ticket', ticketId.value]),
    queryFn: async () => {
      try {
        const { data } = await api.get(`/support/admin/${ticketId.value}`)
        return sanitizeTicket(data as SupportTicket)
      } catch (err: any) {
        // If the backend server has not reloaded the new GET /admin/{ticket_id} endpoint,
        // fallback to /support/admin/list which is already active and contains all tickets.
        const { data: listData } = await api.get('/support/admin/list')
        const found = (listData as SupportTicket[]).find(
          (t) => t.id === ticketId.value || t.ticket_number === ticketId.value
        )
        if (found) {
          return sanitizeTicket(found)
        }
        throw err
      }
    },
    enabled: computed(() => !!ticketId.value),
  })

  const submitReplyMutation = useMutation({
    mutationFn: async ({ message, senderName }: { message: string; senderName?: string }) => {
      const targetId = query.data.value?.id || ticketId.value
      const { data } = await api.post(`/support/admin/${targetId}/replies`, {
        message: sanitize(message),
        sender_name: senderName ? sanitizeText(senderName) : undefined,
      })
      return sanitizeTicket(data as SupportTicket)
    },
    onSuccess: async (updatedTicket) => {
      queryClient.setQueryData(['admin-support-ticket', ticketId.value], updatedTicket)
      if (updatedTicket.id) {
        queryClient.setQueryData(['admin-support-ticket', updatedTicket.id], updatedTicket)
      }
      if (updatedTicket.ticket_number) {
        queryClient.setQueryData(['admin-support-ticket', updatedTicket.ticket_number], updatedTicket)
      }
      await query.refetch()
      queryClient.invalidateQueries({ queryKey: ['admin-support-tickets'] })
      queryClient.invalidateQueries({ queryKey: ['admin-support-counts'] })
      queryClient.invalidateQueries({ queryKey: ['my-support-tickets'] })
    },
  })

  return {
    ticket: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
    submitReply: submitReplyMutation.mutateAsync,
    isReplying: submitReplyMutation.isPending,
  }
}
