<script lang="ts" setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQueryClient } from '@tanstack/vue-query'
import { useAuth } from '@/composables/useAuth'
import { useVerificationStatus } from '@/composables/useVerificationStatus'
import { useShipmentDetail, useShipmentBids } from '@/composables/useShipmentDetail'
import { useUpdateShipmentStatus } from '@/composables/useUpdateShipmentStatus'
import BidSubmissionDialog from '@/components/BidSubmissionDialog.vue'
import BidReviewDialog from '@/components/BidReviewDialog.vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Separator } from '@/components/ui/separator'
import { MapPin, Navigation, Package, Truck, DollarSign, CheckCircle2, ArrowLeft, LoaderCircle, Users, MessageSquare } from '@lucide/vue'

const route = useRoute()
const router = useRouter()
const queryClient = useQueryClient()
const { user } = useAuth()
const { isVerified, isLoading: loadingVerification } = useVerificationStatus()


const shipmentId = computed(() => route.params.id as string)
const { data: shipment, isLoading, error } = useShipmentDetail(() => shipmentId.value)
const { data: bids } = useShipmentBids(() => shipmentId.value)
const updateStatus = useUpdateShipmentStatus()

const showBidDialog = ref(false)
const showBidReviewDialog = ref(false)

const statusSteps = ['active', 'assigned', 'picked_up', 'in_transit', 'delivered', 'completed']

const currentStepIndex = computed(() => {
  if (!shipment.value) return -1
  return statusSteps.indexOf(shipment.value.status)
})

const statusColors: Record<string, string> = {
  active: 'bg-blue-100 text-blue-800 border-blue-200',
  assigned: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  picked_up: 'bg-orange-100 text-orange-800 border-orange-200',
  in_transit: 'bg-purple-100 text-purple-800 border-purple-200',
  delivered: 'bg-cyan-100 text-cyan-800 border-cyan-200',
  completed: 'bg-green-100 text-green-800 border-green-200',
  cancelled: 'bg-red-100 text-red-800 border-red-200',
}

