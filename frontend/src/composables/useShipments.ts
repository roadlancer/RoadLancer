import { useQuery } from '@tanstack/vue-query'
import api from '@/lib/api'
import { sanitizeText } from '@/lib/sanitize'

export interface Shipment {
  id: string
  shipper_id: string
  title: string
  goods_category: string
  weight_kg: number
  pickup_address: string
  dropoff_address: string
  distance_km: number
  vehicle_type: string
  ai_floor_price?: number | null
  ai_estimated_min?: number | null
  ai_estimated_max?: number | null
  shipper_budget?: number | null
  is_forced_price?: boolean
  status: string
  price?: number | null
  assigned_driver_id?: string | null
  bidding_ends_at?: string | null
  created_at: string
  updated_at: string
}

export function sanitizeShipment(shipment: Shipment): Shipment {
  if (!shipment) return shipment
  return {
    ...shipment,
    title: sanitizeText(shipment.title),
    pickup_address: sanitizeText(shipment.pickup_address),
    dropoff_address: sanitizeText(shipment.dropoff_address),
  }
}

export function useShipments() {
  const query = useQuery({
    queryKey: ['shipments'],
    queryFn: async () => {
      const { data } = await api.get('/shipments/')
      return (data as Shipment[]).map(sanitizeShipment)
    },
    staleTime: 15_000,
  })

  return { ...query }
}
