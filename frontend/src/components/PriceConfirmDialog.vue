<script lang="ts" setup>
import { ref, computed } from 'vue'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { LoaderCircle, AlertCircle, CheckCircle2, DollarSign, Info, AlertTriangle } from '@lucide/vue'

interface PriceEstimate {
  floor_price: number
  estimated_min: number
  estimated_max: number
  breakdown?: Record<string, any>
}

const props = defineProps<{
  open: boolean
  estimate: PriceEstimate | null
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'confirm', payload: { price: number; is_forced_price: boolean; custom_min_price?: number; custom_max_price?: number }): void
}>()

const mode = ref<'suggested' | 'custom'>('suggested')
const customMinPrice = ref('')
const customMaxPrice = ref('')
const forcedAcknowledged = ref(false)

const customPriceError = computed(() => {
  if (mode.value !== 'custom' || !props.estimate) return ''
  if (!customMinPrice.value || !customMaxPrice.value) return ''
  const min = parseFloat(customMinPrice.value)
  const max = parseFloat(customMaxPrice.value)
  if (isNaN(min) || isNaN(max) || min <= 0 || max <= 0) return 'Please enter valid prices'
  if (min >= max) return 'Minimum price must be less than maximum price'
  if (min < props.estimate.floor_price * 0.8 || max < props.estimate.floor_price * 0.8) {
    return 'The price range you entered is below market operating cost. This may result in no driver bids.'
  }
  return ''
})

const isForced = computed(() => {
  if (mode.value !== 'custom' || !props.estimate) return false
  if (!customMinPrice.value && !customMaxPrice.value) return false
  const min = parseFloat(customMinPrice.value || '0')
  const max = parseFloat(customMaxPrice.value || '0')
  return (!isNaN(min) && min > 0 && min < props.estimate.floor_price * 0.8) || (!isNaN(max) && max > 0 && max < props.estimate.floor_price * 0.8)
})

function handleConfirm() {
  let price: number
  let is_forced_price = false
  let custom_min_price: number | undefined
  let custom_max_price: number | undefined

  if (mode.value === 'suggested' && props.estimate) {
    price = props.estimate.estimated_max
  } else {
    const minVal = parseFloat(customMinPrice.value)
    const maxVal = parseFloat(customMaxPrice.value)
    if (isNaN(minVal) || isNaN(maxVal) || minVal <= 0 || maxVal <= 0) return
    custom_min_price = minVal
    custom_max_price = maxVal
    price = custom_max_price
    is_forced_price = isForced.value && forcedAcknowledged.value
  }

  emit('confirm', { price, is_forced_price, custom_min_price, custom_max_price })
}

function formatCurrency(amount: number) {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)
}

function handleClose() {
  mode.value = 'suggested'
  customMinPrice.value = ''
  customMaxPrice.value = ''
  forcedAcknowledged.value = false
  emit('update:open', false)
}
</script>

