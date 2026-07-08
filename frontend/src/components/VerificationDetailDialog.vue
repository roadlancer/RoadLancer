<script lang="ts" setup>
import { ref, watch } from 'vue'
import api from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Skeleton } from '@/components/ui/skeleton'
import {
  LoaderCircle, CheckCircle2, XCircle, Clock, Eye, User, CreditCard, Truck, MapPin,
} from '@lucide/vue'

const props = defineProps<{
  open: boolean
  verification: any
  showActions?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'approve', id: string): void
  (e: 'reject'): void
  (e: 'resetPending', id: string): void
}>()

const selectedVerification = ref<any>(null)
const loadingDetails = ref(false)
const lightboxImage = ref<string | null>(null)
const lightboxTitle = ref('')

watch(
  () => props.verification,
  async (v) => {
    if (v) {
      selectedVerification.value = { ...v }
      loadingDetails.value = true
      try {
        const { data } = await api.get(`/verification/documents/${v.id || v.userId}`)
        selectedVerification.value = { ...selectedVerification.value, ...data }
      } catch (err) {
        console.error('Failed to load verification details', err)
      } finally {
        loadingDetails.value = false
      }
    }
  },
  { immediate: true }
)

function statusColor(status: string) {
  if (status === 'approved') return 'bg-green-100 text-green-800 border-green-200'
  if (status === 'rejected') return 'bg-red-100 text-red-800 border-red-200'
  return 'bg-yellow-100 text-yellow-800 border-yellow-200'
}

function roleBadgeColor(role: string) {
  if (role === 'driver') return 'bg-blue-100 text-blue-800 border-blue-200'
  if (role === 'shipper') return 'bg-purple-100 text-purple-800 border-purple-200'
  return 'bg-gray-100 text-gray-800 border-gray-200'
}

