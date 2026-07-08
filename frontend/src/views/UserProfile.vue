<script lang="ts" setup>
import { computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useVerificationStatus } from '@/composables/useVerificationStatus'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { User, ShieldCheck, Clock, CheckCircle2, XCircle, ArrowRight, Truck, Package } from '@lucide/vue'

const router = useRouter()
const { user, loading } = useAuth()
const { data: verification, isLoading: loadingStatus } = useVerificationStatus()

const verificationStatus = computed(() => verification.value?.status ?? 'none')

watch([user, loading], ([u, l]) => {
  if (!l) {
    if (!u) router.replace('/login')
    else if (u.role !== 'driver' && u.role !== 'shipper') router.replace('/')
  }
})

</script>

<template>
  <div class="flex-1 p-6 md:p-8 bg-background">
    <div class="max-w-2xl mx-auto space-y-6">
      <div v-if="loading || loadingStatus" class="space-y-4">
        <Skeleton class="h-8 w-48" />
        <Skeleton class="h-48 w-full rounded-xl" />
        <Skeleton class="h-36 w-full rounded-xl" />
      </div>

      <template v-else-if="user">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-foreground">Account Profile</h1>
            <p class="text-muted-foreground mt-1">Manage your account credentials and verification status</p>
          </div>
        </div>

        <!-- Normal Profile Data Card -->
        <Card class="bg-card text-card-foreground border border-border shadow-xs">
          <CardHeader class="border-b border-border pb-6">
            <div class="flex items-center gap-4">
              <Avatar class="size-16 border border-border">
                <AvatarFallback class="text-xl bg-primary/10 text-primary font-semibold">
                  {{ (user.name || user.role || '?').charAt(0).toUpperCase() }}
                </AvatarFallback>
              </Avatar>
              <div>
                <CardTitle class="flex items-center gap-2 text-2xl font-bold text-foreground">
                  {{ verification?.verification?.fullName || user.name || 'User Profile' }}
                  <Badge variant="outline" class="capitalize font-semibold text-xs border-primary/40 bg-primary/5 text-primary">
                    <Truck v-if="user.role === 'driver'" class="size-3 mr-1" />
                    <Package v-else class="size-3 mr-1" />
                    {{ user.role }}
                  </Badge>
                </CardTitle>
                <CardDescription class="text-muted-foreground mt-0.5">
                  Registered Account Details
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent class="space-y-3.5 pt-6 text-sm">
            <div class="flex items-center justify-between py-1.5 border-b border-border/40">
              <span class="text-muted-foreground font-medium">Full Name</span>
              <span class="font-semibold text-foreground">{{ verification?.verification?.fullName || user.name || 'Not provided' }}</span>
            </div>
            <div class="flex items-center justify-between py-1.5 border-b border-border/40">
              <span class="text-muted-foreground font-medium">Email Address</span>
              <span class="font-semibold text-foreground">{{ user.email }}</span>
            </div>
            <div class="flex items-center justify-between py-1.5 border-b border-border/40">
              <span class="text-muted-foreground font-medium">Phone Number</span>
              <span class="font-semibold text-foreground">{{ verification?.verification?.phone || user.phone || 'Not provided' }}</span>
            </div>
            <div class="flex items-center justify-between py-1.5">
              <span class="text-muted-foreground font-medium">Account Status</span>
              <Badge class="bg-green-100 text-green-800 hover:bg-green-100 border border-green-200">Active</Badge>
            </div>
          </CardContent>
        </Card>

        <!-- Verification Integration Card -->
        <Card class="border border-border shadow-xs overflow-hidden">
          <CardHeader class="bg-muted/30 border-b pb-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2.5">
                <div class="size-9 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                  <ShieldCheck class="size-5" />
                </div>
                <div>
                  <CardTitle class="text-lg font-bold text-foreground">Identity & Document Verification</CardTitle>
                  <CardDescription class="text-xs">Complete verification to access full platform capabilities</CardDescription>
                </div>
              </div>

              <Badge
                v-if="verificationStatus === 'approved'"
                class="bg-green-100 text-green-800 border-green-200 font-semibold px-3 py-1"
              >
                <CheckCircle2 class="size-3.5 mr-1" /> Approved
              </Badge>
              <Badge
                v-else-if="verificationStatus === 'pending'"
                class="bg-yellow-100 text-yellow-800 border-yellow-200 font-semibold px-3 py-1"
              >
                <Clock class="size-3.5 mr-1" /> Under Review
              </Badge>
              <Badge
                v-else-if="verificationStatus === 'rejected'"
                class="bg-red-100 text-red-800 border-red-200 font-semibold px-3 py-1"
              >
                <XCircle class="size-3.5 mr-1" /> Rejected
              </Badge>
              <Badge
                v-else
                class="bg-muted text-muted-foreground border font-semibold px-3 py-1"
              >
                Not Verified
              </Badge>
            </div>
          </CardHeader>
          <CardContent class="p-6 space-y-4">
            <p v-if="verificationStatus === 'approved'" class="text-sm text-muted-foreground">
              Your credentials, identity documents, and regulatory filings have been verified. You have full access to RoadLancer workflows.
            </p>
            <p v-else-if="verificationStatus === 'pending'" class="text-sm text-muted-foreground">
              Your application has been submitted and is currently being audited by our verification team. You can view your submitted details below.
            </p>
            <p v-else class="text-sm text-muted-foreground">
              Please submit your driver license, vehicle registration, or business documentation to complete your verification process.
            </p>

            <div class="pt-2">
              <a
                href="/get-validated"
                class="inline-flex items-center justify-center gap-2 rounded-lg px-6 text-sm font-semibold h-10 bg-primary text-primary-foreground hover:bg-primary/90 w-full sm:w-auto shadow-sm transition-all select-none no-underline"
              >
                <ShieldCheck class="size-4 mr-1" />
                {{ verificationStatus === 'none' ? 'Get Validated — Open Application Forms' : 'View Verification Forms & Attachments' }}
                <ArrowRight class="size-4 ml-1" />
              </a>
            </div>
          </CardContent>
        </Card>
      </template>
    </div>
  </div>
</template>
