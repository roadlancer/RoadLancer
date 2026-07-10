<script lang="ts" setup>
import { reactive, ref } from 'vue'
import { z } from 'zod'
import { useCreateShipment } from '@/composables/useCreateShipment'
import { usePriceEstimate } from '@/composables/usePriceEstimate'
import PriceConfirmDialog from '@/components/PriceConfirmDialog.vue'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { LoaderCircle, AlertCircle, Package, MapPin, Navigation } from '@lucide/vue'

defineProps<{ open: boolean }>()
const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'created'): void
}>()

const createShipment = useCreateShipment()
const priceEstimate = usePriceEstimate()

const form = reactive({
  title: '',
  goods_category: 'general',
  weight_kg: '',
  pickup_address: '',
  dropoff_address: '',
  distance_km: '',
  vehicle_type: 'canter',
})

const errors = reactive({
  title: '',
  weight_kg: '',
  pickup_address: '',
  dropoff_address: '',
  distance_km: '',
})

const formSchema = z.object({
  title: z.string().min(3, 'Title must be at least 3 characters').max(200, 'Title must be at most 200 characters'),
  goods_category: z.string(),
  weight_kg: z.coerce.number().min(1, 'Weight must be at least 1 kg'),
  pickup_address: z.string().min(5, 'Enter a valid pickup address').max(300, 'Address must be at most 300 characters'),
  dropoff_address: z.string().min(5, 'Enter a valid dropoff address').max(300, 'Address must be at most 300 characters'),
  distance_km: z.coerce.number().min(1, 'Distance must be at least 1 km'),
  vehicle_type: z.string(),
})

const showPriceConfirm = ref(false)
const finalPrice = ref(0)
const isForcedPrice = ref(false)

function validate() {
  let valid = true
  const fields = ['title', 'weight_kg', 'pickup_address', 'dropoff_address', 'distance_km']

  for (const f of fields) {
    const fieldResult = (formSchema.shape as Record<string, any>)[f]?.safeParse(
      form[f as keyof typeof form]
    )
    errors[f as keyof typeof errors] = fieldResult?.success
      ? ''
      : fieldResult?.error?.issues[0]?.message ?? ''
    if (!fieldResult?.success) valid = false
  }

  return valid
}

async function handleCheckPrice() {
  if (!validate()) return

  await priceEstimate.mutate({
    distance_km: parseFloat(form.distance_km),
    weight_kg: parseFloat(form.weight_kg),
    vehicle_type: form.vehicle_type,
    goods_category: form.goods_category,
  })

  showPriceConfirm.value = true
}

async function handlePriceConfirm(payload: { price: number; is_forced_price: boolean; custom_min_price?: number; custom_max_price?: number }) {
  finalPrice.value = payload.price
  isForcedPrice.value = payload.is_forced_price

  await createShipment.mutateAsync({
    title: form.title,
    goods_category: form.goods_category,
    weight_kg: parseFloat(form.weight_kg),
    pickup_address: form.pickup_address,
    dropoff_address: form.dropoff_address,
    distance_km: parseFloat(form.distance_km),
    vehicle_type: form.vehicle_type,
    shipper_budget: payload.price,
    is_forced_price: payload.is_forced_price,
    custom_min_price: payload.custom_min_price,
    custom_max_price: payload.custom_max_price,
  })

  showPriceConfirm.value = false
  emit('created')
  emit('update:open', false)
  resetForm()
}

