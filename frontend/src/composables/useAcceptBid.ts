import { useMutation, useQueryClient } from '@tanstack/vue-query'
import api from '@/lib/api'

export function useAcceptBid() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (bidId: string) => {
      const { data } = await api.put(`/shipments/bids/${bidId}/accept`)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shipments'] })
      queryClient.invalidateQueries({ queryKey: ['shipment-bids'] })
    },
  })
}
