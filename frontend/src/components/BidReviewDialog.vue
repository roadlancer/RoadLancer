<script lang="ts" setup>
import { computed } from 'vue'
import { useAcceptBid } from '@/composables/useAcceptBid'
import { useShipmentBids } from '@/composables/useShipmentDetail'
import type { Shipment } from '@/composables/useShipments'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Users, LoaderCircle, AlertCircle, CheckCircle2, Clock, MessageSquare } from '@lucide/vue'

const props = defineProps<{
  open: boolean
  shipment: Shipment | null
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'accepted'): void
}>()

const acceptBid = useAcceptBid()

const shipmentId = computed(() => props.shipment?.id || '')
const { data: bids, isLoading: loadingBids, isError: isBidsError, error: bidsError } = useShipmentBids(() => shipmentId.value)

function formatCurrency(amount?: number | null) {
  if (!amount) return 'N/A'
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function handleAccept(bidId: string) {
  await acceptBid.mutateAsync(bidId)
  emit('accepted')
  emit('update:open', false)
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="sm:max-w-[560px] max-h-[80vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <Users class="size-5 text-primary" />
          Review Driver Bids
        </DialogTitle>
        <DialogDescription v-if="shipment">
          {{ shipment.title }} — Range: {{ formatCurrency(shipment.ai_estimated_min || shipment.ai_floor_price) }} to {{ formatCurrency(shipment.ai_estimated_max || shipment.shipper_budget) }}
        </DialogDescription>
      </DialogHeader>

      <div class="space-y-4">
        <Alert v-if="acceptBid.isError.value" variant="destructive">
          <AlertCircle class="h-4 w-4" />
          <AlertDescription>{{ (acceptBid.error.value as any)?.response?.data?.detail || 'Failed to accept bid' }}</AlertDescription>
        </Alert>

        <Alert v-if="isBidsError" variant="destructive">
          <AlertCircle class="h-4 w-4" />
          <AlertDescription>{{ (bidsError as any)?.response?.data?.detail || 'Failed to load bids from server' }}</AlertDescription>
        </Alert>

        <div v-if="loadingBids" class="flex items-center justify-center py-8">
          <LoaderCircle class="size-6 animate-spin text-muted-foreground" />
        </div>

        <div v-else-if="!bids || bids.length === 0" class="text-center py-8">
          <Users class="size-10 text-muted-foreground mx-auto mb-2 opacity-50" />
          <p class="text-sm font-medium text-foreground">No Bids Yet</p>
          <p class="text-xs text-muted-foreground mt-1">Drivers haven't placed any bids on this shipment yet.</p>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="bid in bids"
            :key="bid.id"
            class="border rounded-lg p-4 space-y-3"
            :class="bid.status === 'accepted' ? 'bg-green-50/50 border-green-200' : bid.status === 'rejected' ? 'bg-red-50/30 border-red-200 opacity-60' : 'bg-card'"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="size-10 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-sm">
                  {{ bid.driver_id.slice(0, 2).toUpperCase() }}
                </div>
                <div>
                  <p class="text-sm font-semibold text-foreground">Driver {{ bid.driver_id.slice(0, 8) }}...</p>
                  <p class="text-xs text-muted-foreground flex items-center gap-1">
                    <Clock class="size-3" />
                    {{ formatDate(bid.created_at) }}
                  </p>
                </div>
              </div>
              <div class="text-right">
                <p class="text-lg font-bold text-primary">{{ formatCurrency(bid.amount) }}</p>
                <Badge
                  v-if="bid.status === 'accepted'"
                  class="bg-green-100 text-green-800 border-green-200"
                >
                  <CheckCircle2 class="size-3 mr-1" />
                  Accepted
                </Badge>
                <Badge
                  v-else-if="bid.status === 'rejected'"
                  variant="destructive"
                  class="text-xs"
                >
                  Rejected
                </Badge>
              </div>
            </div>

            <p v-if="bid.message" class="text-sm text-muted-foreground flex items-start gap-1.5">
              <MessageSquare class="size-3.5 mt-0.5 shrink-0" />
              {{ bid.message }}
            </p>

            <div v-if="bid.status === 'pending'" class="pt-1">
              <Button
                size="sm"
                class="w-full font-semibold"
                :disabled="acceptBid.isPending.value"
                @click="handleAccept(bid.id)"
              >
                <LoaderCircle v-if="acceptBid.isPending.value" class="size-4 animate-spin" />
                {{ acceptBid.isPending.value ? 'Accepting...' : 'Accept This Bid' }}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </DialogContent>
  </Dialog>
</template>
