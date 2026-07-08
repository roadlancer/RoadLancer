import { useMutation, useQueryClient } from '@tanstack/vue-query'
import api from '@/lib/api'

export interface PlaceBidPayload {
  amount: number
  message?: string
}

export function usePlaceBid() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ shipmentId, payload }: { shipmentId: string; payload: PlaceBidPayload }) => {
      const { data } = await api.post(`/shipments/${shipmentId}/bids`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shipments'] })
      queryClient.invalidateQueries({ queryKey: ['shipment-bids'] })
    },
  })
}

export function useUpdateBid() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ shipmentId, payload }: { shipmentId: string; payload: PlaceBidPayload }) => {
      const { data } = await api.put(`/shipments/${shipmentId}/bids/update`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shipments'] })
      queryClient.invalidateQueries({ queryKey: ['shipment-bids'] })
    },
  })
}

export function useWithdrawBid() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (shipmentId: string) => {
      const { data } = await api.delete(`/shipments/${shipmentId}/bids/withdraw`)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shipments'] })
      queryClient.invalidateQueries({ queryKey: ['shipment-bids'] })
    },
  })
}
