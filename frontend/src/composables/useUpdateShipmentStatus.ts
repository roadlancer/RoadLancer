import { useMutation, useQueryClient } from '@tanstack/vue-query'
import api from '@/lib/api'

export function useUpdateShipmentStatus() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ shipmentId, status }: { shipmentId: string; status: string }) => {
      const { data } = await api.put(`/shipments/${shipmentId}/status`, { status })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shipments'] })
      queryClient.invalidateQueries({ queryKey: ['assigned-shipments'] })
      queryClient.invalidateQueries({ queryKey: ['shipment'] })
    },
  })
}
