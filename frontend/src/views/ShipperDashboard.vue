<script lang="ts" setup>
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useVerificationStatus } from '@/composables/useVerificationStatus'
import { useShipments } from '@/composables/useShipments'
import CreateShipmentDialog from '@/components/CreateShipmentDialog.vue'
import BidReviewDialog from '@/components/BidReviewDialog.vue'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Package, Truck, MapPin, Navigation, PlusCircle, DollarSign, Users, ExternalLink, ArrowUpRight } from '@lucide/vue'

const router = useRouter()
const { user, loading } = useAuth()
const { isVerified, status: verificationStatus, isLoading: loadingVerification } = useVerificationStatus()
const { data: shipments, isLoading: loadingShipments } = useShipments()

const showCreateDialog = ref(false)
const showBidReviewDialog = ref(false)
const selectedShipment = ref<any>(null)

watch([user, loading], ([u, l]) => {
  if (l) return
  if (!u) {
    router.replace('/login')
  } else if (u.role !== 'shipper') {
    router.replace('/')
  }
})

const myShipments = computed(() => {
  return shipments.value || []
})

const activeShipments = computed(() => {
  return myShipments.value.filter(s => ['active', 'assigned', 'in_transit'].includes(s.status))
})

const inTransitShipments = computed(() => {
  return myShipments.value.filter(s => ['in_transit', 'picked_up', 'assigned'].includes(s.status))
})



function openCreateDialog() {
  if (!isVerified.value) {
    router.push('/get-validated')
    return
  }
  showCreateDialog.value = true
}

function handleShipmentCreated() {
  showCreateDialog.value = false
}

function openBidReview(shipment: any) {
  selectedShipment.value = shipment
  showBidReviewDialog.value = true
}

function handleBidAccepted() {
  showBidReviewDialog.value = false
  selectedShipment.value = null
}

const formatCurrency = (val: number) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(val)
}

const statusColors: Record<string, string> = {
  active: 'bg-blue-100 text-blue-800 border-blue-200',
  assigned: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  picked_up: 'bg-orange-100 text-orange-800 border-orange-200',
  in_transit: 'bg-purple-100 text-purple-800 border-purple-200',
  delivered: 'bg-cyan-100 text-cyan-800 border-cyan-200',
  completed: 'bg-green-100 text-green-800 border-green-200',
  cancelled: 'bg-red-100 text-red-800 border-red-200',
}
</script>