function resetForm() {
  form.title = ''
  form.goods_category = 'general'
  form.weight_kg = ''
  form.pickup_address = ''
  form.dropoff_address = ''
  form.distance_km = ''
  form.vehicle_type = 'canter'
  Object.keys(errors).forEach((k) => {
    errors[k as keyof typeof errors] = ''
  })
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="sm:max-w-[540px] max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <Package class="size-5 text-primary" />
          Post New Shipment
        </DialogTitle>
        <DialogDescription>
          Fill in the details below to post a new freight load.
        </DialogDescription>
      </DialogHeader>

      <form @submit.prevent="handleCheckPrice" class="space-y-4" novalidate>
        <Alert v-if="createShipment.isError.value" variant="destructive">
          <AlertCircle class="h-4 w-4" />
          <AlertDescription>
            {{
              typeof (createShipment.error.value as any)?.response?.data?.detail === 'string'
                ? (createShipment.error.value as any)?.response?.data?.detail
                : Array.isArray((createShipment.error.value as any)?.response?.data?.detail)
                ? (createShipment.error.value as any).response.data.detail.map((e: any) => `${e.loc?.slice(-1)[0] || 'Field'}: ${e.msg}`).join(', ')
                : (createShipment.error.value as any)?.response?.data?.message || (createShipment.error.value as any)?.message || 'Failed to create shipment'
            }}
          </AlertDescription>
        </Alert>

        <div class="space-y-2">
          <Label for="title">Shipment Title</Label>
          <Input
            id="title"
            v-model="form.title"
            placeholder="e.g. Electronics goods from Mumbai to Delhi"
            :class="errors.title ? 'border-destructive' : ''"
          />
          <p v-if="errors.title" class="text-sm text-destructive">{{ errors.title }}</p>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label for="goods_category">Goods Category</Label>
            <select
              id="goods_category"
              v-model="form.goods_category"
              class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="general">General</option>
              <option value="fragile">Fragile</option>
              <option value="perishable">Perishable</option>
              <option value="electronics">Electronics</option>
              <option value="textiles">Textiles</option>
              <option value="industrial">Industrial</option>
              <option value="hazmat">Hazardous (Hazmat)</option>
              <option value="cold_chain">Cold Chain</option>
              <option value="pharmaceutical">Pharmaceutical</option>
              <option value="high_value">High Value</option>
              <option value="fmcg">FMCG</option>
              <option value="automobile">Automobile</option>
              <option value="construction">Construction</option>
              <option value="furniture">Furniture</option>
              <option value="glass">Glass</option>
              <option value="livestock">Livestock</option>
            </select>
          </div>

          <div class="space-y-2">
            <Label for="vehicle_type">Vehicle Type</Label>
            <select
              id="vehicle_type"
              v-model="form.vehicle_type"
              class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="tempo">Tempo (1-2 Ton)</option>
              <option value="407">Tata 407 (3-4 Ton)</option>
              <option value="canter">Eicher Canter (5-7 Ton)</option>
              <option value="10wheeler">10-Wheeler (10-12 Ton)</option>
              <option value="19mt">19 MT (16-20 Ton)</option>
              <option value="32mt">32 MT Trailer (25-32 Ton)</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label for="weight_kg">Weight (kg)</Label>
            <Input
              id="weight_kg"
              v-model="form.weight_kg"
              type="number"
              placeholder="e.g. 5000"
              min="1"
              :class="errors.weight_kg ? 'border-destructive' : ''"
            />
            <p v-if="errors.weight_kg" class="text-sm text-destructive">{{ errors.weight_kg }}</p>
          </div>

          <div class="space-y-2">
            <Label for="distance_km">Distance (km)</Label>
            <Input
              id="distance_km"
              v-model="form.distance_km"
              type="number"
              placeholder="e.g. 1200"
              min="1"
              :class="errors.distance_km ? 'border-destructive' : ''"
            />
            <p v-if="errors.distance_km" class="text-sm text-destructive">{{ errors.distance_km }}</p>
          </div>
        </div>

        <div class="space-y-2">
          <Label for="pickup_address" class="flex items-center gap-1.5">
            <MapPin class="size-3.5 text-green-600" />
            Pickup Address
          </Label>
          <Input
            id="pickup_address"
            v-model="form.pickup_address"
            placeholder="e.g. Mumbai, Maharashtra"
            :class="errors.pickup_address ? 'border-destructive' : ''"
          />
          <p v-if="errors.pickup_address" class="text-sm text-destructive">{{ errors.pickup_address }}</p>
        </div>

        <div class="space-y-2">
          <Label for="dropoff_address" class="flex items-center gap-1.5">
            <Navigation class="size-3.5 text-red-600" />
            Dropoff Address
          </Label>
          <Input
            id="dropoff_address"
            v-model="form.dropoff_address"
            placeholder="e.g. Delhi, NCR"
            :class="errors.dropoff_address ? 'border-destructive' : ''"
          />
          <p v-if="errors.dropoff_address" class="text-sm text-destructive">{{ errors.dropoff_address }}</p>
        </div>

        <DialogFooter>
          <Button type="button" variant="outline" @click="emit('update:open', false)">Cancel</Button>
          <Button type="submit" :disabled="priceEstimate.isPending.value">
            <LoaderCircle v-if="priceEstimate.isPending.value" class="size-4 animate-spin" />
            {{ priceEstimate.isPending.value ? 'Calculating...' : 'Check Price' }}
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>

  <!-- Price Confirmation Dialog -->
  <PriceConfirmDialog
    :open="showPriceConfirm"
    :estimate="priceEstimate.data.value || null"
    :loading="priceEstimate.isPending.value"
    @update:open="showPriceConfirm = $event"
    @confirm="handlePriceConfirm"
  />
</template>
