import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import api from '@/lib/api'
import type { Shipment } from './useShipments'

export interface Bid {
  id: string
  shipment_id: string
  driver_id: string
  amount: number
  message: string | null
  status: string
  created_at: string
  shipment?: Shipment
}

export function useShipmentDetail(shipmentId: () => string) {
  return useQuery({
    queryKey: computed(() => ['shipment', shipmentId()]),
    queryFn: async () => {
      const { data } = await api.get(`/shipments/${shipmentId()}`)
      return data as Shipment
    },
    enabled: computed(() => !!shipmentId()),
  })
}

export function useShipmentBids(shipmentId: () => string) {
  return useQuery({
    queryKey: computed(() => ['shipment-bids', shipmentId()]),
    queryFn: async () => {
      const { data } = await api.get(`/shipments/${shipmentId()}/bids`)
      return data as Bid[]
    },
    enabled: computed(() => !!shipmentId()),
  })
}

export function useMyBids() {
  return useQuery({
    queryKey: ['my-bids'],
    queryFn: async () => {
      const { data } = await api.get('/shipments/bids/my')
      return data as Bid[]
    },
  })
}

export function useAssignedShipments() {
  return useQuery({
    queryKey: ['assigned-shipments'],
    queryFn: async () => {
      const { data } = await api.get('/shipments/assigned')
      return data as Shipment[]
    },
  })
}
