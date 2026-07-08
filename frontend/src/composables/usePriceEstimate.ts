import { useMutation } from '@tanstack/vue-query'
import api from '@/lib/api'

interface PriceEstimateParams {
  distance_km: number
  weight_kg: number
  vehicle_type: string
  goods_category: string
}

interface PriceBreakdown {
  distance_cost: number
  weight_cost: number
  base_cost: number
  fuel_cost: number
  toll_cost: number
  labour_cost: number
  vehicle_adjustment: number
  goods_adjustment: number
  seasonal_adjustment: number
  total_before_margin: number
  per_km_rate: number
  fuel_rate_per_litre: number
  vehicle_multiplier: number
  goods_multiplier: number
  seasonal_multiplier: number
}

interface PriceEstimateResponse {
  floor_price: number
  estimated_min: number
  estimated_max: number
  breakdown: PriceBreakdown
}

export function usePriceEstimate() {
  return useMutation({
    mutationFn: async (params: PriceEstimateParams): Promise<PriceEstimateResponse> => {
      const { data } = await api.post('/shipments/estimate-price', params)
      return data
    },
  })
}
