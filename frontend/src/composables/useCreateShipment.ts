import { useMutation, useQueryClient } from '@tanstack/vue-query'
import api from '@/lib/api'

export interface CreateShipmentPayload {
  title: string
  goods_category: string
  weight_kg: number
  pickup_address: string
  dropoff_address: string
  distance_km: number
  vehicle_type: string
  shipper_budget?: number | null
  is_forced_price?: boolean
  custom_min_price?: number
  custom_max_price?: number
}

export function useCreateShipment() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (payload: CreateShipmentPayload) => {
      const { data } = await api.post('/shipments/', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shipments'] })
    },
  })
}