function formatCurrency(amount?: number | null) {
  if (!amount) return 'N/A'
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

const nextStatus: Record<string, { status: string; label: string } | null> = {
  active: null,
  assigned: { status: 'picked_up', label: 'Confirm Pickup' },
  picked_up: { status: 'in_transit', label: 'Start Transit' },
  in_transit: { status: 'delivered', label: 'Mark Delivered' },
  delivered: { status: 'completed', label: 'Confirm Delivery' },
  completed: null,
  cancelled: null,
}

async function handleStatusUpdate(newStatus: string) {
  await updateStatus.mutateAsync({ shipmentId: shipmentId.value, status: newStatus })
}

function openBidDialog() {
  if (!isVerified.value && !loadingVerification.value) {
    alert('You must complete Document & Profile Verification before you can place bids.')
    router.push('/get-validated')
    return
  }
  showBidDialog.value = true
}

function handleBidSubmitted() {
  queryClient.invalidateQueries({ queryKey: ['shipment', shipmentId.value] })
  queryClient.invalidateQueries({ queryKey: ['shipment-bids', shipmentId.value] })
}

function handleBidAccepted() {
  queryClient.invalidateQueries({ queryKey: ['shipment', shipmentId.value] })
  queryClient.invalidateQueries({ queryKey: ['shipment-bids', shipmentId.value] })
  queryClient.invalidateQueries({ queryKey: ['shipments'] })
}
</script>

<template>
  <div class="flex-1 p-6 md:p-8 bg-background">
    <div class="max-w-4xl mx-auto space-y-6">
      <div v-if="isLoading" class="space-y-6">
        <Skeleton class="h-10 w-48" />
        <Skeleton class="h-64 w-full rounded-xl" />
        <Skeleton class="h-48 w-full rounded-xl" />
      </div>

      <div v-else-if="error" class="text-center py-16">
        <p class="text-lg font-semibold text-destructive">Shipment not found</p>
        <Button variant="link" @click="router.back()" class="mt-2">Go back</Button>
      </div>

      <template v-else-if="shipment">
        <div class="flex items-center gap-4 border-b pb-6">
          <Button variant="ghost" size="icon" @click="router.back()">
            <ArrowLeft class="size-5" />
          </Button>
          <div class="flex-1">
            <div class="flex items-center gap-3 flex-wrap">
              <h1 class="text-2xl font-bold text-foreground">{{ shipment.title }}</h1>
              <Badge :class="statusColors[shipment.status] || 'bg-muted'" class="capitalize">{{ shipment.status.replace('_', ' ') }}</Badge>
            </div>
            <p class="text-sm text-muted-foreground mt-1">Created on {{ formatDate(shipment.created_at) }}</p>
          </div>
          <div class="text-right hidden sm:block">
            <p class="text-xs text-muted-foreground">Bidding Range</p>
            <p class="text-xl font-bold text-primary">{{ formatCurrency(shipment.ai_estimated_min) }} — {{ formatCurrency(shipment.ai_estimated_max || shipment.shipper_budget) }}</p>
          </div>
        </div>

        <div class="flex items-center gap-1 bg-muted/30 rounded-lg p-2 overflow-x-auto">
          <div
            v-for="(step, i) in statusSteps"
            :key="step"
            class="flex items-center gap-1 min-w-0"
          >
            <div
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap transition-colors"
              :class="i <= currentStepIndex ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'"
            >
              <CheckCircle2 v-if="i <= currentStepIndex" class="size-3.5" />
              <span class="hidden sm:inline">{{ step.replace('_', ' ') }}</span>
            </div>
            <div v-if="i < statusSteps.length - 1" class="w-4 h-px bg-border" :class="i < currentStepIndex ? 'bg-primary' : ''" />
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="lg:col-span-2 space-y-6">
            <Card class="border">
              <CardHeader>
                <CardTitle class="text-lg flex items-center gap-2">
                  <Package class="size-5 text-primary" />
                  Shipment Details
                </CardTitle>
              </CardHeader>
              <CardContent class="space-y-4">
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div>
                    <p class="text-xs text-muted-foreground">Category</p>
                    <p class="text-sm font-medium capitalize">{{ shipment.goods_category }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-muted-foreground">Weight</p>
                    <p class="text-sm font-medium">{{ shipment.weight_kg }} kg</p>
                  </div>
                  <div>
                    <p class="text-xs text-muted-foreground">Distance</p>
                    <p class="text-sm font-medium">{{ shipment.distance_km }} km</p>
                  </div>
                  <div>
                    <p class="text-xs text-muted-foreground">Vehicle</p>
                    <p class="text-sm font-medium capitalize">{{ shipment.vehicle_type.replace('_', ' ') }}</p>
                  </div>
                </div>

                <Separator />

                <div class="space-y-3">
                  <div class="flex items-start gap-3">
                    <div class="size-8 rounded-full bg-green-100 text-green-700 flex items-center justify-center shrink-0">
                      <MapPin class="size-4" />
                    </div>
                    <div>
                      <p class="text-xs text-muted-foreground">Pickup Address</p>
                      <p class="text-sm font-medium">{{ shipment.pickup_address }}</p>
                    </div>
                  </div>
                  <div class="flex items-start gap-3">
                    <div class="size-8 rounded-full bg-red-100 text-red-700 flex items-center justify-center shrink-0">
                      <Navigation class="size-4" />
                    </div>
                    <div>
                      <p class="text-xs text-muted-foreground">Dropoff Address</p>
                      <p class="text-sm font-medium">{{ shipment.dropoff_address }}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card v-if="shipment.status === 'active' && user?.role === 'driver'" class="border">
              <CardHeader>
                <CardTitle class="text-lg flex items-center gap-2">
                  <DollarSign class="size-5 text-primary" />
                  Your Bid
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div v-if="bids && bids.length > 0" class="space-y-3">
                  <div v-for="bid in bids" :key="bid.id" class="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p class="text-sm font-semibold">{{ formatCurrency(bid.amount) }}</p>
                      <p v-if="bid.message" class="text-xs text-muted-foreground mt-0.5">{{ bid.message }}</p>
                    </div>
                    <Badge :class="bid.status === 'accepted' ? 'bg-green-100 text-green-800' : bid.status === 'rejected' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'" class="capitalize text-xs">
                      {{ bid.status }}
                    </Badge>
                  </div>
                </div>
                <Button class="w-full mt-2" :class="!isVerified && !loadingVerification ? 'bg-muted text-muted-foreground cursor-not-allowed hover:bg-muted' : ''" @click="openBidDialog">
                  <span v-if="!isVerified && !loadingVerification">Verify to Bid</span>
                  <span v-else>{{ bids && bids.length > 0 ? 'Update Bid' : 'Submit Bid Quote' }}</span>
                </Button>
              </CardContent>
            </Card>

            <Card v-if="shipment.status === 'active' && user?.role === 'shipper' && shipment.shipper_id === user.id" class="border">
              <CardHeader>
                <CardTitle class="text-lg flex items-center gap-2">
                  <Users class="size-5 text-primary" />
                  Bids Received ({{ bids?.length || 0 }})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div v-if="bids && bids.length > 0" class="space-y-3">
                  <div v-for="bid in bids" :key="bid.id" class="flex items-center justify-between p-3 border rounded-lg">
                    <div class="flex items-center gap-3">
                      <div class="size-10 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-sm">
                        {{ bid.driver_id.slice(0, 2).toUpperCase() }}
                      </div>
                      <div>
                        <p class="text-sm font-semibold">Driver {{ bid.driver_id.slice(0, 8) }}...</p>
                        <p v-if="bid.message" class="text-xs text-muted-foreground flex items-center gap-1">
                          <MessageSquare class="size-3" /> {{ bid.message }}
                        </p>
                      </div>
                    </div>
                    <div class="text-right">
                      <p class="text-lg font-bold text-primary">{{ formatCurrency(bid.amount) }}</p>
                      <Badge :class="bid.status === 'accepted' ? 'bg-green-100 text-green-800' : bid.status === 'rejected' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'" class="capitalize text-xs">
                        {{ bid.status }}
                      </Badge>
                    </div>
                  </div>
                </div>
                <div v-else class="text-center py-4">
                  <p class="text-sm text-muted-foreground">No bids received yet.</p>
                </div>
                <Button variant="outline" class="w-full mt-3" @click="showBidReviewDialog = true">
                  Review All Bids
                </Button>
              </CardContent>
            </Card>

            <Card v-if="shipment.status === 'assigned' && user?.role === 'driver' && shipment.assigned_driver_id === user.id" class="border">
              <CardHeader>
                <CardTitle class="text-lg flex items-center gap-2">
                  <Truck class="size-5 text-primary" />
                  Ready to Pick Up
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p class="text-sm text-muted-foreground mb-4">This shipment has been assigned to you. Please confirm pickup when ready.</p>
                <Button class="w-full font-semibold" @click="handleStatusUpdate('picked_up')">
                  <LoaderCircle v-if="updateStatus.isPending.value" class="size-4 animate-spin" />
                  {{ updateStatus.isPending.value ? 'Updating...' : 'Confirm Pickup' }}
                </Button>
              </CardContent>
            </Card>
          </div>

          <div class="space-y-6">
            <Card class="border">
              <CardHeader>
                <CardTitle class="text-lg">AI Suggested Price Range</CardTitle>
              </CardHeader>
              <CardContent class="space-y-4">
                <div class="space-y-3">
                  <div class="flex justify-between items-center">
                    <span class="text-sm text-muted-foreground">Minimum Price</span>
                    <span class="text-base font-semibold text-primary">{{ formatCurrency(shipment.ai_estimated_min) }}</span>
                  </div>
                  <div class="flex justify-between items-center">
                    <span class="text-sm text-muted-foreground">Maximum Price</span>
                    <span class="text-base font-semibold text-primary">{{ formatCurrency(shipment.ai_estimated_max || shipment.shipper_budget) }}</span>
                  </div>
                </div>
                <div v-if="shipment.is_forced_price && user?.role === 'admin'" class="bg-orange-50 border border-orange-200 rounded-lg p-3 mt-2">
                  <p class="text-sm font-medium text-orange-800 flex items-center gap-1.5">
                    <span class="w-2 h-2 bg-orange-500 rounded-full"></span>
                    Forced Price
                  </p>
                  <p class="text-xs text-orange-600 mt-1">This shipment was priced below market rate by the shipper.</p>
                </div>
              </CardContent>
            </Card>

            <Card v-if="user?.role === 'driver' && shipment.assigned_driver_id === user.id && !['completed', 'cancelled', 'delivered'].includes(shipment.status)" class="border">
              <CardHeader>
                <CardTitle class="text-lg">Transit Actions</CardTitle>
              </CardHeader>
              <CardContent class="space-y-2">
                <Button
                  v-if="nextStatus[shipment.status]"
                  class="w-full font-semibold"
                  :disabled="updateStatus.isPending.value"
                  @click="handleStatusUpdate(nextStatus[shipment.status]!.status)"
                >
                  <LoaderCircle v-if="updateStatus.isPending.value" class="size-4 animate-spin" />
                  {{ updateStatus.isPending.value ? 'Updating...' : nextStatus[shipment.status]!.label }}
                </Button>
                <Button
                  v-if="shipment.status === 'delivered' && (user?.role as string) === 'shipper' && shipment.shipper_id === user?.id"
                  class="w-full font-semibold bg-green-600 hover:bg-green-700"
                  :disabled="updateStatus.isPending.value"
                  @click="handleStatusUpdate('completed')"
                >
                  <LoaderCircle v-if="updateStatus.isPending.value" class="size-4 animate-spin" />
                  {{ updateStatus.isPending.value ? 'Confirming...' : 'Confirm Delivery & Complete' }}
                </Button>
              </CardContent>
            </Card>

            <Card v-if="(user?.role as string) === 'shipper' && shipment.shipper_id === user?.id && shipment.status !== 'completed' && shipment.status !== 'cancelled'" class="border">
              <CardHeader>
                <CardTitle class="text-lg">Shipper Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <Button
                  v-if="shipment.status === 'delivered'"
                  class="w-full font-semibold bg-green-600 hover:bg-green-700"
                  :disabled="updateStatus.isPending.value"
                  @click="handleStatusUpdate('completed')"
                >
                  <LoaderCircle v-if="updateStatus.isPending.value" class="size-4 animate-spin" />
                  {{ updateStatus.isPending.value ? 'Confirming...' : 'Confirm Delivery' }}
                </Button>
                <Button
                  v-else-if="shipment.status === 'active' || shipment.status === 'assigned'"
                  variant="destructive"
                  class="w-full"
                  :disabled="updateStatus.isPending.value"
                  @click="handleStatusUpdate('cancelled')"
                >
                  <LoaderCircle v-if="updateStatus.isPending.value" class="size-4 animate-spin" />
                  Cancel Shipment
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </template>

      <BidSubmissionDialog
        v-if="user?.role === 'driver'"
        :open="showBidDialog"
        :shipment="shipment || null"
        @update:open="showBidDialog = $event"
        @submitted="handleBidSubmitted"
      />

      <BidReviewDialog
        v-if="user?.role === 'shipper'"
        :open="showBidReviewDialog"
        :shipment="shipment || null"
        @update:open="showBidReviewDialog = $event"
        @accepted="handleBidAccepted"
      />
    </div>
  </div>
</template>
