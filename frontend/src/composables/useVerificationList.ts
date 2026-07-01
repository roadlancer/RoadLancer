import { ref, computed } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import api from '@/lib/api'

export interface VerificationRecord {
  id: string
  userId: string
  userName: string
  userEmail: string
  userRole: string
  status: string
  licenseNumber: string | null
  vehicleType: string | null
  vehicleNumber: string | null
  businessName: string | null
  gstNumber: string | null
  companyAddress: string | null
  rejectionReason: string | null
  reviewedAt: string | null
  createdAt: string
}

export function useVerificationList() {
  const queryClient = useQueryClient()
  const searchQuery = ref('')
  const activeTab = ref('pending')

  const queryKey = computed(() => [
    'admin-verifications',
    { search: searchQuery.value, status: activeTab.value },
  ])

  const query = useQuery({
    queryKey,
    queryFn: async () => {
      const params: Record<string, string> = {}
      if (activeTab.value !== 'all') params.status = activeTab.value
      if (searchQuery.value) params.search = searchQuery.value
      const { data } = await api.get('/verification/admin/list', { params })
      return data as VerificationRecord[]
    },
  })

  const approveMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.post(`/verification/admin/${id}/approve`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-verifications'] })
      queryClient.invalidateQueries({ queryKey: ['admin-verification-count'] })
    },
  })

  const rejectMutation = useMutation({
    mutationFn: async ({ id, reason }: { id: string; reason?: string }) => {
      await api.post(`/verification/admin/${id}/reject`, { reason: reason || undefined })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-verifications'] })
      queryClient.invalidateQueries({ queryKey: ['admin-verification-count'] })
    },
  })

  return {
    ...query,
    searchQuery,
    activeTab,
    approveMutation,
    rejectMutation,
  }
}
