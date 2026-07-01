<script lang="ts" setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { authClient } from '@/lib/auth-client'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { LoaderCircle, CheckCircle2, XCircle, Clock, ShieldCheck, ArrowLeft, Truck, FileText } from '@lucide/vue'

const router = useRouter()
const { user, loading } = useAuth()

const submitting = ref(false)
const submitSuccess = ref(false)
const submitError = ref('')
const verificationStatus = ref<string>('none')
const verificationData = ref<any>(null)
const loadingStatus = ref(true)

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

watch([user, loading], ([u, l]) => {
  if (!l) {
    if (!u) router.replace('/login')
    else if (u.role !== 'driver' && u.role !== 'shipper') router.replace('/')
  }
})

onMounted(async () => {
  if (!user.value) return
  try {
    const session = await authClient.getSession()
    const token = (session.data as any)?.session?.token
    if (!token) return

    const res = await fetch('/api/verification/status', {
      headers: { Authorization: `Bearer ${token}` },
    })
    const data = await res.json()
    verificationStatus.value = data.status
    verificationData.value = data.verification

    if (data.verification) {
      if (user.value?.role === 'driver') {
        driverForm.licenseNumber = data.verification.licenseNumber || ''
        driverForm.vehicleType = data.verification.vehicleType || ''
        driverForm.vehicleNumber = data.verification.vehicleNumber || ''
      } else {
        shipperForm.businessName = data.verification.businessName || ''
        shipperForm.gstNumber = data.verification.gstNumber || ''
        shipperForm.companyAddress = data.verification.companyAddress || ''
      }
    }
  } catch {
    // ignore
  } finally {
    loadingStatus.value = false
  }
})

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

async function handleSubmit() {
  submitError.value = ''
  submitSuccess.value = false

  const isDriver = user.value?.role === 'driver'
  if (isDriver ? !validateDriver() : !validateShipper()) return

  submitting.value = true
  try {
    const session = await authClient.getSession()
    const token = (session.data as any)?.session?.token
    if (!token) {
      submitError.value = 'Not authenticated'
      return
    }

    const endpoint = isDriver ? '/api/verification/submit/driver' : '/api/verification/submit/shipper'
    const body = isDriver ? driverForm : shipperForm

    const res = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(body),
    })

    if (!res.ok) {
      const data = await res.json()
      submitError.value = data.detail || 'Failed to submit verification'
      return
    }

    const data = await res.json()
    verificationStatus.value = data.status
    verificationData.value = data
    submitSuccess.value = true
  } catch {
    submitError.value = 'Something went wrong. Please try again.'
  } finally {
    submitting.value = false
  }
}

function goBack() {
  const role = user.value?.role
  if (role === 'driver') router.push('/driver')
  else if (role === 'shipper') router.push('/shipper')
  else router.push('/')
}
</script>

<template>
  <div class="flex-1 p-8 bg-background">
    <div class="max-w-2xl mx-auto">
      <div v-if="loading || loadingStatus" class="text-center py-12">
        <LoaderCircle class="size-8 animate-spin mx-auto text-muted-foreground" />
        <p class="text-muted-foreground mt-2">Loading...</p>
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

        <!-- Status Cards -->
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

        <!-- Driver Form -->
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
            <Alert v-if="submitError" variant="destructive" class="mb-4">
              <AlertDescription>{{ submitError }}</AlertDescription>
            </Alert>
            <Alert v-if="submitSuccess" class="mb-4 border-green-200 bg-green-50 text-green-800">
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
                :disabled="submitting || verificationStatus === 'approved' || verificationStatus === 'pending'"
                class="w-full"
                size="lg"
              >
                <LoaderCircle v-if="submitting" class="size-4 animate-spin" />
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

        <!-- Shipper Form -->
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
            <Alert v-if="submitError" variant="destructive" class="mb-4">
              <AlertDescription>{{ submitError }}</AlertDescription>
            </Alert>
            <Alert v-if="submitSuccess" class="mb-4 border-green-200 bg-green-50 text-green-800">
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
                :disabled="submitting || verificationStatus === 'approved' || verificationStatus === 'pending'"
                class="w-full"
                size="lg"
              >
                <LoaderCircle v-if="submitting" class="size-4 animate-spin" />
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