function openLightbox(title: string, src: string) {
  lightboxTitle.value = title
  lightboxImage.value = src
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="sm:max-w-4xl md:max-w-5xl lg:max-w-6xl w-[95vw] max-h-[90vh] overflow-y-auto p-6 sm:p-8">
      <DialogHeader>
        <DialogTitle class="text-xl">Verification Dossier</DialogTitle>
        <DialogDescription>Complete applicant submission and credential check.</DialogDescription>
      </DialogHeader>

      <div v-if="selectedVerification" class="space-y-5 py-2">
        <div class="flex items-center justify-between p-4 rounded-xl bg-muted/40 border">
          <div class="flex items-center gap-3.5">
            <div class="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center font-bold text-lg text-primary border border-primary/20">
              {{ (selectedVerification.userName || '?').charAt(0).toUpperCase() }}
            </div>
            <div>
              <h3 class="font-bold text-base text-foreground">{{ selectedVerification.userName }}</h3>
              <p class="text-xs text-muted-foreground">{{ selectedVerification.userEmail }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <Badge :class="roleBadgeColor(selectedVerification.userRole)" class="capitalize px-3 py-1 font-semibold border">
              {{ selectedVerification.userRole }}
            </Badge>
            <Badge :class="statusColor(selectedVerification.status)" class="capitalize px-3 py-1 font-semibold border">
              {{ selectedVerification.status }}
            </Badge>
          </div>
        </div>

        <div v-if="loadingDetails" class="space-y-3 py-4">
          <Skeleton class="h-6 w-48" />
          <div class="grid grid-cols-2 gap-3"><Skeleton class="h-16" /><Skeleton class="h-16" /></div>
        </div>

        <template v-else>
          <div class="space-y-2.5">
            <h4 class="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <User class="size-3.5" /> Identity & Contact Credentials
            </h4>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 p-3.5 rounded-lg border bg-card text-xs">
              <div>
                <span class="text-muted-foreground block">Full Legal Name</span>
                <strong class="font-semibold text-sm">{{ selectedVerification.fullName || selectedVerification.userName }}</strong>
              </div>
              <div>
                <span class="text-muted-foreground block">Aadhaar Last 4</span>
                <strong class="font-semibold text-sm">{{ selectedVerification.aadhaarLast4 ? `XXXX-XXXX-${selectedVerification.aadhaarLast4}` : '-' }}</strong>
              </div>
              <div>
                <span class="text-muted-foreground block">Phone Contact</span>
                <strong class="font-semibold text-sm">{{ selectedVerification.phone || '-' }}</strong>
              </div>
              <div v-if="selectedVerification.fatherName">
                <span class="text-muted-foreground block">Father's Name</span>
                <strong class="font-semibold text-sm">{{ selectedVerification.fatherName }}</strong>
              </div>
              <div v-if="selectedVerification.dateOfBirth">
                <span class="text-muted-foreground block">Date of Birth</span>
                <strong class="font-semibold text-sm">{{ selectedVerification.dateOfBirth.split('T')[0] }}</strong>
              </div>
              <div v-if="selectedVerification.bloodGroup">
                <span class="text-muted-foreground block">Blood Group</span>
                <strong class="font-semibold text-sm">{{ selectedVerification.bloodGroup }}</strong>
              </div>
              <div v-if="selectedVerification.address" class="col-span-2 sm:col-span-3">
                <span class="text-muted-foreground block">Address</span>
                <strong class="font-semibold">{{ selectedVerification.address }}</strong>
              </div>
              <div v-if="selectedVerification.emergencyContactName" class="col-span-2 sm:col-span-3 pt-2 border-t mt-1">
                <span class="text-muted-foreground block">Emergency Contact</span>
                <strong class="font-semibold">{{ selectedVerification.emergencyContactName }} ({{ selectedVerification.emergencyContactPhone }})</strong>
              </div>
            </div>
          </div>

          <div v-if="selectedVerification.userRole === 'driver'" class="space-y-4">
            <div class="space-y-2.5">
              <h4 class="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                <CreditCard class="size-3.5" /> Driving License Details
              </h4>
              <div class="grid grid-cols-3 gap-3 p-3.5 rounded-lg border bg-card text-xs">
                <div>
                  <span class="text-muted-foreground block">DL Number</span>
                  <strong class="font-semibold text-sm">{{ selectedVerification.licenseNumber || '-' }}</strong>
                </div>
                <div>
                  <span class="text-muted-foreground block">Category</span>
                  <strong class="font-semibold text-sm">{{ selectedVerification.dlCategory || 'LMV' }}</strong>
                </div>
                <div>
                  <span class="text-muted-foreground block">Expiry Date</span>
                  <strong class="font-semibold text-sm">{{ selectedVerification.dlExpiryDate ? selectedVerification.dlExpiryDate.split('T')[0] : '-' }}</strong>
                </div>
              </div>
            </div>

            <div class="space-y-2.5">
              <h4 class="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                <Truck class="size-3.5" /> Vehicle & Compliance
              </h4>
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 p-3.5 rounded-lg border bg-card text-xs">
                <div>
                  <span class="text-muted-foreground block">Registration No.</span>
                  <strong class="font-semibold text-sm">{{ selectedVerification.vehicleRegNumber || selectedVerification.vehicleNumber || '-' }}</strong>
                </div>
                <div>
                  <span class="text-muted-foreground block">Type</span>
                  <strong class="font-semibold text-sm">{{ selectedVerification.vehicleType || '-' }}</strong>
                </div>
                <div>
                  <span class="text-muted-foreground block">Make / Model</span>
                  <strong class="font-semibold text-sm">{{ selectedVerification.vehicleMakeModel || '-' }}</strong>
                </div>
                <div v-if="selectedVerification.insurancePolicyNumber">
                  <span class="text-muted-foreground block">Insurance Policy</span>
                  <strong class="font-semibold">{{ selectedVerification.insurancePolicyNumber }} ({{ selectedVerification.insuranceProvider }})</strong>
                </div>
                <div v-if="selectedVerification.pucCertificateNumber">
                  <span class="text-muted-foreground block">PUC Certificate</span>
                  <strong class="font-semibold">{{ selectedVerification.pucCertificateNumber }}</strong>
                </div>
              </div>
            </div>
          </div>

          <div v-if="selectedVerification.userRole === 'shipper'" class="space-y-2.5">
            <h4 class="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <MapPin class="size-3.5" /> Enterprise & Taxation Credentials
            </h4>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 p-3.5 rounded-lg border bg-card text-xs">
              <div class="col-span-2">
                <span class="text-muted-foreground block">Business Legal Name</span>
                <strong class="font-semibold text-sm">{{ selectedVerification.businessName || '-' }}</strong>
              </div>
              <div>
                <span class="text-muted-foreground block">Constitution</span>
                <strong class="font-semibold text-sm">{{ selectedVerification.businessType || 'Pvt Ltd' }}</strong>
              </div>
              <div>
                <span class="text-muted-foreground block">GST Number</span>
                <strong class="font-semibold text-sm">{{ selectedVerification.gstNumber || '-' }}</strong>
              </div>
              <div>
                <span class="text-muted-foreground block">PAN Number</span>
                <strong class="font-semibold text-sm">{{ selectedVerification.panNumber || '-' }}</strong>
              </div>
              <div>
                <span class="text-muted-foreground block">Turnover / Years</span>
                <strong class="font-semibold text-sm">{{ selectedVerification.annualTurnover || '-' }} ({{ selectedVerification.yearsInBusiness || 1 }} yrs)</strong>
              </div>
              <div class="col-span-2 sm:col-span-3">
                <span class="text-muted-foreground block">Registered Address</span>
                <strong class="font-semibold">{{ selectedVerification.registeredAddress || selectedVerification.companyAddress || '-' }}</strong>
              </div>
            </div>
          </div>

          <div class="space-y-2.5 pt-2">
            <h4 class="text-xs font-bold uppercase tracking-wider text-muted-foreground">Attached Document Files (Click to inspect)</h4>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div
                v-if="selectedVerification.profilePhoto"
                @click="openLightbox('Profile Photo', selectedVerification.profilePhoto)"
                class="border rounded-lg p-2 cursor-pointer hover:border-primary transition-all bg-card text-center space-y-1.5 shadow-2xs"
              >
                <img :src="selectedVerification.profilePhoto" class="h-20 w-full object-cover rounded" />
                <span class="text-xs font-medium block truncate">Profile Photo</span>
              </div>
              <div
                v-if="selectedVerification.aadhaarPhoto"
                @click="openLightbox('Aadhaar Photo', selectedVerification.aadhaarPhoto)"
                class="border rounded-lg p-2 cursor-pointer hover:border-primary transition-all bg-card text-center space-y-1.5 shadow-2xs"
              >
                <img :src="selectedVerification.aadhaarPhoto" class="h-20 w-full object-cover rounded" />
                <span class="text-xs font-medium block truncate">Aadhaar Photo</span>
              </div>
              <div
                v-if="selectedVerification.dlPhoto"
                @click="openLightbox('Driving License Photo', selectedVerification.dlPhoto)"
                class="border rounded-lg p-2 cursor-pointer hover:border-primary transition-all bg-card text-center space-y-1.5 shadow-2xs"
              >
                <img :src="selectedVerification.dlPhoto" class="h-20 w-full object-cover rounded" />
                <span class="text-xs font-medium block truncate">DL Photo</span>
              </div>
              <div
                v-if="selectedVerification.rcBookPhoto"
                @click="openLightbox('RC Book Photo', selectedVerification.rcBookPhoto)"
                class="border rounded-lg p-2 cursor-pointer hover:border-primary transition-all bg-card text-center space-y-1.5 shadow-2xs"
              >
                <img :src="selectedVerification.rcBookPhoto" class="h-20 w-full object-cover rounded" />
                <span class="text-xs font-medium block truncate">RC Book Photo</span>
              </div>
              <div
                v-if="selectedVerification.insurancePhoto"
                @click="openLightbox('Insurance Policy Photo', selectedVerification.insurancePhoto)"
                class="border rounded-lg p-2 cursor-pointer hover:border-primary transition-all bg-card text-center space-y-1.5 shadow-2xs"
              >
                <img :src="selectedVerification.insurancePhoto" class="h-20 w-full object-cover rounded" />
                <span class="text-xs font-medium block truncate">Insurance Photo</span>
              </div>
              <div
                v-if="selectedVerification.gstCertPhoto"
                @click="openLightbox('GST Certificate Photo', selectedVerification.gstCertPhoto)"
                class="border rounded-lg p-2 cursor-pointer hover:border-primary transition-all bg-card text-center space-y-1.5 shadow-2xs"
              >
                <img :src="selectedVerification.gstCertPhoto" class="h-20 w-full object-cover rounded" />
                <span class="text-xs font-medium block truncate">GST Certificate</span>
              </div>
              <div
                v-if="selectedVerification.panCardPhoto"
                @click="openLightbox('PAN Card Photo', selectedVerification.panCardPhoto)"
                class="border rounded-lg p-2 cursor-pointer hover:border-primary transition-all bg-card text-center space-y-1.5 shadow-2xs"
              >
                <img :src="selectedVerification.panCardPhoto" class="h-20 w-full object-cover rounded" />
                <span class="text-xs font-medium block truncate">PAN Card</span>
              </div>
            </div>
          </div>
        </template>

        <div v-if="selectedVerification.rejectionReason" class="p-3.5 rounded-xl bg-destructive/10 border border-destructive/20 mt-3">
          <p class="text-xs font-bold uppercase tracking-wider text-destructive">Rejection Verdict:</p>
          <p class="text-sm text-destructive mt-1">{{ selectedVerification.rejectionReason }}</p>
        </div>
      </div>

      <DialogFooter class="gap-2 pt-4 border-t flex flex-col sm:flex-row sm:justify-between items-center w-full">
        <Button
          v-if="showActions && selectedVerification?.status !== 'pending'"
          variant="outline"
          size="sm"
          class="text-amber-700 border-amber-300 hover:bg-amber-50 w-full sm:w-auto"
          @click="emit('resetPending', selectedVerification?.id)"
        >
          <Clock class="size-4 mr-1.5" />
          Reset to Pending
        </Button>
        <div v-else-if="showActions" class="flex gap-2 w-full sm:w-auto justify-end ml-auto">
          <Button
            variant="outline"
            class="border-destructive text-destructive hover:bg-destructive/10"
            @click="emit('reject')"
          >
            <XCircle class="size-4 mr-1.5" />
            Reject Application
          </Button>
          <Button
            @click="emit('approve', selectedVerification?.id)"
            class="bg-green-600 hover:bg-green-700 text-white"
          >
            <CheckCircle2 class="size-4 mr-1.5" />
            Approve Verification
          </Button>
        </div>
        <Button v-else variant="outline" @click="emit('update:open', false)">Close</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>

  <Dialog :open="!!lightboxImage" @update:open="lightboxImage = null">
    <DialogContent class="sm:max-w-4xl md:max-w-5xl lg:max-w-6xl w-[95vw] max-h-[94vh] p-4 bg-background">
      <DialogHeader>
        <DialogTitle>{{ lightboxTitle }}</DialogTitle>
      </DialogHeader>
      <div class="flex items-center justify-center max-h-[75vh] overflow-hidden bg-muted/30 rounded-lg p-2">
        <img v-if="lightboxImage" :src="lightboxImage" class="max-w-full max-h-[72vh] object-contain rounded" />
      </div>
    </DialogContent>
  </Dialog>
</template>
