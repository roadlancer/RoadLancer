<script lang="ts" setup>
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useVerificationStatus } from '@/composables/useVerificationStatus'
import { useShipments } from '@/composables/useShipments'
import { useAssignedShipments } from '@/composables/useShipmentDetail'
import BidSubmissionDialog from '@/components/BidSubmissionDialog.vue'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Truck, MapPin, Package, Navigation, CheckCircle2, ArrowUpRight, ExternalLink, DollarSign } from '@lucide/vue'

const router = useRouter()
const { user, loading } = useAuth()
const { isVerified, status: verificationStatus, isLoading: loadingVerification } = useVerificationStatus()
const { data: shipments, isLoading: loadingShipments } = useShipments()
const { data: assignedShipments, isLoading: loadingAssigned } = useAssignedShipments()

const activeTab = ref<'available' | 'assigned'>('available')
const showBidDialog = ref(false)
const selectedShipment = ref<any>(null)

watch([user, loading], ([u, l]) => {
  if (l) return
  if (!u) {
    router.replace('/login')
  } else if (u.role !== 'driver') {
    router.replace('/')
  }
})

const availableShipments = computed(() => {
  return (shipments.value || []).filter(s => s.status === 'active')
})

function openBidDialog(shipment: any) {
  if (!isVerified.value && !loadingVerification.value) {
    alert('You must complete Document & Profile Verification before you can place bids.')
    router.push('/get-validated')
    return
  }
  selectedShipment.value = shipment
  showBidDialog.value = true
}

function handleBidSubmitted() {
  showBidDialog.value = false
  selectedShipment.value = null
}

function formatCurrency(amount?: number | null) {
  if (!amount) return 'Negotiable'
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)
}

const statusColors: Record<string, string> = {
  assigned: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  picked_up: 'bg-orange-100 text-orange-800 border-orange-200',
  in_transit: 'bg-purple-100 text-purple-800 border-purple-200',
  delivered: 'bg-cyan-100 text-cyan-800 border-cyan-200',
  completed: 'bg-green-100 text-green-800 border-green-200',
}

function getNextAction(status: string): { label: string; nextStatus: string } | null {
  const actions: Record<string, { label: string; nextStatus: string }> = {
    assigned: { label: 'Confirm Pickup', nextStatus: 'picked_up' },
    picked_up: { label: 'Start Transit', nextStatus: 'in_transit' },
    in_transit: { label: 'Mark Delivered', nextStatus: 'delivered' },
  }
  return actions[status] || null
}
</script>

