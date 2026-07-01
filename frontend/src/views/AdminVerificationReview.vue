<script lang="ts" setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useVerificationList } from '@/composables/useVerificationList'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { LoaderCircle, CheckCircle2, XCircle, Clock, Search, ArrowLeft, ShieldCheck, User, Mail, Phone, Building2, CreditCard, MapPin, Truck, FileText, Eye } from '@lucide/vue'

const router = useRouter()
const { user, loading } = useAuth()

const {
  data: verifications,
  isLoading: loadingData,
  searchQuery,
  activeTab,
  approveMutation,
  rejectMutation,
} = useVerificationList()

const selectedVerification = ref<any>(null)
const showDetailDialog = ref(false)
const showRejectDialog = ref(false)
const rejectReason = ref('')

watch([user, loading], ([u, l]) => {
  if (!l) {
    if (!u) router.replace('/login')
    else if (u.role !== 'admin') router.replace('/')
  }
})

function viewDetails(v: any) {
  selectedVerification.value = v
  showDetailDialog.value = true
}

function approveVerification(id: string) {
  approveMutation.mutate(id, {
    onSuccess: () => { showDetailDialog.value = false },
  })
}

function openRejectDialog() {
  rejectReason.value = ''
  showRejectDialog.value = true
}

function confirmReject() {
  if (!selectedVerification.value) return
  rejectMutation.mutate(
    { id: selectedVerification.value.id, reason: rejectReason.value },
    {
      onSuccess: () => {
        showRejectDialog.value = false
        showDetailDialog.value = false
      },
    },
  )
}

function statusColor(status: string) {
  if (status === 'approved') return 'bg-green-100 text-green-800'
  if (status === 'rejected') return 'bg-red-100 text-red-800'
  return 'bg-yellow-100 text-yellow-800'
}

function roleBadgeColor(role: string) {
  if (role === 'driver') return 'bg-blue-100 text-blue-800'
  if (role === 'shipper') return 'bg-purple-100 text-purple-800'
  return 'bg-gray-100 text-gray-800'
}
</script>