<template>
  <Dialog :open="open" @update:open="handleClose">
    <DialogContent class="sm:max-w-[500px]">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <DollarSign class="size-5 text-primary" />
          Review & Confirm Shipment Price
        </DialogTitle>
        <DialogDescription>
          Choose a pricing strategy for your shipment.
        </DialogDescription>
      </DialogHeader>

      <!-- Loading State -->
      <div v-if="loading" class="py-12 text-center space-y-3">
        <LoaderCircle class="size-8 animate-spin mx-auto text-primary" />
        <p class="text-sm font-medium text-muted-foreground">Calculating AI Price Estimate...</p>
      </div>

      <!-- Estimate Loaded -->
      <div v-else-if="estimate" class="space-y-4">
        <!-- Suggested Price Card -->
        <div class="bg-primary/5 border border-primary/20 rounded-xl p-4">
          <p class="text-sm font-semibold text-primary mb-3">AI Suggested Market Range</p>
          <div class="grid grid-cols-2 gap-4 text-center">
            <div class="bg-background rounded-lg p-3 border">
              <p class="text-xs text-muted-foreground">Minimum Price</p>
              <p class="text-lg font-bold text-foreground">{{ formatCurrency(estimate.estimated_min) }}</p>
            </div>
            <div class="bg-primary/10 rounded-lg p-3 border border-primary/30">
              <p class="text-xs text-primary font-medium">Maximum Price</p>
              <p class="text-lg font-bold text-primary">{{ formatCurrency(estimate.estimated_max) }}</p>
            </div>
          </div>
        </div>

        <!-- Mode Selection -->
        <div class="space-y-3">
          <p class="text-sm font-medium text-foreground">How would you like to post this shipment?</p>

          <!-- Option A: Use Suggested -->
          <button
            type="button"
            class="w-full text-left p-4 rounded-xl border-2 transition-all"
            :class="mode === 'suggested' ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'"
            @click="mode = 'suggested'"
          >
            <div class="flex items-center gap-3">
              <div class="w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0"
                   :class="mode === 'suggested' ? 'border-primary bg-primary' : 'border-muted-foreground'">
                <CheckCircle2 v-if="mode === 'suggested'" class="size-3 text-primary-foreground" />
              </div>
              <div>
                <p class="font-semibold text-foreground">Use AI Suggested Range (Recommended)</p>
                <p class="text-sm text-muted-foreground">Post with bidding range <strong class="text-primary">{{ formatCurrency(estimate.estimated_min) }} — {{ formatCurrency(estimate.estimated_max) }}</strong>.</p>
              </div>
            </div>
          </button>

          <!-- Option B: Set Custom -->
          <button
            type="button"
            class="w-full text-left p-4 rounded-xl border-2 transition-all"
            :class="mode === 'custom' ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'"
            @click="mode = 'custom'"
          >
            <div class="flex items-center gap-3">
              <div class="w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0"
                   :class="mode === 'custom' ? 'border-primary bg-primary' : 'border-muted-foreground'">
                <CheckCircle2 v-if="mode === 'custom'" class="size-3 text-primary-foreground" />
              </div>
              <div>
                <p class="font-semibold text-foreground">Set Custom Price Range</p>
                <p class="text-sm text-muted-foreground">Enter your own minimum and maximum bidding range</p>
              </div>
            </div>
          </button>
        </div>

        <!-- Custom Price Input -->
        <div v-if="mode === 'custom'" class="space-y-4">
          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-1.5">
              <Label for="custom_min_price">Minimum Price (INR)</Label>
              <Input
                id="custom_min_price"
                v-model="customMinPrice"
                type="number"
                :placeholder="`e.g. ${estimate.estimated_min}`"
                min="1"
                :class="customPriceError ? 'border-destructive' : ''"
              />
            </div>
            <div class="space-y-1.5">
              <Label for="custom_max_price">Maximum Price (INR)</Label>
              <Input
                id="custom_max_price"
                v-model="customMaxPrice"
                type="number"
                :placeholder="`e.g. ${estimate.estimated_max}`"
                min="1"
                :class="customPriceError ? 'border-destructive' : ''"
              />
            </div>
          </div>
          <p v-if="customPriceError" class="text-sm text-destructive flex items-start gap-1.5">
            <AlertTriangle class="size-4 shrink-0 mt-0.5" />
            {{ customPriceError }}
          </p>

          <!-- Forced Price Warning -->
          <div v-if="isForced" class="bg-destructive/10 border border-destructive/30 rounded-lg p-3 space-y-2">
            <p class="text-sm font-medium text-destructive flex items-center gap-1.5">
              <AlertTriangle class="size-4" />
              Low Price Warning
            </p>
            <p class="text-xs text-muted-foreground">
              Your price range is more than 20% below the AI recommended market rate. This shipment will be marked as <strong>"Forced Price"</strong> and will be visible to admins for review.
            </p>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="forcedAcknowledged" class="rounded border-destructive text-destructive focus:ring-destructive" />
              <span class="text-xs font-medium text-destructive">I understand the risks and want to proceed</span>
            </label>
          </div>
        </div>
      </div>

      <DialogFooter>
        <Button type="button" variant="outline" @click="handleClose">Cancel</Button>
        <Button
          type="button"
          @click="handleConfirm"
          :disabled="mode === 'custom' && (!customMinPrice || !customMaxPrice || parseFloat(customMinPrice) <= 0 || parseFloat(customMaxPrice) <= 0 || parseFloat(customMinPrice) >= parseFloat(customMaxPrice) || (isForced && !forcedAcknowledged))"
        >
          <CheckCircle2 class="size-4 mr-1" />
          Confirm & Post Shipment
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
