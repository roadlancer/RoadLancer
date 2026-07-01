<script lang="ts" setup>
import { reactive, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useVerificationStatus, useSubmitVerification } from '@/composables/useVerificationStatus'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { LoaderCircle, CheckCircle2, XCircle, Clock, ShieldCheck, ArrowLeft, Truck, FileText } from '@lucide/vue'

const router = useRouter()
const { user, loading } = useAuth()

const { data: verification, isLoading: loadingStatus, isVerified } = useVerificationStatus()
const submitMutation = useSubmitVerification()

const verificationStatus = computed(() => verification.value?.status ?? 'none')
const verificationData = computed(() => verification.value?.verification ?? null)

const driverForm = reactive({
  licenseNumber: '',
  vehicleType: '',
  vehicleNumber: '',
})

const shipperForm = reactive({
  businessName: '',
  gstNumber: '',
  companyAddress: '',
})

const driverErrors = reactive({ licenseNumber: '', vehicleType: '', vehicleNumber: '' })
const shipperErrors = reactive({ businessName: '', gstNumber: '', companyAddress: '' })

watch(verificationData, (data) => {
  if (!data || !user.value) return
  if (user.value.role === 'driver') {
    driverForm.licenseNumber = data.licenseNumber || ''
    driverForm.vehicleType = data.vehicleType || ''
    driverForm.vehicleNumber = data.vehicleNumber || ''
  } else {
    shipperForm.businessName = data.businessName || ''
    shipperForm.gstNumber = data.gstNumber || ''
    shipperForm.companyAddress = data.companyAddress || ''
  }
}, { immediate: true })

function validateDriver() {
  let valid = true
  driverErrors.licenseNumber = ''
  driverErrors.vehicleType = ''
  driverErrors.vehicleNumber = ''

  if (!driverForm.licenseNumber.trim()) {
    driverErrors.licenseNumber = 'License number is required'
    valid = false
  }
  if (!driverForm.vehicleType.trim()) {
    driverErrors.vehicleType = 'Vehicle type is required'
    valid = false
  }
  if (!driverForm.vehicleNumber.trim()) {
    driverErrors.vehicleNumber = 'Vehicle number is required'
    valid = false
  }
  return valid
}

function validateShipper() {
  let valid = true
  shipperErrors.businessName = ''
  shipperErrors.gstNumber = ''
  shipperErrors.companyAddress = ''

  if (!shipperForm.businessName.trim()) {
    shipperErrors.businessName = 'Business name is required'
    valid = false
  }
  if (!shipperForm.gstNumber.trim()) {
    shipperErrors.gstNumber = 'GST number is required'
    valid = false
  }
  if (!shipperForm.companyAddress.trim()) {
    shipperErrors.companyAddress = 'Company address is required'
    valid = false
  }
  return valid
}

