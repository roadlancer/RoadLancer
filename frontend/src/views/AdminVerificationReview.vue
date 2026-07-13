<script lang="ts" setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useVerificationList } from '@/composables/useVerificationList'
import VerificationDetailDialog from '@/components/VerificationDetailDialog.vue'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Search, ArrowLeft, ShieldCheck, Clock, CheckCircle2, XCircle, Eye } from '@lucide/vue'

const router = useRouter()
const { user, loading } = useAuth()

const {
  data: verifications,
  isLoading: loadingData,
  searchQuery,
  activeTab,
  approveMutation,
  rejectMutation,
  resetPendingMutation,
} = useVerificationList()

const selectedVerification = ref<any>(null)
const showDetailDialog = ref(false)
const showRejectDialog = ref(false)
const rejectReason = ref('')
const customRejectMessage = ref('')

const verificationRejectReasons = [
  'Invalid or expired identity documents',
  'Documents are unclear or unreadable',
  'Information does not match registration details',
  'Suspected fraudulent submission',
  'Missing required documents',
  'Vehicle registration documents are invalid',
  'Business registration not verifiable',
  'Does not meet platform eligibility requirements',
  'Other',
]

watch([user, loading], ([u, l]) => {
  if (l) return
  if (!u) router.replace('/login')
  else if (u.role !== 'admin') router.replace('/')
})

async function viewDetails(v: any) {
  selectedVerification.value = { ...v }
  showDetailDialog.value = true
}

function handleApprove(id: string) {
  approveMutation.mutate(id, {
    onSuccess: () => { showDetailDialog.value = false },
  })
}

function openRejectDialog() {
  rejectReason.value = ''
  customRejectMessage.value = ''
  showRejectDialog.value = true
}

function confirmReject() {
  if (!selectedVerification.value) return
  const finalReason = rejectReason.value === 'Other' ? customRejectMessage.value : rejectReason.value
  if (!finalReason) return
  rejectMutation.mutate(
    { id: selectedVerification.value.id, reason: finalReason },
    {
      onSuccess: () => {
        showRejectDialog.value = false
        showDetailDialog.value = false
      },
    },
  )
}

function handleResetPending(id: string) {
  resetPendingMutation.mutate(id)
  showDetailDialog.value = false
}

function roleBadgeColor(role: string) {
  if (role === 'driver') return 'bg-blue-100 text-blue-800 border-blue-200'
  if (role === 'shipper') return 'bg-purple-100 text-purple-800 border-purple-200'
  return 'bg-gray-100 text-gray-800 border-gray-200'
}

function statusColor(status: string) {
  if (status === 'approved') return 'bg-green-100 text-green-800 border-green-200'
  if (status === 'rejected') return 'bg-red-100 text-red-800 border-red-200'
  if (status === 'pending') return 'bg-yellow-100 text-yellow-800 border-yellow-200'
  return 'bg-gray-100 text-gray-800 border-gray-200'
}
</script>