<template>
  <div class="flex-1 p-8 bg-background">
    <div class="max-w-5xl mx-auto">
      <Button variant="ghost" size="sm" class="mb-4" @click="router.push('/admin')">
        <ArrowLeft class="size-4 mr-2" />
        Back to Dashboard
      </Button>

      <div class="mb-6">
        <h1 class="text-3xl font-bold text-foreground">Verification Reviews</h1>
        <p class="text-muted-foreground mt-1">Review and approve user verification submissions.</p>
      </div>

      <div class="flex flex-col sm:flex-row gap-4 mb-6">
        <div class="relative flex-1">
          <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input
            v-model="searchQuery"
            placeholder="Search by name or email..."
            class="pl-9"
          />
        </div>
      </div>

      <Tabs v-model="activeTab" class="mb-6">
        <TabsList>
          <TabsTrigger value="pending">
            <Clock class="size-4 mr-1" />
            Pending
          </TabsTrigger>
          <TabsTrigger value="approved">
            <CheckCircle2 class="size-4 mr-1" />
            Approved
          </TabsTrigger>
          <TabsTrigger value="rejected">
            <XCircle class="size-4 mr-1" />
            Rejected
          </TabsTrigger>
          <TabsTrigger value="all">All</TabsTrigger>
        </TabsList>
      </Tabs>

      <div v-if="loadingData" class="space-y-3">
        <Card v-for="i in 4" :key="i">
          <CardContent class="p-4 flex items-center justify-between">
            <div class="flex items-center gap-4">
              <Skeleton class="w-10 h-10 rounded-full" />
              <div class="space-y-2">
                <Skeleton class="h-4 w-32" />
                <Skeleton class="h-3 w-48" />
              </div>
            </div>
            <div class="flex items-center gap-3">
              <Skeleton class="h-6 w-16" />
              <Skeleton class="h-6 w-20" />
              <Skeleton class="h-8 w-8" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div v-else-if="!verifications || verifications.length === 0" class="text-center py-12">
        <ShieldCheck class="size-12 mx-auto text-muted-foreground/50 mb-4" />
        <p class="text-muted-foreground">No verification submissions found.</p>
      </div>

      <div v-else class="space-y-3">
        <Card
          v-for="v in verifications"
          :key="v.id"
          class="hover:shadow-md transition-shadow cursor-pointer"
          @click="viewDetails(v)"
        >
          <CardContent class="p-4 flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                <span class="text-sm font-semibold text-primary">
                  {{ (v.userName || '?').charAt(0).toUpperCase() }}
                </span>
              </div>
              <div>
                <p class="font-medium text-foreground">{{ v.userName }}</p>
                <p class="text-sm text-muted-foreground">{{ v.userEmail }}</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <Badge :class="roleBadgeColor(v.userRole)" class="capitalize">
                {{ v.userRole }}
              </Badge>
              <Badge :class="statusColor(v.status)" class="capitalize">
                {{ v.status }}
              </Badge>
              <Button variant="ghost" size="sm">
                <Eye class="size-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <Dialog v-model:open="showDetailDialog">
        <DialogContent class="max-w-lg">
          <DialogHeader>
            <DialogTitle>Verification Details</DialogTitle>
            <DialogDescription>
              Review the submitted verification information.
            </DialogDescription>
          </DialogHeader>

          <div v-if="selectedVerification" class="space-y-4">
            <div class="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
              <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                <span class="text-sm font-semibold text-primary">
                  {{ (selectedVerification.userName || '?').charAt(0).toUpperCase() }}
                </span>
              </div>
              <div>
                <p class="font-medium">{{ selectedVerification.userName }}</p>
                <p class="text-sm text-muted-foreground">{{ selectedVerification.userEmail }}</p>
              </div>
              <Badge :class="roleBadgeColor(selectedVerification.userRole)" class="capitalize ml-auto">
                {{ selectedVerification.userRole }}
              </Badge>
            </div>

            <div class="grid grid-cols-2 gap-3 text-sm">
              <template v-if="selectedVerification.userRole === 'driver'">
                <div class="space-y-1">
                  <p class="text-muted-foreground flex items-center gap-1"><CreditCard class="size-3" /> License Number</p>
                  <p class="font-medium">{{ selectedVerification.licenseNumber || '-' }}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-muted-foreground flex items-center gap-1"><Truck class="size-3" /> Vehicle Type</p>
                  <p class="font-medium">{{ selectedVerification.vehicleType || '-' }}</p>
                </div>
                <div class="space-y-1 col-span-2">
                  <p class="text-muted-foreground flex items-center gap-1"><Truck class="size-3" /> Vehicle Number</p>
                  <p class="font-medium">{{ selectedVerification.vehicleNumber || '-' }}</p>
                </div>
              </template>

              <template v-if="selectedVerification.userRole === 'shipper'">
                <div class="space-y-1 col-span-2">
                  <p class="text-muted-foreground flex items-center gap-1"><Building2 class="size-3" /> Business Name</p>
                  <p class="font-medium">{{ selectedVerification.businessName || '-' }}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-muted-foreground flex items-center gap-1"><CreditCard class="size-3" /> GST Number</p>
                  <p class="font-medium">{{ selectedVerification.gstNumber || '-' }}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-muted-foreground flex items-center gap-1"><MapPin class="size-3" /> Company Address</p>
                  <p class="font-medium">{{ selectedVerification.companyAddress || '-' }}</p>
                </div>
              </template>
            </div>

            <div class="flex items-center gap-2">
              <p class="text-sm text-muted-foreground">Status:</p>
              <Badge :class="statusColor(selectedVerification.status)" class="capitalize">
                {{ selectedVerification.status }}
              </Badge>
            </div>

            <div v-if="selectedVerification.rejectionReason" class="p-3 rounded-lg bg-destructive/5 border border-destructive/20">
              <p class="text-sm text-destructive font-medium">Rejection Reason:</p>
              <p class="text-sm text-destructive/80">{{ selectedVerification.rejectionReason }}</p>
            </div>
          </div>

          <DialogFooter v-if="selectedVerification?.status === 'pending'">
            <Button
              variant="outline"
              @click="openRejectDialog"
              :disabled="approveMutation.isPending.value || rejectMutation.isPending.value"
            >
              <XCircle class="size-4 mr-1" />
              Reject
            </Button>
            <Button
              @click="approveVerification(selectedVerification?.id)"
              :disabled="approveMutation.isPending.value || rejectMutation.isPending.value"
            >
              <LoaderCircle v-if="approveMutation.isPending.value" class="size-4 animate-spin" />
              <CheckCircle2 v-else class="size-4 mr-1" />
              Approve
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog v-model:open="showRejectDialog">
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject Verification</DialogTitle>
            <DialogDescription>
              Optionally provide a reason for rejection.
            </DialogDescription>
          </DialogHeader>
          <div class="space-y-4">
            <div class="space-y-2">
              <Label for="rejectReason">Reason (optional)</Label>
              <Input
                id="rejectReason"
                v-model="rejectReason"
                placeholder="e.g., Invalid documents, unclear photos..."
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" @click="showRejectDialog = false">Cancel</Button>
            <Button
              variant="destructive"
              @click="confirmReject"
              :disabled="rejectMutation.isPending.value"
            >
              <LoaderCircle v-if="rejectMutation.isPending.value" class="size-4 animate-spin" />
              Reject
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  </div>
</template>
