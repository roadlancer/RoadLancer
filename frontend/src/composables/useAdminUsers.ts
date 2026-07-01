import { ref, computed } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import api from '@/lib/api'

export interface UserRecord {
  id: string
  name: string
  email: string
  role: string
  phone: string | null
  suspended: boolean
  status: string
  created_at: string | null
}

export function useAdminUsers() {
  const queryClient = useQueryClient()
  const searchQuery = ref('')
  const activeTab = ref('all')

  const queryKey = computed(() => [
    'admin-users',
    { search: searchQuery.value, role: activeTab.value },
  ])

  const query = useQuery({
    queryKey,
    queryFn: async () => {
      const params: Record<string, string> = {}
      if (activeTab.value !== 'all') params.role = activeTab.value
      if (searchQuery.value) params.search = searchQuery.value
      const { data } = await api.get('/admin/users', { params })
      return data as UserRecord[]
    },
  })

  const pendingCount = useQuery({
    queryKey: ['admin-verification-count', 'pending'],
    queryFn: async () => {
      const { data } = await api.get('/verification/admin/count')
      return data.count as number
    },
  })

  const rejectedCount = useQuery({
    queryKey: ['admin-verification-count', 'rejected'],
    queryFn: async () => {
      const { data } = await api.get('/verification/admin/count', { params: { status: 'rejected' } })
      return data.count as number
    },
  })

  const suspendMutation = useMutation({
    mutationFn: async ({ userId, suspended }: { userId: string; suspended: boolean }) => {
      const { data } = await api.post(`/admin/users/${userId}/suspend`, { suspended })
      return data as UserRecord
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
    },
  })

  function refetchAll() {
    query.refetch()
    pendingCount.refetch()
    rejectedCount.refetch()
  }

  return {
    ...query,
    searchQuery,
    activeTab,
    pendingCount,
    rejectedCount,
    suspendMutation,
    refetchAll,
  }
}