<template>
  <div class="flex-1 p-6 md:p-8 bg-background">
    <div class="max-w-6xl mx-auto space-y-8">
      <!-- Loading State -->
      <div v-if="loading || loadingShipments || loadingAssigned" class="space-y-6">
        <Skeleton class="h-10 w-64" />
        <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <Skeleton v-for="i in 4" :key="i" class="h-28 w-full rounded-xl" />
        </div>
        <Skeleton class="h-96 w-full rounded-xl" />
      </div>

      <template v-else-if="user?.role === 'driver'">
        <!-- Header -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b pb-6">
          <div>
            <div class="flex items-center gap-3">
              <h1 class="text-3xl font-bold text-foreground">Driver Dashboard</h1>
              <Badge v-if="!isVerified && !loadingVerification && verificationStatus === 'pending'" class="bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/30 capitalize px-2.5 py-0.5 animate-pulse">Under Review</Badge>
              <Badge v-else-if="!isVerified && !loadingVerification" class="bg-yellow-500/15 text-yellow-700 dark:text-yellow-400 border-yellow-500/30 capitalize px-2.5 py-0.5 animate-pulse">Verification Required</Badge>
              <Badge v-else class="bg-primary/10 text-primary border-primary/20 capitalize px-2.5 py-0.5">Verified Driver</Badge>
            </div>
            <p class="text-muted-foreground mt-1">
              Find loads, submit competitive quotes, and track your active transport jobs.
            </p>
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
              Your profile and document verification have been submitted and are currently being reviewed by our team. Placing bids and accepting transport jobs will be unlocked as soon as an admin approves your application.
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
              You can explore available loads and market rates immediately. However, placing bids and accepting transport jobs requires you to complete Document & Profile Verification.
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
                <p class="text-xs font-medium text-muted-foreground uppercase tracking-wider">Available Loads</p>
                <p class="text-2xl font-bold text-foreground mt-1">{{ availableShipments.length }}</p>
              </div>
              <div class="size-11 rounded-lg bg-blue-500/10 text-blue-600 flex items-center justify-center">
                <Package class="size-6" />
              </div>
            </CardContent>
          </Card>

          <Card class="border shadow-2xs">
            <CardContent class="p-5 flex items-center justify-between">
              <div>
                <p class="text-xs font-medium text-muted-foreground uppercase tracking-wider">Won / Active Jobs</p>
                <p class="text-2xl font-bold text-foreground mt-1">{{ (assignedShipments || []).length }}</p>
              </div>
              <div class="size-11 rounded-lg bg-green-500/10 text-green-600 flex items-center justify-center">
                <Truck class="size-6" />
              </div>
            </CardContent>
          </Card>

          <Card class="border shadow-2xs">
            <CardContent class="p-5 flex items-center justify-between">
              <div>
                <p class="text-xs font-medium text-muted-foreground uppercase tracking-wider">Completed Trips</p>
                <p class="text-2xl font-bold text-foreground mt-1">{{ (assignedShipments || []).filter(s => s.status === 'completed').length }}</p>
              </div>
              <div class="size-11 rounded-lg bg-purple-500/10 text-purple-600 flex items-center justify-center">
                <CheckCircle2 class="size-6" />
              </div>
            </CardContent>
          </Card>

          <Card class="border shadow-2xs">
            <CardContent class="p-5 flex items-center justify-between">
              <div>
                <p class="text-xs font-medium text-muted-foreground uppercase tracking-wider">Active Shipments</p>
                <p class="text-2xl font-bold text-foreground mt-1">{{ (assignedShipments || []).filter(s => s.status !== 'completed' && s.status !== 'cancelled').length }}</p>
              </div>
              <div class="size-11 rounded-lg bg-emerald-500/10 text-emerald-600 flex items-center justify-center">
                <Truck class="size-6" />
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- Section Navigation -->
        <div class="flex items-center gap-2 border-b">
          <button
            @click="activeTab = 'available'"
            class="px-5 py-3 font-semibold text-sm border-b-2 transition flex items-center gap-2"
            :class="activeTab === 'available' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'"
          >
            <Package class="size-4" />
            Load Board ({{ availableShipments.length }})
          </button>
          <button
            @click="activeTab = 'assigned'"
            class="px-5 py-3 font-semibold text-sm border-b-2 transition flex items-center gap-2"
            :class="activeTab === 'assigned' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'"
          >
            <Truck class="size-4" />
            My Active Shipments ({{ (assignedShipments || []).length }})
          </button>
        </div>

        <!-- Available Loads Tab -->
        <div v-if="activeTab === 'available'" class="space-y-4">
          <div v-if="availableShipments.length === 0" class="text-center py-16 bg-card border rounded-xl">
            <Package class="size-12 text-muted-foreground mx-auto mb-3 opacity-50" />
            <h3 class="text-lg font-bold text-foreground">No Available Loads Right Now</h3>
            <p class="text-sm text-muted-foreground mt-1">Check back soon for new shipment postings from verified shippers.</p>
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card v-for="s in availableShipments" :key="s.id" class="border hover:border-primary/50 transition shadow-xs flex flex-col justify-between">
              <CardHeader class="pb-3">
                <div class="flex items-start justify-between gap-2">
                  <div>
                    <Badge variant="outline" class="mb-1.5 bg-muted/50 text-xs">{{ s.goods_category }}</Badge>
                    <CardTitle class="text-lg font-bold text-foreground">{{ s.title }}</CardTitle>
                  </div>
                  <div class="text-right">
                    <span class="text-xs text-muted-foreground block">Bidding Range</span>
                    <span class="text-base font-bold text-primary">{{ formatCurrency(s.ai_estimated_min || s.ai_floor_price) }} — {{ formatCurrency(s.ai_estimated_max || s.shipper_budget) }}</span>
                  </div>
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

                <div class="flex items-center justify-between text-xs text-muted-foreground px-1">
                  <span class="flex items-center gap-1"><Truck class="size-3.5 text-primary" /> {{ s.vehicle_type }}</span>
                  <span class="flex items-center gap-1"><Package class="size-3.5 text-primary" /> {{ s.weight_kg }} kg</span>
                  <span class="flex items-center gap-1"><Navigation class="size-3.5 text-primary" /> {{ s.distance_km }} km</span>
                </div>
              </CardContent>
              <CardFooter class="pt-0 flex items-center gap-2">
                <Button variant="outline" class="flex-1 text-xs h-9 font-medium" @click="router.push(`/shipments/${s.id}`)">
                  <ExternalLink class="size-3.5 mr-1" />
                  View Details
                </Button>
                <Button class="flex-1 text-xs h-9 font-semibold" :class="!isVerified && !loadingVerification ? 'bg-muted text-muted-foreground cursor-not-allowed hover:bg-muted' : 'bg-primary hover:bg-primary/90'" @click="openBidDialog(s)">
                  <span v-if="!isVerified && !loadingVerification">Verify to Bid</span>
                  <span v-else class="flex items-center justify-center"><DollarSign class="size-3.5 mr-1" /> Submit Bid</span>
                </Button>
              </CardFooter>
            </Card>
          </div>
        </div>

        <!-- Section 2: Assigned / Active Trips -->
        <div v-else class="space-y-4">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-bold text-foreground flex items-center gap-2">
              <Truck class="size-5 text-primary" />
              Your Assigned Trips
              <Badge variant="secondary" class="ml-1 text-xs">{{ assignedShipments?.length || 0 }}</Badge>
            </h2>
          </div>

          <div v-if="loadingAssigned" class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Skeleton v-for="i in 2" :key="i" class="h-44 w-full rounded-xl" />
          </div>

          <div v-else-if="!assignedShipments || assignedShipments.length === 0" class="text-center py-12 bg-card rounded-xl border border-dashed">
            <Truck class="size-10 text-muted-foreground mx-auto mb-2 opacity-50" />
            <p class="text-sm font-semibold text-foreground">No Active Trips</p>
            <p class="text-xs text-muted-foreground mt-1">When shippers accept your bids, your assigned trips will show up here.</p>
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card v-for="s in assignedShipments" :key="s.id" class="border hover:border-primary/50 transition shadow-xs">
              <CardHeader>
                <div class="flex items-center justify-between">
                  <Badge :class="statusColors[s.status] || 'bg-muted'" class="capitalize font-semibold">{{ s.status.replace('_', ' ') }}</Badge>
                  <span class="text-sm font-bold text-foreground">{{ formatCurrency(s.ai_estimated_min || s.ai_floor_price) }} — {{ formatCurrency(s.ai_estimated_max || s.shipper_budget) }}</span>
                </div>
                <CardTitle class="text-lg font-bold text-foreground mt-2">{{ s.title }}</CardTitle>
              </CardHeader>
              <CardContent class="space-y-3 text-sm">
                <div class="space-y-1.5">
                  <p class="flex items-center gap-2"><MapPin class="size-3.5 text-green-600" /> {{ s.pickup_address }}</p>
                  <p class="flex items-center gap-2"><Navigation class="size-3.5 text-red-600" /> {{ s.dropoff_address }}</p>
                </div>
                <div class="flex items-center gap-2">
                  <Button variant="outline" class="flex-1" @click="router.push(`/shipments/${s.id}`)">
                    <ExternalLink class="size-4 mr-1.5" />
                    View Details
                  </Button>
                  <Button
                    v-if="getNextAction(s.status)"
                    class="flex-1 font-semibold"
                    @click="router.push(`/shipments/${s.id}`)"
                  >
                    {{ getNextAction(s.status)!.label }}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <BidSubmissionDialog
          :open="showBidDialog"
          :shipment="selectedShipment"
          @update:open="showBidDialog = $event"
          @submitted="handleBidSubmitted"
        />
      </template>
    </div>
  </div>
</template>
