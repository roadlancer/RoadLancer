<script lang="ts" setup>
import { reactive, watch, computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { z } from 'zod'
import { useAuth } from '@/composables/useAuth'
import { useVerificationStatus, useSubmitVerification } from '@/composables/useVerificationStatus'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import FileUpload from '@/components/FileUpload.vue'
import {
  LoaderCircle, CheckCircle2, XCircle, Clock, ShieldCheck, ArrowLeft,
  FileText, ChevronDown, ChevronUp
} from '@lucide/vue'
import SupportEmailSimulatorModal from '@/components/SupportEmailSimulatorModal.vue'

const router = useRouter()
const { user, loading } = useAuth()

const { data: verification, isLoading: loadingStatus } = useVerificationStatus(true)
const submitMutation = useSubmitVerification()

const verificationStatus = computed(() => verification.value?.status ?? 'none')
const verificationData = computed(() => verification.value?.verification ?? null)
const isEditingProfile = ref(false)
const editReasonText = ref('')
const supportModalOpen = ref(false)

function onTicketGenerated(ticketNum: string) {
  editReasonText.value = `Ticket #${ticketNum} - Profile edit request submitted via support email`
}

const isLocked = computed(() => !isEditingProfile.value && (verificationStatus.value === 'approved' || verificationStatus.value === 'pending'))

const activeDriverSection = ref(1)
const activeShipperSection = ref(1)

const driverForm = reactive({
  fullName: '',
  fatherName: '',
  dateOfBirth: '',
  bloodGroup: 'B+',
  aadhaarLast4: '',
  address: '',
  phone: '',
  emergencyContactName: '',
  emergencyContactPhone: '',
  profilePhoto: null as string | null,
  aadhaarPhoto: null as string | null,

  licenseNumber: '',
  dlExpiryDate: '',
  dlCategory: 'LMV',
  dlPhoto: null as string | null,

  vehicleRegNumber: '',
  vehicleType: 'Truck',
  vehicleMakeModel: '',
  vehicleYear: new Date().getFullYear(),
  rcBookPhoto: null as string | null,

  insurancePolicyNumber: '',
  insuranceProvider: '',
  insuranceExpiryDate: '',
  insurancePhoto: null as string | null,
  pucCertificateNumber: '',
  pucExpiryDate: '',
})

const shipperForm = reactive({
  fullName: '',
  aadhaarLast4: '',
  phone: '',
  emergencyContactName: '',
  emergencyContactPhone: '',
  profilePhoto: null as string | null,
  aadhaarPhoto: null as string | null,

  businessName: '',
  businessType: 'Pvt Ltd',
  gstNumber: '',
  panNumber: '',
  registeredAddress: '',
  annualTurnover: '10L-50L',
  yearsInBusiness: 1,
  primaryGoodsCategory: '',
  gstCertPhoto: null as string | null,
  panCardPhoto: null as string | null,
  businessRegPhoto: null as string | null,
})

const driverErrors = reactive<Record<string, string>>({})
const shipperErrors = reactive<Record<string, string>>({})

const driverSchema = z.object({
  fullName: z.string().min(2, 'Full name is required'),
  fatherName: z.string().min(2, "Father's name is required"),
  dateOfBirth: z.string().min(10, 'Date of birth is required'),
  aadhaarLast4: z.string().length(4, 'Enter exact last 4 digits of Aadhaar'),
  address: z.string().min(10, 'Complete address is required'),
  phone: z.string().length(10, 'Phone must be exactly 10 digits'),
  emergencyContactName: z.string().min(2, 'Emergency contact name required'),
  emergencyContactPhone: z.string().length(10, 'Emergency phone must be 10 digits'),

  licenseNumber: z.string().min(6, 'Driving license number required'),
  dlExpiryDate: z.string().min(10, 'DL expiry date required'),
  vehicleRegNumber: z.string().min(4, 'Vehicle registration number required'),
  vehicleMakeModel: z.string().min(2, 'Make & model required'),
  insurancePolicyNumber: z.string().min(4, 'Insurance policy number required'),
  insuranceProvider: z.string().min(2, 'Insurance provider required'),
  pucCertificateNumber: z.string().min(3, 'PUC number required'),
})

const shipperSchema = z.object({
  fullName: z.string().min(2, 'Authorized person name required'),
  aadhaarLast4: z.string().length(4, 'Enter exact last 4 digits of Aadhaar'),
  phone: z.string().length(10, 'Phone must be exactly 10 digits'),
  emergencyContactName: z.string().min(2, 'Emergency contact name required'),
  emergencyContactPhone: z.string().length(10, 'Emergency phone must be 10 digits'),

  businessName: z.string().min(2, 'Business name required'),
  gstNumber: z.string().min(15, 'GST number must be 15 characters'),
  panNumber: z.string().length(10, 'PAN number must be 10 characters'),
  registeredAddress: z.string().min(10, 'Registered address required'),
  primaryGoodsCategory: z.string().min(2, 'Goods category required'),
})

watch([verificationData, user], ([data, u]) => {
  if (!u) return
  if (u.role === 'driver') {
    Object.assign(driverForm, {
      fullName: data?.fullName || u.name || '',
      fatherName: data?.fatherName || '',
      dateOfBirth: data?.dateOfBirth ? data.dateOfBirth.split('T')[0] : '',
      bloodGroup: data?.bloodGroup || 'B+',
      aadhaarLast4: data?.aadhaarLast4 || '',
      address: data?.address || '',
      phone: data?.phone || u.phone || '',
      emergencyContactName: data?.emergencyContactName || '',
      emergencyContactPhone: data?.emergencyContactPhone || '',
      profilePhoto: data?.profilePhoto || null,
      aadhaarPhoto: data?.aadhaarPhoto || null,

      licenseNumber: data?.licenseNumber || '',
      dlExpiryDate: data?.dlExpiryDate ? data.dlExpiryDate.split('T')[0] : '',
      dlCategory: data?.dlCategory || 'LMV',
      dlPhoto: data?.dlPhoto || null,

      vehicleRegNumber: data?.vehicleRegNumber || '',
      vehicleType: data?.vehicleType || 'Truck',
      vehicleMakeModel: data?.vehicleMakeModel || '',
      vehicleYear: data?.vehicleYear || new Date().getFullYear(),
      rcBookPhoto: data?.rcBookPhoto || null,

      insurancePolicyNumber: data?.insurancePolicyNumber || '',
      insuranceProvider: data?.insuranceProvider || '',
      insuranceExpiryDate: data?.insuranceExpiryDate ? data.insuranceExpiryDate.split('T')[0] : '',
      insurancePhoto: data?.insurancePhoto || null,
      pucCertificateNumber: data?.pucCertificateNumber || '',
      pucExpiryDate: data?.pucExpiryDate ? data.pucExpiryDate.split('T')[0] : '',
    })
  } else {
    Object.assign(shipperForm, {
      fullName: data?.fullName || u.name || '',
      aadhaarLast4: data?.aadhaarLast4 || '',
      phone: data?.phone || u.phone || '',
      emergencyContactName: data?.emergencyContactName || '',
      emergencyContactPhone: data?.emergencyContactPhone || '',
      profilePhoto: data?.profilePhoto || null,
      aadhaarPhoto: data?.aadhaarPhoto || null,

      businessName: data?.businessName || '',
      businessType: data?.businessType || 'Pvt Ltd',
      gstNumber: data?.gstNumber || '',
      panNumber: data?.panNumber || '',
      registeredAddress: data?.registeredAddress || '',
      annualTurnover: data?.annualTurnover || '10L-50L',
      yearsInBusiness: data?.yearsInBusiness || 1,
      primaryGoodsCategory: data?.primaryGoodsCategory || '',
      gstCertPhoto: data?.gstCertPhoto || null,
      panCardPhoto: data?.panCardPhoto || null,
      businessRegPhoto: data?.businessRegPhoto || null,
    })
  }
}, { immediate: true })

function validateDriver() {
  Object.keys(driverErrors).forEach(k => delete driverErrors[k])
  const result = driverSchema.safeParse(driverForm)
  if (!result.success) {
    for (const issue of result.error.issues) {
      const field = issue.path[0] as string
      if (!driverErrors[field]) driverErrors[field] = issue.message
    }
    return false
  }
  return true
}

function validateShipper() {
  Object.keys(shipperErrors).forEach(k => delete shipperErrors[k])
  const result = shipperSchema.safeParse(shipperForm)
  if (!result.success) {
    for (const issue of result.error.issues) {
      const field = issue.path[0] as string
      if (!shipperErrors[field]) shipperErrors[field] = issue.message
    }
    return false
  }
  return true
}

function handleSubmit() {
  const isDriver = user.value?.role === 'driver'
  if (isDriver ? !validateDriver() : !validateShipper()) return

  if (isEditingProfile.value && !editReasonText.value.trim()) {
    alert('Please enter a support ticket reference or reason for your profile edit request.')
    return
  }

  const endpoint = isDriver ? '/verification/submit/driver' : '/verification/submit/shipper'
  const body = {
    ...(isDriver ? driverForm : shipperForm),
    isEditRequest: isEditingProfile.value,
    editReason: isEditingProfile.value ? editReasonText.value : undefined,
  }

  submitMutation.mutate({ endpoint, body }, {
    onSuccess: () => {
      isEditingProfile.value = false
      editReasonText.value = ''
      goBack()
    }
  })
}

function goBack() {
  const role = user.value?.role
  if (role === 'driver') router.push('/driver')
  else if (role === 'shipper') router.push('/shipper')
  else router.push('/')
}

watch([user, loading], ([u, l]) => {
  if (!l) {
    if (!u) router.replace('/login')
    else if (u.role !== 'driver' && u.role !== 'shipper') router.replace('/')
  }
})
</script>

<template>
  <div class="flex-1 p-6 md:p-8 bg-background">
    <div class="max-w-3xl mx-auto">
      <div v-if="loading || loadingStatus" class="space-y-6">
        <Skeleton class="h-9 w-40" />
        <Skeleton class="h-10 w-64" />
        <Skeleton class="h-48 w-full" />
        <Skeleton class="h-48 w-full" />
      </div>

      <template v-else-if="user?.role === 'driver' || user?.role === 'shipper'">
        <Button variant="ghost" size="sm" class="mb-4" @click="goBack">
          <ArrowLeft class="size-4 mr-2" />
          Back to Dashboard
        </Button>

        <div class="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 class="text-3xl font-bold text-foreground flex items-center gap-2.5">
              <ShieldCheck class="size-8 text-primary" />
              Get Validated
            </h1>
            <p class="text-muted-foreground mt-1">
              Complete your profile & document verification to access platform features.
            </p>
          </div>
        </div>

        <div v-if="verificationStatus === 'approved'" class="mb-6 space-y-4">
          <Alert class="border-green-200 bg-green-50 text-green-800 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div class="flex items-center">
              <CheckCircle2 class="h-5 w-5 text-green-600 shrink-0" />
              <AlertDescription class="text-green-700 ml-2">
                <strong class="font-semibold">Verification Approved!</strong> Your identity and documents have been verified. You now have unrestricted platform access.
              </AlertDescription>
            </div>
            <Button
              v-if="!isEditingProfile"
              variant="outline"
              size="sm"
              class="border-green-300 text-green-900 bg-white hover:bg-green-100 shrink-0 self-start sm:self-center"
              @click="isEditingProfile = true"
            >
              Request Profile Edit / Update
            </Button>
          </Alert>

          <Alert v-if="isEditingProfile" class="border-blue-200 bg-blue-50 text-blue-900 shadow-xs space-y-3">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <FileText class="h-5 w-5 text-blue-600 shrink-0" />
                <span class="font-semibold text-blue-900 ml-2">Profile Edit Request (Requires Admin Re-verification)</span>
              </div>
              <Button variant="ghost" size="sm" class="h-7 px-2 text-blue-800 hover:bg-blue-100" @click="isEditingProfile = false">
                Cancel Edit
              </Button>
            </div>
            <p class="text-sm text-blue-800">
              For compliance and auditability, modifying verified profile details requires submitting a support ticket / explanation. An Admin will review and verify your updated credentials.
            </p>
            <div class="space-y-1.5 pt-1">
              <div class="flex items-center justify-between flex-wrap gap-2">
                <Label class="text-xs font-bold uppercase tracking-wider text-blue-900">Support Ticket Reference / Reason for Edit *</Label>
                <button
                  type="button"
                  @click="supportModalOpen = true"
                  class="text-xs font-extrabold text-teal-800 bg-teal-100 hover:bg-teal-200 px-2.5 py-1 rounded-md transition-all flex items-center gap-1 shadow-xs border border-teal-300"
                >
                  <span>📧</span> Generate Ticket via Email Simulator
                </button>
              </div>
              <Input
                v-model="editReasonText"
                placeholder="e.g., Ticket #TICK-1042 - Updated vehicle registration number..."
                class="bg-white border-blue-300 focus-visible:ring-blue-500 h-9 font-medium"
              />
            </div>
          </Alert>
        </div>

        <div v-else-if="verificationStatus === 'rejected'" class="mb-6">
          <Alert variant="destructive" class="shadow-xs">
            <XCircle class="h-5 w-5" />
            <AlertDescription class="ml-2">
              <strong class="font-semibold">Verification Rejected.</strong>
              {{ verificationData?.rejectionReason ? `Reason: ${verificationData.rejectionReason}` : 'Please check your details and document attachments, then resubmit.' }}
            </AlertDescription>
          </Alert>
        </div>

        <div v-else-if="verificationStatus === 'pending'" class="mb-6">
          <Alert class="border-yellow-200 bg-yellow-50 text-yellow-800 shadow-xs">
            <Clock class="h-5 w-5 text-yellow-600" />
            <AlertDescription class="text-yellow-700 ml-2">
              <strong class="font-semibold">Under Review.</strong> Your verification form and attached documents are currently being inspected by our verification team.
            </AlertDescription>
          </Alert>
        </div>

        <Alert v-if="submitMutation.isError.value" variant="destructive" class="mb-6">
          <AlertDescription>{{ (submitMutation.error.value as any)?.response?.data?.detail || 'Something went wrong while submitting.' }}</AlertDescription>
        </Alert>

        <Alert v-if="submitMutation.isSuccess.value" class="mb-6 border-green-200 bg-green-50 text-green-800">
          <CheckCircle2 class="h-4 w-4 text-green-600" />
          <AlertDescription class="text-green-700">
            Verification submitted successfully! An admin will review your credentials.
          </AlertDescription>
        </Alert>

        <!-- DRIVER FORM -->
        <form v-if="user?.role === 'driver'" @submit.prevent="handleSubmit" class="space-y-4" novalidate>
          <!-- Section 1: Personal Information -->
          <Card class="border shadow-xs overflow-hidden transition-all">
            <CardHeader
              class="cursor-pointer bg-muted/30 select-none flex flex-row items-center justify-between p-4"
              @click="activeDriverSection = activeDriverSection === 1 ? 0 : 1"
            >
              <div class="flex items-center gap-2.5">
                <div class="size-8 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-sm">1</div>
                <div>
                  <CardTitle class="text-base font-semibold">Personal Information</CardTitle>
                  <CardDescription class="text-xs">Identity, address, and emergency contact details</CardDescription>
                </div>
              </div>
              <component :is="activeDriverSection === 1 ? ChevronUp : ChevronDown" class="size-5 text-muted-foreground" />
            </CardHeader>

            <CardContent v-show="activeDriverSection === 1" class="p-6 space-y-4 border-t">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-1.5">
                  <Label for="d-fullname">Full Name *</Label>
                  <Input id="d-fullname" v-model="driverForm.fullName" :disabled="isLocked" :class="{ 'border-destructive': driverErrors.fullName }" placeholder="Rajesh Kumar" />
                  <p v-if="driverErrors.fullName" class="text-xs text-destructive">{{ driverErrors.fullName }}</p>
                </div>

                <div class="space-y-1.5">
                  <Label for="d-fathername">Father's Name *</Label>
                  <Input id="d-fathername" v-model="driverForm.fatherName" :disabled="isLocked" :class="{ 'border-destructive': driverErrors.fatherName }" placeholder="Suresh Kumar" />
                  <p v-if="driverErrors.fatherName" class="text-xs text-destructive">{{ driverErrors.fatherName }}</p>
                </div>

                <div class="space-y-1.5">
                  <Label for="d-dob">Date of Birth *</Label>
                  <Input id="d-dob" type="date" v-model="driverForm.dateOfBirth" :disabled="isLocked" :class="{ 'border-destructive': driverErrors.dateOfBirth }" />
                  <p v-if="driverErrors.dateOfBirth" class="text-xs text-destructive">{{ driverErrors.dateOfBirth }}</p>
                </div>

                <div class="space-y-1.5">
                  <Label for="d-blood">Blood Group</Label>
                  <select id="d-blood" v-model="driverForm.bloodGroup" :disabled="isLocked" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                    <option v-for="bg in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']" :key="bg" :value="bg">{{ bg }}</option>
                  </select>
                </div>

                <div class="space-y-1.5">
                  <Label for="d-aadhaar">Aadhaar Last 4 Digits *</Label>
                  <Input id="d-aadhaar" v-model="driverForm.aadhaarLast4" maxlength="4" :disabled="isLocked" :class="{ 'border-destructive': driverErrors.aadhaarLast4 }" placeholder="1234" />
                  <p v-if="driverErrors.aadhaarLast4" class="text-xs text-destructive">{{ driverErrors.aadhaarLast4 }}</p>
                </div>

                <div class="space-y-1.5">
                  <Label for="d-phone">Phone Number *</Label>
                  <Input id="d-phone" v-model="driverForm.phone" maxlength="10" :disabled="isLocked" :class="{ 'border-destructive': driverErrors.phone }" placeholder="9876543210" />
                  <p v-if="driverErrors.phone" class="text-xs text-destructive">{{ driverErrors.phone }}</p>
                </div>
              </div>

              <div class="space-y-1.5">
                <Label for="d-address">Complete Residential Address *</Label>
                <Input id="d-address" v-model="driverForm.address" :disabled="isLocked" :class="{ 'border-destructive': driverErrors.address }" placeholder="Flat / House No, Street, Landmark, City, State, Pincode" />
                <p v-if="driverErrors.address" class="text-xs text-destructive">{{ driverErrors.address }}</p>
              </div>

              <Separator class="my-2" />
              <h4 class="text-sm font-semibold text-foreground">Emergency Contact</h4>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-1.5">
                  <Label for="d-ecname">Contact Person Name *</Label>
                  <Input id="d-ecname" v-model="driverForm.emergencyContactName" :disabled="isLocked" :class="{ 'border-destructive': driverErrors.emergencyContactName }" placeholder="Relative / Friend Name" />
                  <p v-if="driverErrors.emergencyContactName" class="text-xs text-destructive">{{ driverErrors.emergencyContactName }}</p>
                </div>

                <div class="space-y-1.5">
                  <Label for="d-ecphone">Contact Phone *</Label>
                  <Input id="d-ecphone" v-model="driverForm.emergencyContactPhone" maxlength="10" :disabled="isLocked" :class="{ 'border-destructive': driverErrors.emergencyContactPhone }" placeholder="9123456789" />
                  <p v-if="driverErrors.emergencyContactPhone" class="text-xs text-destructive">{{ driverErrors.emergencyContactPhone }}</p>
                </div>
              </div>

              <Separator class="my-2" />
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FileUpload v-model="driverForm.profilePhoto" label="Profile Photo" :disabled="isLocked" />
                <FileUpload v-model="driverForm.aadhaarPhoto" label="Aadhaar Card Photo (Front)" :disabled="isLocked" />
              </div>

              <div class="flex justify-end pt-2">
                <Button type="button" variant="outline" @click="activeDriverSection = 2">Next: Driving License &rarr;</Button>
              </div>
            </CardContent>
          </Card>

          <!-- Section 2: Driving License -->
          <Card class="border shadow-xs overflow-hidden transition-all">
            <CardHeader
              class="cursor-pointer bg-muted/30 select-none flex flex-row items-center justify-between p-4"
              @click="activeDriverSection = activeDriverSection === 2 ? 0 : 2"
            >
              <div class="flex items-center gap-2.5">
                <div class="size-8 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-sm">2</div>
                <div>
                  <CardTitle class="text-base font-semibold">Driving License Details</CardTitle>
                  <CardDescription class="text-xs">License number, validity, and photo upload</CardDescription>
                </div>
              </div>
              <component :is="activeDriverSection === 2 ? ChevronUp : ChevronDown" class="size-5 text-muted-foreground" />
            </CardHeader>

            <CardContent v-show="activeDriverSection === 2" class="p-6 space-y-4 border-t">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="space-y-1.5">
                  <Label for="d-dlnum">License Number *</Label>
                  <Input id="d-dlnum" v-model="driverForm.licenseNumber" :disabled="isLocked" :class="{ 'border-destructive': driverErrors.licenseNumber }" placeholder="MH1220190012345" />
                  <p v-if="driverErrors.licenseNumber" class="text-xs text-destructive">{{ driverErrors.licenseNumber }}</p>
                </div>

                <div class="space-y-1.5">
                  <Label for="d-dlexp">DL Expiry Date *</Label>
                  <Input id="d-dlexp" type="date" v-model="driverForm.dlExpiryDate" :disabled="isLocked" :class="{ 'border-destructive': driverErrors.dlExpiryDate }" />
                  <p v-if="driverErrors.dlExpiryDate" class="text-xs text-destructive">{{ driverErrors.dlExpiryDate }}</p>
                </div>

                <div class="space-y-1.5">
                  <Label for="d-dlcat">Vehicle Category</Label>
                  <select id="d-dlcat" v-model="driverForm.dlCategory" :disabled="isLocked" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                    <option v-for="cat in ['LMV', 'HMV', 'HPMV', 'HTV']" :key="cat" :value="cat">{{ cat }}</option>
                  </select>
                </div>
              </div>

              <FileUpload v-model="driverForm.dlPhoto" label="Driving License Photo (Front)" :disabled="isLocked" />

              <div class="flex justify-between pt-2">
                <Button type="button" variant="ghost" @click="activeDriverSection = 1">&larr; Previous</Button>
                <Button type="button" variant="outline" @click="activeDriverSection = 3">Next: Vehicle Details &rarr;</Button>
              </div>
            </CardContent>
          </Card>

          <!-- Section 3: Vehicle Details -->
          <Card class="border shadow-xs overflow-hidden transition-all">
            <CardHeader
              class="cursor-pointer bg-muted/30 select-none flex flex-row items-center justify-between p-4"
              @click="activeDriverSection = activeDriverSection === 3 ? 0 : 3"
            >
              <div class="flex items-center gap-2.5">
                <div class="size-8 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-sm">3</div>
                <div>
                  <CardTitle class="text-base font-semibold">Vehicle Specification</CardTitle>
                  <CardDescription class="text-xs">Registration number, make, model, and RC Book</CardDescription>
                </div>
              </div>
              <component :is="activeDriverSection === 3 ? ChevronUp : ChevronDown" class="size-5 text-muted-foreground" />
            </CardHeader>

            <CardContent v-show="activeDriverSection === 3" class="p-6 space-y-4 border-t">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-1.5">
                  <Label for="d-vehreg">Registration Number *</Label>
                  <Input id="d-vehreg" v-model="driverForm.vehicleRegNumber" :disabled="isLocked" :class="{ 'border-destructive': driverErrors.vehicleRegNumber }" placeholder="MH-12-AB-1234" />
                  <p v-if="driverErrors.vehicleRegNumber" class="text-xs text-destructive">{{ driverErrors.vehicleRegNumber }}</p>
                </div>

                <div class="space-y-1.5">
                  <Label for="d-vehtype">Vehicle Type</Label>
                  <select id="d-vehtype" v-model="driverForm.vehicleType" :disabled="isLocked" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                    <option v-for="vt in ['Truck', 'Container', 'Tanker', 'Trailer', 'Mini Truck']" :key="vt" :value="vt">{{ vt }}</option>
                  </select>
                </div>

                <div class="space-y-1.5">
                  <Label for="d-vehmake">Make & Model *</Label>
                  <Input id="d-vehmake" v-model="driverForm.vehicleMakeModel" :disabled="isLocked" :class="{ 'border-destructive': driverErrors.vehicleMakeModel }" placeholder="Tata Prima 4928.S" />
                  <p v-if="driverErrors.vehicleMakeModel" class="text-xs text-destructive">{{ driverErrors.vehicleMakeModel }}</p>
                </div>

                <div class="space-y-1.5">
                  <Label for="d-vehyear">Manufacturing Year</Label>
                  <Input id="d-vehyear" type="number" v-model="driverForm.vehicleYear" :disabled="isLocked" min="2000" :max="new Date().getFullYear()" />
                </div>
              </div>

              <FileUpload v-model="driverForm.rcBookPhoto" label="RC Book / Registration Certificate Photo" :disabled="isLocked" />

              <div class="flex justify-between pt-2">
                <Button type="button" variant="ghost" @click="activeDriverSection = 2">&larr; Previous</Button>
                <Button type="button" variant="outline" @click="activeDriverSection = 4">Next: Insurance & PUC &rarr;</Button>
              </div>
            </CardContent>
          </Card>

          <!-- Section 4: Insurance & PUC -->
          <Card class="border shadow-xs overflow-hidden transition-all">
            <CardHeader
              class="cursor-pointer bg-muted/30 select-none flex flex-row items-center justify-between p-4"
              @click="activeDriverSection = activeDriverSection === 4 ? 0 : 4"
            >
              <div class="flex items-center gap-2.5">
                <div class="size-8 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-sm">4</div>
                <div>
                  <CardTitle class="text-base font-semibold">Insurance & PUC Certification</CardTitle>
                  <CardDescription class="text-xs">Active vehicle insurance and pollution certificate</CardDescription>
                </div>
              </div>
              <component :is="activeDriverSection === 4 ? ChevronUp : ChevronDown" class="size-5 text-muted-foreground" />
            </CardHeader>

            <CardContent v-show="activeDriverSection === 4" class="p-6 space-y-4 border-t">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="space-y-1.5">
                  <Label for="d-inspol">Insurance Policy Number *</Label>
                  <Input id="d-inspol" v-model="driverForm.insurancePolicyNumber" :disabled="isLocked" :class="{ 'border-destructive': driverErrors.insurancePolicyNumber }" placeholder="POL-987654321" />
                  <p v-if="driverErrors.insurancePolicyNumber" class="text-xs text-destructive">{{ driverErrors.insurancePolicyNumber }}</p>
                </div>

                <div class="space-y-1.5">
                  <Label for="d-inprov">Insurance Provider *</Label>
                  <Input id="d-inprov" v-model="driverForm.insuranceProvider" :disabled="isLocked" :class="{ 'border-destructive': driverErrors.insuranceProvider }" placeholder="ICICI Lombard" />
                  <p v-if="driverErrors.insuranceProvider" class="text-xs text-destructive">{{ driverErrors.insuranceProvider }}</p>
                </div>

                <div class="space-y-1.5">
                  <Label for="d-insexp">Insurance Expiry Date</Label>
                  <Input id="d-insexp" type="date" v-model="driverForm.insuranceExpiryDate" :disabled="isLocked" />
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-1.5">
                  <Label for="d-pucnum">PUC Certificate Number *</Label>
                  <Input id="d-pucnum" v-model="driverForm.pucCertificateNumber" :disabled="isLocked" :class="{ 'border-destructive': driverErrors.pucCertificateNumber }" placeholder="PUC-123456" />
                  <p v-if="driverErrors.pucCertificateNumber" class="text-xs text-destructive">{{ driverErrors.pucCertificateNumber }}</p>
                </div>

                <div class="space-y-1.5">
                  <Label for="d-pucexp">PUC Expiry Date</Label>
                  <Input id="d-pucexp" type="date" v-model="driverForm.pucExpiryDate" :disabled="isLocked" />
                </div>
              </div>

              <FileUpload v-model="driverForm.insurancePhoto" label="Insurance Certificate Photo" :disabled="isLocked" />

              <div class="flex justify-between pt-2">
                <Button type="button" variant="ghost" @click="activeDriverSection = 3">&larr; Previous</Button>
                <Button
                  type="submit"
                  :disabled="submitMutation.isPending.value || isLocked"
                  size="lg"
                  class="px-8"
                >
                  <LoaderCircle v-if="submitMutation.isPending.value" class="size-4 animate-spin mr-2" />
                  <ShieldCheck v-else class="size-4 mr-2" />
                  {{ isLocked ? 'Form Submitted' : (isEditingProfile ? 'Submit Profile Update Request' : 'Submit Complete Application') }}
                </Button>
              </div>
            </CardContent>
          </Card>
        </form>

        <!-- SHIPPER FORM -->
        <form v-else-if="user?.role === 'shipper'" @submit.prevent="handleSubmit" class="space-y-4" novalidate>
          <!-- Section 1: Personal Info -->
          <Card class="border shadow-xs overflow-hidden transition-all">
            <CardHeader
              class="cursor-pointer bg-muted/30 select-none flex flex-row items-center justify-between p-4"
              @click="activeShipperSection = activeShipperSection === 1 ? 0 : 1"
            >
              <div class="flex items-center gap-2.5">
                <div class="size-8 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-sm">1</div>
                <div>
                  <CardTitle class="text-base font-semibold">Authorized Person Information</CardTitle>
                  <CardDescription class="text-xs">Representative details and Aadhaar verification</CardDescription>
                </div>
              </div>
              <component :is="activeShipperSection === 1 ? ChevronUp : ChevronDown" class="size-5 text-muted-foreground" />
            </CardHeader>

            <CardContent v-show="activeShipperSection === 1" class="p-6 space-y-4 border-t">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="space-y-1.5">
                  <Label for="s-fullname">Authorized Person Name *</Label>
                  <Input id="s-fullname" v-model="shipperForm.fullName" :disabled="isLocked" :class="{ 'border-destructive': shipperErrors.fullName }" placeholder="Priya Sharma" />
                  <p v-if="shipperErrors.fullName" class="text-xs text-destructive">{{ shipperErrors.fullName }}</p>
                </div>

                <div class="space-y-1.5">
                  <Label for="s-aadhaar">Aadhaar Last 4 Digits *</Label>
                  <Input id="s-aadhaar" v-model="shipperForm.aadhaarLast4" maxlength="4" :disabled="isLocked" :class="{ 'border-destructive': shipperErrors.aadhaarLast4 }" placeholder="5678" />
                  <p v-if="shipperErrors.aadhaarLast4" class="text-xs text-destructive">{{ shipperErrors.aadhaarLast4 }}</p>
                </div>

                <div class="space-y-1.5">
                  <Label for="s-phone">Direct Phone Number *</Label>
                  <Input id="s-phone" v-model="shipperForm.phone" maxlength="10" :disabled="isLocked" :class="{ 'border-destructive': shipperErrors.phone }" placeholder="9876543210" />
                  <p v-if="shipperErrors.phone" class="text-xs text-destructive">{{ shipperErrors.phone }}</p>
                </div>
              </div>

              <Separator class="my-2" />
              <h4 class="text-sm font-semibold text-foreground">Emergency Contact</h4>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-1.5">
                  <Label for="s-ecname">Contact Person Name *</Label>
                  <Input id="s-ecname" v-model="shipperForm.emergencyContactName" :disabled="isLocked" :class="{ 'border-destructive': shipperErrors.emergencyContactName }" placeholder="Representative / Colleague Name" />
                  <p v-if="shipperErrors.emergencyContactName" class="text-xs text-destructive">{{ shipperErrors.emergencyContactName }}</p>
                </div>

                <div class="space-y-1.5">
                  <Label for="s-ecphone">Contact Phone *</Label>
                  <Input id="s-ecphone" v-model="shipperForm.emergencyContactPhone" maxlength="10" :disabled="isLocked" :class="{ 'border-destructive': shipperErrors.emergencyContactPhone }" placeholder="9123456789" />
                  <p v-if="shipperErrors.emergencyContactPhone" class="text-xs text-destructive">{{ shipperErrors.emergencyContactPhone }}</p>
                </div>
              </div>

              <Separator class="my-2" />
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FileUpload v-model="shipperForm.profilePhoto" label="Representative Profile Photo" :disabled="isLocked" />
                <FileUpload v-model="shipperForm.aadhaarPhoto" label="Aadhaar Card Photo (Front)" :disabled="isLocked" />
              </div>

              <div class="flex justify-end pt-2">
                <Button type="button" variant="outline" @click="activeShipperSection = 2">Next: Business Details &rarr;</Button>
              </div>
            </CardContent>
          </Card>

          <!-- Section 2: Business Details -->
          <Card class="border shadow-xs overflow-hidden transition-all">
            <CardHeader
              class="cursor-pointer bg-muted/30 select-none flex flex-row items-center justify-between p-4"
              @click="activeShipperSection = activeShipperSection === 2 ? 0 : 2"
            >
              <div class="flex items-center gap-2.5">
                <div class="size-8 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-sm">2</div>
                <div>
                  <CardTitle class="text-base font-semibold">Company & Tax Details</CardTitle>
                  <CardDescription class="text-xs">GSTIN, PAN, registration, and documents</CardDescription>
                </div>
              </div>
              <component :is="activeShipperSection === 2 ? ChevronUp : ChevronDown" class="size-5 text-muted-foreground" />
            </CardHeader>

            <CardContent v-show="activeShipperSection === 2" class="p-6 space-y-4 border-t">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-1.5">
                  <Label for="s-bizname">Business Name *</Label>
                  <Input id="s-bizname" v-model="shipperForm.businessName" :disabled="isLocked" :class="{ 'border-destructive': shipperErrors.businessName }" placeholder="ABC Logistics Pvt Ltd" />
                  <p v-if="shipperErrors.businessName" class="text-xs text-destructive">{{ shipperErrors.businessName }}</p>
                </div>

                <div class="space-y-1.5">
                  <Label for="s-biztype">Constitution / Business Type</Label>
                  <select id="s-biztype" v-model="shipperForm.businessType" :disabled="isLocked" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                    <option v-for="bt in ['Proprietorship', 'Partnership', 'Pvt Ltd', 'LLP', 'Public Ltd']" :key="bt" :value="bt">{{ bt }}</option>
                  </select>
                </div>

                <div class="space-y-1.5">
                  <Label for="s-gst">GST Number (15 Chars) *</Label>
                  <Input id="s-gst" v-model="shipperForm.gstNumber" maxlength="15" :disabled="isLocked" :class="{ 'border-destructive': shipperErrors.gstNumber }" placeholder="27AAPFU0939F1ZV" />
                  <p v-if="shipperErrors.gstNumber" class="text-xs text-destructive">{{ shipperErrors.gstNumber }}</p>
                </div>

                <div class="space-y-1.5">
                  <Label for="s-pan">Company PAN Number (10 Chars) *</Label>
                  <Input id="s-pan" v-model="shipperForm.panNumber" maxlength="10" :disabled="isLocked" :class="{ 'border-destructive': shipperErrors.panNumber }" placeholder="AAPFU0939F" />
                  <p v-if="shipperErrors.panNumber" class="text-xs text-destructive">{{ shipperErrors.panNumber }}</p>
                </div>
              </div>

              <div class="space-y-1.5">
                <Label for="s-address">Registered Office Address *</Label>
                <Input id="s-address" v-model="shipperForm.registeredAddress" :disabled="isLocked" :class="{ 'border-destructive': shipperErrors.registeredAddress }" placeholder="Block, Building, Industrial Estate, City, State, Pincode" />
                <p v-if="shipperErrors.registeredAddress" class="text-xs text-destructive">{{ shipperErrors.registeredAddress }}</p>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="space-y-1.5">
                  <Label for="s-turnover">Annual Turnover</Label>
                  <select id="s-turnover" v-model="shipperForm.annualTurnover" :disabled="isLocked" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                    <option v-for="t in ['Below 10L', '10L-50L', '50L-2Cr', 'Above 2Cr']" :key="t" :value="t">{{ t }}</option>
                  </select>
                </div>

                <div class="space-y-1.5">
                  <Label for="s-years">Years in Business</Label>
                  <Input id="s-years" type="number" v-model="shipperForm.yearsInBusiness" :disabled="isLocked" min="0" max="100" />
                </div>

                <div class="space-y-1.5">
                  <Label for="s-goods">Primary Goods Category *</Label>
                  <Input id="s-goods" v-model="shipperForm.primaryGoodsCategory" :disabled="isLocked" :class="{ 'border-destructive': shipperErrors.primaryGoodsCategory }" placeholder="FMCG, Electronics, Steel" />
                  <p v-if="shipperErrors.primaryGoodsCategory" class="text-xs text-destructive">{{ shipperErrors.primaryGoodsCategory }}</p>
                </div>
              </div>

              <Separator class="my-2" />
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <FileUpload v-model="shipperForm.gstCertPhoto" label="GST Certificate Photo" :disabled="isLocked" />
                <FileUpload v-model="shipperForm.panCardPhoto" label="PAN Card Photo" :disabled="isLocked" />
                <FileUpload v-model="shipperForm.businessRegPhoto" label="Business Registration Certificate" :disabled="isLocked" />
              </div>

              <div class="flex justify-between pt-4">
                <Button type="button" variant="ghost" @click="activeShipperSection = 1">&larr; Previous</Button>
                <Button
                  type="submit"
                  :disabled="submitMutation.isPending.value || isLocked"
                  size="lg"
                  class="px-8"
                >
                  <LoaderCircle v-if="submitMutation.isPending.value" class="size-4 animate-spin mr-2" />
                  <ShieldCheck v-else class="size-4 mr-2" />
                  {{ isLocked ? 'Form Submitted' : (isEditingProfile ? 'Submit Profile Update Request' : 'Submit Complete Application') }}
                </Button>
              </div>
            </CardContent>
          </Card>
        </form>
      </template>
    </div>

    <SupportEmailSimulatorModal
      :open="supportModalOpen"
      default-tab="email"
      default-subject="[PROFILE EDIT REQUEST] Profile credential updates"
      @update:open="supportModalOpen = $event"
      @ticket-created="onTicketGenerated"
    />
  </div>
</template>
