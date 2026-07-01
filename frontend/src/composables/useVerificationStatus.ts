import { computed } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import api from '@/lib/api'
import { useAuth } from './useAuth'

export function useVerificationStatus() {
  const { user } = useAuth()
  const queryClient = useQueryClient()

  const queryKey = computed(() => ['verification-status', user.value?.id])

  const query = useQuery({
    queryKey,
    queryFn: async () => {
      const { data } = await api.get('/verification/status')
      return data as { status: string; verification: any }
    },
    enabled: computed(() => !!user.value && user.value.role !== 'admin'),
    staleTime: 30_000,
  })

  const isVerified = computed(() => query.data.value?.status === 'approved')

  function invalidate() {
    queryClient.invalidateQueries({ queryKey: ['verification-status'] })
  }

  return { ...query, isVerified, invalidate }
}

export function useSubmitVerification() {
  const queryClient = useQueryClient()
  const { user } = useAuth()

  return useMutation({
    mutationFn: async (payload: { endpoint: string; body: any }) => {
      const { data } = await api.post(payload.endpoint, payload.body)
      return data as { status: string; verification: any }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['verification-status', user.value?.id] })
    },
  })
}
