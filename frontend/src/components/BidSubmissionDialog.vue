<script lang="ts" setup>
import { reactive } from 'vue'
import { z } from 'zod'
import { usePlaceBid } from '@/composables/usePlaceBid'
import type { Shipment } from '@/composables/useShipments'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { LoaderCircle, AlertCircle, DollarSign, Info, MapPin, Navigation, Package, Truck } from '@lucide/vue'

const props = defineProps<{
  open: boolean
  shipment: Shipment | null
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'submitted'): void
}>()

const placeBid = usePlaceBid()

const form = reactive({
  amount: '',
  message: '',
})

const errors = reactive({
  amount: '',
})

const bidSchema = z.object({
  amount: z.coerce.number().min(1, 'Bid amount is required'),
})

function validate() {
  const result = bidSchema.safeParse(form)
  errors.amount = result.success ? '' : result.error.issues[0]?.message ?? ''

  if (result.success && props.shipment?.ai_floor_price && parseFloat(form.amount) < props.shipment.ai_floor_price) {
    errors.amount = "Your bid is below the minimum viable operating cost for this route."
    return false
  }

  return result.success
}

function formatCurrency(amount?: number | null) {
  if (!amount) return 'N/A'
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)
}

async function handleSubmit() {
  if (!validate() || !props.shipment) return

  await placeBid.mutateAsync({
    shipmentId: props.shipment.id,
    payload: {
      amount: parseFloat(form.amount),
      message: form.message || undefined,
    },
  })

  emit('submitted')
  emit('update:open', false)
  form.amount = ''
  form.message = ''
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="sm:max-w-[480px]">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <DollarSign class="size-5 text-primary" />
          Submit Bid Quote
        </DialogTitle>
        <DialogDescription>
          Place your competitive bid for this shipment.
        </DialogDescription>
      </DialogHeader>

      <div v-if="shipment" class="space-y-4">
        <div class="bg-muted/50 border rounded-lg p-3 space-y-2">
          <p class="font-semibold text-sm text-foreground">{{ shipment.title }}</p>
          <div class="flex items-center gap-4 text-xs text-muted-foreground">
            <span class="flex items-center gap-1"><MapPin class="size-3" /> {{ shipment.pickup_address }}</span>
            <span class="flex items-center gap-1"><Navigation class="size-3" /> {{ shipment.dropoff_address }}</span>
          </div>
          <div class="flex items-center gap-4 text-xs text-muted-foreground">
            <span class="flex items-center gap-1"><Package class="size-3" /> {{ shipment.weight_kg }} kg</span>
            <span class="flex items-center gap-1"><Truck class="size-3" /> {{ shipment.vehicle_type }}</span>
            <span class="flex items-center gap-1"><Navigation class="size-3" /> {{ shipment.distance_km }} km</span>
          </div>
        </div>

        <div v-if="shipment.ai_estimated_min" class="bg-primary/5 border border-primary/20 rounded-lg p-3">
          <p class="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
            <Info class="size-3.5" />
            AI Suggested Price Range
          </p>
          <div class="mt-1 flex items-center gap-4 text-sm">
            <span>Suggested Range: <strong class="text-primary">{{ formatCurrency(shipment.ai_estimated_min) }} — {{ formatCurrency(shipment.ai_estimated_max || shipment.shipper_budget) }}</strong></span>
          </div>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4" novalidate>
          <Alert v-if="placeBid.isError.value" variant="destructive">
            <AlertCircle class="h-4 w-4" />
            <AlertDescription>{{ (placeBid.error.value as any)?.response?.data?.detail || 'Failed to place bid' }}</AlertDescription>
          </Alert>

          <div class="space-y-2">
            <Label for="bid-amount">Bid Amount (INR)</Label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground text-sm">₹</span>
              <Input
                id="bid-amount"
                v-model="form.amount"
                type="number"
                :placeholder="`e.g. ${shipment.ai_estimated_min || 15000}`"
                class="pl-8 text-lg font-semibold"
                :class="errors.amount ? 'border-destructive' : ''"
              />
            </div>
            <p v-if="errors.amount" class="text-sm text-destructive">{{ errors.amount }}</p>
          </div>

          <div class="space-y-2">
            <Label for="bid-message">Message (optional)</Label>
            <textarea
              id="bid-message"
              v-model="form.message"
              rows="3"
              placeholder="Tell the shipper why they should choose you..."
              class="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground"
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" @click="emit('update:open', false)">Cancel</Button>
            <Button type="submit" :disabled="placeBid.isPending.value">
              <LoaderCircle v-if="placeBid.isPending.value" class="size-4 animate-spin" />
              {{ placeBid.isPending.value ? 'Submitting...' : 'Submit Bid' }}
            </Button>
          </DialogFooter>
        </form>
      </div>
    </DialogContent>
  </Dialog>
</template>
