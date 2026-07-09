import { ref, computed } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import api from '@/lib/api'

export interface PendingUser {
  id: string
  name: string
  email: string
  role: string
  phone: string | null
  suspended: boolean
  status: string
  verification_status?: string | null
  created_at: string | null
}

export function usePendingUsers() {
  const queryClient = useQueryClient()
  const searchQuery = ref('')

  const queryKey = computed(() => [
    'admin-pending-users',
    { search: searchQuery.value },
  ])

  const query = useQuery({
    queryKey,
    queryFn: async () => {
      const params: Record<string, string> = {}
      if (searchQuery.value) params.search = searchQuery.value
      const { data } = await api.get('/admin/users/pending/list', { params })
      return data as PendingUser[]
    },
  })

  const approveMutation = useMutation({
    mutationFn: async (userId: string) => {
      await api.post(`/admin/users/${userId}/approve`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-pending-users'] })
    },
  })

  const rejectMutation = useMutation({
    mutationFn: async ({ userId, reason }: { userId: string; reason: string }) => {
      await api.post(`/admin/users/${userId}/reject`, { reason })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-pending-users'] })
    },
  })

  return {
    ...query,
    searchQuery,
    approveMutation,
    rejectMutation,
  }
}