function handleSubmit() {
  const isDriver = user.value?.role === 'driver'
  if (isDriver ? !validateDriver() : !validateShipper()) return

  const endpoint = isDriver ? '/verification/submit/driver' : '/verification/submit/shipper'
  const body = isDriver ? driverForm : shipperForm

  submitMutation.mutate({ endpoint, body })
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
  <div class="flex-1 p-8 bg-background">
    <div class="max-w-2xl mx-auto">
      <div v-if="loading || loadingStatus" class="max-w-2xl mx-auto">
        <Skeleton class="h-9 w-32 mb-4" />
        <Skeleton class="h-9 w-48 mb-2" />
        <Skeleton class="h-5 w-80 mb-6" />
        <Skeleton class="h-16 w-full mb-6" />
        <Card>
          <CardHeader>
            <Skeleton class="h-6 w-48 mb-2" />
            <Skeleton class="h-4 w-64" />
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="space-y-2">
              <Skeleton class="h-4 w-24" />
              <Skeleton class="h-10 w-full" />
            </div>
            <div class="space-y-2">
              <Skeleton class="h-4 w-24" />
              <Skeleton class="h-10 w-full" />
            </div>
            <div class="space-y-2">
              <Skeleton class="h-4 w-24" />
              <Skeleton class="h-10 w-full" />
            </div>
            <Skeleton class="h-px w-full my-4" />
            <Skeleton class="h-12 w-full" />
          </CardContent>
        </Card>
      </div>

      <template v-else-if="user?.role === 'driver' || user?.role === 'shipper'">
        <Button variant="ghost" size="sm" class="mb-4" @click="goBack">
          <ArrowLeft class="size-4 mr-2" />
          Back to Dashboard
        </Button>

        <div class="mb-6">
          <h1 class="text-3xl font-bold text-foreground">Get Validated</h1>
          <p class="text-muted-foreground mt-1">
            Complete your profile verification to start using the platform.
          </p>
        </div>

        <div v-if="verificationStatus === 'approved'" class="mb-6">
          <Alert class="border-green-200 bg-green-50 text-green-800">
            <CheckCircle2 class="h-4 w-4 text-green-600" />
            <AlertDescription class="text-green-700">
              <strong>You're verified!</strong> Your account has been approved. You can now access all features.
            </AlertDescription>
          </Alert>
        </div>

        <div v-else-if="verificationStatus === 'rejected'" class="mb-6">
          <Alert variant="destructive">
            <XCircle class="h-4 w-4" />
            <AlertDescription>
              <strong>Verification rejected.</strong>
              {{ verificationData?.rejectionReason ? `Reason: ${verificationData.rejectionReason}` : 'Please update your details and resubmit.' }}
            </AlertDescription>
          </Alert>
        </div>

        <div v-else-if="verificationStatus === 'pending'" class="mb-6">
          <Alert class="border-yellow-200 bg-yellow-50 text-yellow-800">
            <Clock class="h-4 w-4 text-yellow-600" />
            <AlertDescription class="text-yellow-700">
              <strong>Under review.</strong> Your verification is being reviewed by an admin. We'll notify you once it's processed.
            </AlertDescription>
          </Alert>
        </div>

        <Card v-if="user?.role === 'driver'">
          <CardHeader>
            <CardTitle class="flex items-center gap-2">
              <Truck class="size-5" />
              Driver Verification
            </CardTitle>
            <CardDescription>
              Please provide your driving license and vehicle details.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Alert v-if="submitMutation.isError.value" variant="destructive" class="mb-4">
              <AlertDescription>{{ (submitMutation.error.value as any)?.response?.data?.detail || 'Something went wrong.' }}</AlertDescription>
            </Alert>
            <Alert v-if="submitMutation.isSuccess.value" class="mb-4 border-green-200 bg-green-50 text-green-800">
              <CheckCircle2 class="h-4 w-4 text-green-600" />
              <AlertDescription class="text-green-700">
                Verification submitted successfully! An admin will review your details.
              </AlertDescription>
            </Alert>

            <form @submit.prevent="handleSubmit" class="space-y-4" novalidate>
              <div class="space-y-2">
                <Label for="licenseNumber">License Number</Label>
                <Input
                  id="licenseNumber"
                  v-model="driverForm.licenseNumber"
                  placeholder="e.g., DL-1234567890"
                  autocomplete="off"
                  :disabled="verificationStatus === 'approved' || verificationStatus === 'pending'"
                  :class="driverErrors.licenseNumber ? 'border-destructive' : ''"
                />
                <p v-if="driverErrors.licenseNumber" class="text-sm text-destructive">{{ driverErrors.licenseNumber }}</p>
              </div>

              <div class="space-y-2">
                <Label for="vehicleType">Vehicle Type</Label>
                <Input
                  id="vehicleType"
                  v-model="driverForm.vehicleType"
                  placeholder="e.g., Truck, Container, Tanker"
                  autocomplete="off"
                  :disabled="verificationStatus === 'approved' || verificationStatus === 'pending'"
                  :class="driverErrors.vehicleType ? 'border-destructive' : ''"
                />
                <p v-if="driverErrors.vehicleType" class="text-sm text-destructive">{{ driverErrors.vehicleType }}</p>
              </div>

              <div class="space-y-2">
                <Label for="vehicleNumber">Vehicle Number</Label>
                <Input
                  id="vehicleNumber"
                  v-model="driverForm.vehicleNumber"
                  placeholder="e.g., MH-12-AB-1234"
                  autocomplete="off"
                  :disabled="verificationStatus === 'approved' || verificationStatus === 'pending'"
                  :class="driverErrors.vehicleNumber ? 'border-destructive' : ''"
                />
                <p v-if="driverErrors.vehicleNumber" class="text-sm text-destructive">{{ driverErrors.vehicleNumber }}</p>
              </div>

              <Separator class="my-4" />

              <Button
                type="submit"
                :disabled="submitMutation.isPending.value || verificationStatus === 'approved' || verificationStatus === 'pending'"
                class="w-full"
                size="lg"
              >
                <LoaderCircle v-if="submitMutation.isPending.value" class="size-4 animate-spin" />
                <ShieldCheck v-else class="size-4 mr-2" />
                {{
                  verificationStatus === 'approved' ? 'Already Verified'
                  : verificationStatus === 'pending' ? 'Under Review'
                  : verificationStatus === 'rejected' ? 'Resubmit Verification'
                  : 'Submit for Verification'
                }}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card v-if="user?.role === 'shipper'">
          <CardHeader>
            <CardTitle class="flex items-center gap-2">
              <FileText class="size-5" />
              Shipper Verification
            </CardTitle>
            <CardDescription>
              Please provide your business details for verification.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Alert v-if="submitMutation.isError.value" variant="destructive" class="mb-4">
              <AlertDescription>{{ (submitMutation.error.value as any)?.response?.data?.detail || 'Something went wrong.' }}</AlertDescription>
            </Alert>
            <Alert v-if="submitMutation.isSuccess.value" class="mb-4 border-green-200 bg-green-50 text-green-800">
              <CheckCircle2 class="h-4 w-4 text-green-600" />
              <AlertDescription class="text-green-700">
                Verification submitted successfully! An admin will review your details.
              </AlertDescription>
            </Alert>

            <form @submit.prevent="handleSubmit" class="space-y-4" novalidate>
              <div class="space-y-2">
                <Label for="businessName">Business Name</Label>
                <Input
                  id="businessName"
                  v-model="shipperForm.businessName"
                  placeholder="e.g., ABC Logistics Pvt Ltd"
                  autocomplete="off"
                  :disabled="verificationStatus === 'approved' || verificationStatus === 'pending'"
                  :class="shipperErrors.businessName ? 'border-destructive' : ''"
                />
                <p v-if="shipperErrors.businessName" class="text-sm text-destructive">{{ shipperErrors.businessName }}</p>
              </div>

              <div class="space-y-2">
                <Label for="gstNumber">GST Number</Label>
                <Input
                  id="gstNumber"
                  v-model="shipperForm.gstNumber"
                  placeholder="e.g., 27AAPFU0939F1ZV"
                  autocomplete="off"
                  :disabled="verificationStatus === 'approved' || verificationStatus === 'pending'"
                  :class="shipperErrors.gstNumber ? 'border-destructive' : ''"
                />
                <p v-if="shipperErrors.gstNumber" class="text-sm text-destructive">{{ shipperErrors.gstNumber }}</p>
              </div>

              <div class="space-y-2">
                <Label for="companyAddress">Company Address</Label>
                <Input
                  id="companyAddress"
                  v-model="shipperForm.companyAddress"
                  placeholder="e.g., 123 Business Park, Mumbai 400001"
                  autocomplete="off"
                  :disabled="verificationStatus === 'approved' || verificationStatus === 'pending'"
                  :class="shipperErrors.companyAddress ? 'border-destructive' : ''"
                />
                <p v-if="shipperErrors.companyAddress" class="text-sm text-destructive">{{ shipperErrors.companyAddress }}</p>
              </div>

              <Separator class="my-4" />

              <Button
                type="submit"
                :disabled="submitMutation.isPending.value || verificationStatus === 'approved' || verificationStatus === 'pending'"
                class="w-full"
                size="lg"
              >
                <LoaderCircle v-if="submitMutation.isPending.value" class="size-4 animate-spin" />
                <ShieldCheck v-else class="size-4 mr-2" />
                {{
                  verificationStatus === 'approved' ? 'Already Verified'
                  : verificationStatus === 'pending' ? 'Under Review'
                  : verificationStatus === 'rejected' ? 'Resubmit Verification'
                  : 'Submit for Verification'
                }}
              </Button>
            </form>
          </CardContent>
        </Card>
      </template>
    </div>
  </div>
</template>