<template>
  <div class="flex-1 p-6 md:p-8 bg-background">
    <div class="max-w-6xl mx-auto">
      <a href="/admin" class="inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium h-8 px-3 hover:bg-muted hover:text-foreground mb-4 no-underline">
        <ArrowLeft class="size-4 mr-2" />
        Back to Dashboard
      </a>

      <div class="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-3xl font-bold text-foreground flex items-center gap-2">
            <ShieldCheck class="size-8 text-primary" />
            Verification Reviews
          </h1>
          <p class="text-muted-foreground mt-1">Review applicant profiles, inspect attached credentials, and approve access.</p>
        </div>
      </div>

      <div class="flex flex-col sm:flex-row gap-4 mb-6">
        <div class="relative flex-1">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input
            v-model="searchQuery"
            placeholder="Search applicants by name or email..."
            class="pl-9 h-10"
          />
        </div>
      </div>

      <Tabs v-model="activeTab" class="mb-6">
        <TabsList class="h-11 p-1">
          <TabsTrigger value="pending" class="px-4">
            <Clock class="size-4 mr-1.5" />
            Pending Review
          </TabsTrigger>
          <TabsTrigger value="approved" class="px-4">
            <CheckCircle2 class="size-4 mr-1.5" />
            Approved
          </TabsTrigger>
          <TabsTrigger value="rejected" class="px-4">
            <XCircle class="size-4 mr-1.5" />
            Rejected
          </TabsTrigger>
          <TabsTrigger value="all" class="px-4">All Submissions</TabsTrigger>
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
            </div>
          </CardContent>
        </Card>
      </div>

      <div v-else-if="!verifications || verifications.length === 0" class="text-center py-16 bg-muted/20 rounded-xl border border-dashed">
        <ShieldCheck class="size-14 mx-auto text-muted-foreground/40 mb-3" />
        <p class="text-lg font-medium text-foreground">No verification records found</p>
        <p class="text-sm text-muted-foreground mt-1">Submissions matching your filter will appear here.</p>
      </div>

      <div v-else class="space-y-3">
        <Card
          v-for="v in verifications"
          :key="v.id"
          class="hover:shadow-md transition-shadow cursor-pointer border"
          @click="viewDetails(v)"
        >
          <CardContent class="p-4 flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="w-11 h-11 rounded-full bg-primary/10 flex items-center justify-center border border-primary/20">
                <span class="text-base font-bold text-primary">
                  {{ (v.userName || '?').charAt(0).toUpperCase() }}
                </span>
              </div>
              <div>
                <p class="font-semibold text-foreground flex items-center gap-2">
                  {{ v.userName }}
                  <span v-if="v.fullName" class="text-xs font-normal text-muted-foreground">({{ v.fullName }})</span>
                </p>
                <p class="text-sm text-muted-foreground">{{ v.userEmail }} &bull; Submitted {{ v.createdAt ? v.createdAt.split('T')[0] : 'Recently' }}</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <Badge :class="roleBadgeColor(v.userRole)" class="capitalize px-3 py-1 font-medium border">
                {{ v.userRole }}
              </Badge>
              <Badge :class="statusColor(v.status)" class="capitalize px-3 py-1 font-medium border">
                {{ v.status }}
              </Badge>
              <Button variant="outline" size="sm" class="gap-1.5">
                <Eye class="size-3.5" /> View Application
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Verification Details Dialog -->
      <VerificationDetailDialog
        :open="showDetailDialog"
        :verification="selectedVerification"
        :show-actions="true"
        @update:open="showDetailDialog = $event"
        @approve="handleApprove"
        @reject="openRejectDialog"
        @reset-pending="handleResetPending"
      />

      <!-- Rejection Reason Dialog -->
      <Dialog v-model:open="showRejectDialog">
        <DialogContent class="sm:max-w-lg w-[90vw] p-6">
          <DialogHeader>
            <DialogTitle>Decline Application</DialogTitle>
            <DialogDescription>
              Select the primary non-compliance reason for rejecting this verification request.
            </DialogDescription>
          </DialogHeader>
          <div class="space-y-4 py-2">
            <div class="space-y-2 max-h-60 overflow-y-auto pr-1">
              <label
                v-for="reason in verificationRejectReasons"
                :key="reason"
                class="flex items-center gap-3 rounded-lg border p-3 cursor-pointer transition-colors"
                :class="rejectReason === reason ? 'border-destructive bg-destructive/5' : 'border-border hover:border-destructive/40'"
              >
                <input type="radio" :value="reason" v-model="rejectReason" class="size-4 accent-destructive" />
                <span class="text-sm font-medium">{{ reason }}</span>
              </label>
            </div>
            <div v-if="rejectReason === 'Other'" class="space-y-2">
              <Label for="customRejectMessage">Specific non-compliance explanation</Label>
              <textarea
                id="customRejectMessage"
                v-model="customRejectMessage"
                placeholder="Detail exact document or verification discrepancy..."
                rows="3"
                class="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-none"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" @click="showRejectDialog = false">Cancel</Button>
            <Button
              variant="destructive"
              @click="confirmReject"
              :disabled="!rejectReason || (rejectReason === 'Other' && !customRejectMessage) || rejectMutation.isPending.value"
            >
              Confirm Rejection
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

    </div>
  </div>
</template>