<template>
  <div class="flex-1 p-6 md:p-8 bg-background">
    <div class="max-w-7xl mx-auto space-y-8">
      <!-- Loading State -->
      <div v-if="loading || loadingShipments" class="space-y-6">
        <Skeleton class="h-10 w-48" />
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Skeleton class="h-28" />
          <Skeleton class="h-28" />
          <Skeleton class="h-28" />
          <Skeleton class="h-28" />
        </div>
        <Skeleton class="h-96" />
      </div>

      <template v-else>
        <!-- Header -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b pb-6">
          <div>
            <div class="flex items-center gap-3">
              <h1 class="text-3xl font-bold text-foreground">Shipper Dashboard</h1>
              <Badge v-if="!isVerified && !loadingVerification && verificationStatus === 'pending'" class="bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/30 capitalize px-2.5 py-0.5 animate-pulse">Under Review</Badge>
              <Badge v-else-if="!isVerified && !loadingVerification" class="bg-yellow-500/15 text-yellow-700 dark:text-yellow-400 border-yellow-500/30 capitalize px-2.5 py-0.5 animate-pulse">Verification Required</Badge>
              <Badge v-else class="bg-primary/10 text-primary border-primary/20 capitalize px-2.5 py-0.5">Verified Shipper</Badge>
            </div>
            <p class="text-muted-foreground mt-1">
              Post freight loads, review quotes from verified transport partners, and dispatch cargo.
            </p>
          </div>
          <div class="flex items-center gap-3">
            <Button class="h-10 px-5 font-semibold shadow-sm" :class="!isVerified && !loadingVerification ? 'bg-muted text-muted-foreground hover:bg-muted' : ''" @click="openCreateDialog">
              <PlusCircle class="size-4 mr-2" />
              <span v-if="!isVerified && !loadingVerification && verificationStatus === 'pending'">Under Review</span>
              <span v-else-if="!isVerified && !loadingVerification">Verify to Post</span>
              <span v-else>Post New Shipment</span>
            </Button>
          </div>
        </div>

        <!-- Pending Verification Banner -->
        <div v-if="!isVerified && !loadingVerification && verificationStatus === 'pending'" class="p-5 rounded-xl bg-amber-500/10 border border-amber-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 animate-in fade-in duration-300">
          <div class="space-y-1">
            <div class="flex items-center gap-2 font-bold text-amber-800 dark:text-amber-300 text-base">
              <span class="size-2.5 rounded-full bg-amber-500 animate-pulse"></span>
              Document Verification Under Review
            </div>
            <p class="text-sm text-amber-700/90 dark:text-amber-400/90 max-w-3xl">
              Your profile and document verification have been submitted and are currently being reviewed by our team. Posting new cargo shipments will be unlocked as soon as an admin approves your application.
            </p>
          </div>
          <a
            href="/get-validated"
            class="inline-flex items-center justify-center gap-1.5 rounded-lg px-3 text-xs font-semibold h-8 bg-amber-600 hover:bg-amber-700 text-white shrink-0 shadow-sm transition-all select-none no-underline"
          >
            View Application <ArrowUpRight class="size-4" />
          </a>
        </div>
        <div v-else-if="!isVerified && !loadingVerification" class="p-5 rounded-xl bg-yellow-500/10 border border-yellow-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 animate-in fade-in duration-300">
          <div class="space-y-1">
            <div class="flex items-center gap-2 font-bold text-yellow-800 dark:text-yellow-300 text-base">
              <span class="size-2.5 rounded-full bg-yellow-500 animate-pulse"></span>
              Document Verification Required
            </div>
            <p class="text-sm text-yellow-700/90 dark:text-yellow-400/90 max-w-3xl">
              You can explore the platform and check AI pricing estimates immediately. However, posting new cargo shipments requires you to complete Document & Profile Verification.
            </p>
          </div>
          <a
            href="/get-validated"
            class="inline-flex items-center justify-center gap-1.5 rounded-lg px-3 text-xs font-semibold h-8 bg-yellow-600 hover:bg-yellow-700 text-white shrink-0 shadow-sm transition-all select-none no-underline"
          >
            Complete Verification <ArrowUpRight class="size-4" />
          </a>
        </div>

        <!-- KPI Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card class="border shadow-2xs">
            <CardContent class="p-5 flex items-center justify-between">
              <div>
                <p class="text-xs font-medium text-muted-foreground uppercase tracking-wider">Active Shipments</p>
                <p class="text-2xl font-bold text-foreground mt-1">{{ activeShipments.length }}</p>
              </div>
              <div class="size-11 rounded-lg bg-blue-500/10 text-blue-600 flex items-center justify-center">
                <Package class="size-6" />
              </div>
            </CardContent>
          </Card>

          <Card class="border shadow-2xs">
            <CardContent class="p-5 flex items-center justify-between">
              <div>
                <p class="text-xs font-medium text-muted-foreground uppercase tracking-wider">Total Shipments</p>
                <p class="text-2xl font-bold text-foreground mt-1">{{ myShipments.length }}</p>
              </div>
              <div class="size-11 rounded-lg bg-yellow-500/10 text-yellow-600 flex items-center justify-center">
                <Users class="size-6" />
              </div>
            </CardContent>
          </Card>

          <Card class="border shadow-2xs">
            <CardContent class="p-5 flex items-center justify-between">
              <div>
                <p class="text-xs font-medium text-muted-foreground uppercase tracking-wider">In Transit / Dispatched</p>
                <p class="text-2xl font-bold text-foreground mt-1">{{ inTransitShipments.length }}</p>
              </div>
              <div class="size-11 rounded-lg bg-green-500/10 text-green-600 flex items-center justify-center">
                <Truck class="size-6" />
              </div>
            </CardContent>
          </Card>

          <Card class="border shadow-2xs">
            <CardContent class="p-5 flex items-center justify-between">
              <div>
                <p class="text-xs font-medium text-muted-foreground uppercase tracking-wider">Completed</p>
                <p class="text-2xl font-bold text-foreground mt-1">{{ myShipments.filter(s => s.status === 'completed').length }}</p>
              </div>
              <div class="size-11 rounded-lg bg-emerald-500/10 text-emerald-600 flex items-center justify-center">
                <DollarSign class="size-6" />
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- Shipments List Section -->
        <div class="space-y-4">
          <div class="flex items-center justify-between border-b pb-3">
            <h2 class="text-lg font-bold text-foreground">My Posted Shipments</h2>
            <span class="text-sm text-muted-foreground">{{ myShipments.length }} shipments</span>
          </div>

          <div v-if="myShipments.length === 0" class="text-center py-16 bg-card border rounded-xl">
            <Package class="size-12 text-muted-foreground mx-auto opacity-50" />
            <p class="text-sm text-muted-foreground mt-2">No shipments posted yet.</p>
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card v-for="s in myShipments" :key="s.id" class="border hover:border-primary/50 transition shadow-xs flex flex-col justify-between">
              <CardHeader class="pb-3">
                <div class="flex items-start justify-between gap-2">
                  <div>
                    <Badge variant="outline" class="mb-1.5 bg-muted/50 text-xs">{{ s.goods_category }}</Badge>
                    <CardTitle class="text-lg font-bold text-foreground">{{ s.title }}</CardTitle>
                  </div>
                  <Badge :class="statusColors[s.status] || 'bg-muted'" class="capitalize">{{ s.status.replace('_', ' ') }}</Badge>
                </div>
              </CardHeader>
              <CardContent class="space-y-3 pt-0 text-sm">
                <div class="bg-muted/30 p-3 rounded-lg space-y-2 border border-border/50">
                  <div class="flex items-center gap-2 text-foreground">
                    <MapPin class="size-4 text-green-600 shrink-0" />
                    <span class="font-medium truncate">{{ s.pickup_address }}</span>
                  </div>
                  <div class="flex items-center gap-2 text-foreground">
                    <Navigation class="size-4 text-red-600 shrink-0" />
                    <span class="font-medium truncate">{{ s.dropoff_address }}</span>
                  </div>
                </div>

                <div class="flex items-center justify-between text-xs text-muted-foreground pt-1">
                  <span class="flex items-center gap-1"><Truck class="size-3.5" /> {{ s.vehicle_type }}</span>
                  <span class="flex items-center gap-1"><Package class="size-3.5" /> {{ s.weight_kg }} kg</span>
                  <span class="font-semibold text-foreground">Range: {{ formatCurrency(s.ai_estimated_min ?? s.ai_floor_price ?? 0) }} — {{ formatCurrency(s.ai_estimated_max ?? s.shipper_budget ?? 0) }}</span>
                </div>

                <div class="pt-2 flex items-center gap-2">
                  <Button variant="outline" class="flex-1" @click="router.push(`/shipments/${s.id}`)">
                    <ExternalLink class="size-4 mr-1.5" />
                    View Details
                  </Button>
                  <Button
                    v-if="s.status === 'active'"
                    class="flex-1 font-semibold"
                    @click="openBidReview(s)"
                  >
                    Review Bids
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <CreateShipmentDialog
          :open="showCreateDialog"
          @update:open="showCreateDialog = $event"
          @created="handleShipmentCreated"
        />

        <BidReviewDialog
          :open="showBidReviewDialog"
          :shipment="selectedShipment"
          @update:open="showBidReviewDialog = $event"
          @accepted="handleBidAccepted"
        />
      </template>
    </div>
  </div>
</template>
