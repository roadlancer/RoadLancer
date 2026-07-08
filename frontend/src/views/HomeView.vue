<script lang="ts" setup>
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Truck, Package, Search, IndianRupee, ShieldCheck, MapPin, Clock, Users, ArrowRight, Star, CheckCircle2 } from '@lucide/vue'

const router = useRouter()
const { user } = useAuth()
</script>

<template>
  <div class="flex-1">
    <!-- Hero Section -->
    <section class="relative overflow-hidden bg-gradient-to-br from-primary/5 via-background to-primary/10 border-b">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28">
        <div class="text-center max-w-3xl mx-auto">
          <div class="inline-flex items-center gap-2 bg-primary/10 text-primary px-4 py-1.5 rounded-full text-sm font-medium mb-6">
            <Truck class="size-4" />
            India's Trusted Logistics Platform
          </div>
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground leading-tight mb-6">
            Move Goods Across India
            <span class="text-primary"> Smarter & Faster</span>
          </h1>
          <p class="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Connect with verified transporters. Post shipments, get competitive bids, and track your loads in real-time — all on one platform.
          </p>
          <div class="flex flex-col sm:flex-row gap-3 justify-center">
            <Button size="lg" class="px-8 font-semibold" @click="router.push(user ? '/shipper' : '/register')">
              <Package class="size-5 mr-2" />
              Post a Shipment
            </Button>
            <Button size="lg" variant="outline" class="px-8 font-semibold" @click="router.push(user ? '/driver' : '/register')">
              <Search class="size-5 mr-2" />
              Find Loads
            </Button>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section class="py-20 bg-background">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-14">
          <h2 class="text-3xl font-bold text-foreground mb-3">How RoadLancer Works</h2>
          <p class="text-muted-foreground max-w-xl mx-auto">Three simple steps to move your cargo</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="text-center space-y-4">
            <div class="w-14 h-14 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto">
              <span class="text-2xl font-bold text-primary">1</span>
            </div>
            <h3 class="text-lg font-bold text-foreground">Post Your Load</h3>
            <p class="text-sm text-muted-foreground">Enter pickup, delivery, weight, and vehicle type. Our AI suggests a fair market price instantly.</p>
          </div>
          <div class="text-center space-y-4">
            <div class="w-14 h-14 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto">
              <span class="text-2xl font-bold text-primary">2</span>
            </div>
            <h3 class="text-lg font-bold text-foreground">Get Competitive Bids</h3>
            <p class="text-sm text-muted-foreground">Verified drivers bid on your shipment. Compare quotes, ratings, and choose the best fit.</p>
          </div>
          <div class="text-center space-y-4">
            <div class="w-14 h-14 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto">
              <span class="text-2xl font-bold text-primary">3</span>
            </div>
            <h3 class="text-lg font-bold text-foreground">Track & Deliver</h3>
            <p class="text-sm text-muted-foreground">Follow your shipment in real-time from pickup to delivery. Confirm completion securely.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- For Shippers -->
    <section class="py-20 bg-muted/30 border-y">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div>
            <div class="inline-flex items-center gap-2 bg-green-500/10 text-green-600 px-3 py-1 rounded-full text-sm font-medium mb-4">
              <Package class="size-4" />
              For Shippers
            </div>
            <h2 class="text-3xl font-bold text-foreground mb-4">Post Shipments, Get the Best Rates</h2>
            <p class="text-muted-foreground mb-6">Reach hundreds of verified drivers competing to transport your goods at fair prices.</p>
            <ul class="space-y-3">
              <li class="flex items-start gap-3">
                <CheckCircle2 class="size-5 text-green-600 mt-0.5 shrink-0" />
                <span class="text-sm"><strong>AI Price Estimate</strong> — Get fair market pricing based on distance and weight</span>
              </li>
              <li class="flex items-start gap-3">
                <CheckCircle2 class="size-5 text-green-600 mt-0.5 shrink-0" />
                <span class="text-sm"><strong>Competitive Bidding</strong> — Drivers bid down, you save more</span>
              </li>
              <li class="flex items-start gap-3">
                <CheckCircle2 class="size-5 text-green-600 mt-0.5 shrink-0" />
                <span class="text-sm"><strong>Real-Time Tracking</strong> — Know exactly where your load is</span>
              </li>
              <li class="flex items-start gap-3">
                <CheckCircle2 class="size-5 text-green-600 mt-0.5 shrink-0" />
                <span class="text-sm"><strong>Verified Drivers</strong> — Every transporter is Aadhaar-verified</span>
              </li>
            </ul>
          </div>
          <div class="bg-card border rounded-2xl p-6 shadow-sm space-y-4">
            <div class="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
              <div class="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                <MapPin class="size-5 text-primary" />
              </div>
              <div>
                <p class="text-xs text-muted-foreground">From</p>
                <p class="text-sm font-medium">Mumbai, Maharashtra</p>
              </div>
            </div>
            <div class="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
              <div class="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                <MapPin class="size-5 text-red-600" />
              </div>
              <div>
                <p class="text-xs text-muted-foreground">To</p>
                <p class="text-sm font-medium">Delhi, NCR</p>
              </div>
            </div>
            <div class="grid grid-cols-3 gap-3 text-center">
              <div class="p-3 bg-muted/50 rounded-lg">
                <p class="text-xs text-muted-foreground">Weight</p>
                <p class="text-sm font-bold">5,000 kg</p>
              </div>
              <div class="p-3 bg-muted/50 rounded-lg">
                <p class="text-xs text-muted-foreground">Vehicle</p>
                <p class="text-sm font-bold">19 MT</p>
              </div>
              <div class="p-3 bg-green-500/10 rounded-lg">
                <p class="text-xs text-green-600">Est. Price</p>
                <p class="text-sm font-bold text-green-600">₹45,000</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- For Drivers -->
    <section class="py-20 bg-background">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div class="order-2 lg:order-1 bg-card border rounded-2xl p-6 shadow-sm">
            <div class="space-y-3">
              <div class="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                <div>
                  <p class="text-sm font-bold">Electronics Shipment</p>
                  <p class="text-xs text-muted-foreground">Mumbai → Delhi • 5,000 kg</p>
                </div>
                <span class="text-sm font-bold text-primary">₹42,000</span>
              </div>
              <div class="flex items-center justify-between p-3 bg-primary/5 border border-primary/20 rounded-lg">
                <div>
                  <p class="text-sm font-bold">Steel Coil Transport</p>
                  <p class="text-xs text-muted-foreground">Pune → Nagpur • 8,000 kg</p>
                </div>
                <span class="text-sm font-bold text-primary">₹38,500</span>
              </div>
              <div class="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                <div>
                  <p class="text-sm font-bold">FMCG Goods</p>
                  <p class="text-xs text-muted-foreground">Chennai → Bangalore • 3,000 kg</p>
                </div>
                <span class="text-sm font-bold text-primary">₹18,000</span>
              </div>
            </div>
          </div>
          <div class="order-1 lg:order-2">
            <div class="inline-flex items-center gap-2 bg-blue-500/10 text-blue-600 px-3 py-1 rounded-full text-sm font-medium mb-4">
              <Truck class="size-4" />
              For Drivers
            </div>
            <h2 class="text-3xl font-bold text-foreground mb-4">Find Loads, Maximize Earnings</h2>
            <p class="text-muted-foreground mb-6">Browse available shipments near you and bid on loads that fit your routes.</p>
            <ul class="space-y-3">
              <li class="flex items-start gap-3">
                <CheckCircle2 class="size-5 text-blue-600 mt-0.5 shrink-0" />
                <span class="text-sm"><strong>Browse All Shipments</strong> — See every available load with full details</span>
              </li>
              <li class="flex items-start gap-3">
                <CheckCircle2 class="size-5 text-blue-600 mt-0.5 shrink-0" />
                <span class="text-sm"><strong>Submit Competitive Bids</strong> — Set your price and win loads</span>
              </li>
              <li class="flex items-start gap-3">
                <CheckCircle2 class="size-5 text-blue-600 mt-0.5 shrink-0" />
                <span class="text-sm"><strong>Manage Assignments</strong> — Track all your accepted shipments</span>
              </li>
              <li class="flex items-start gap-3">
                <CheckCircle2 class="size-5 text-blue-600 mt-0.5 shrink-0" />
                <span class="text-sm"><strong>Update Status Live</strong> — Keep shippers informed at every step</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats -->
    <section class="py-16 bg-primary text-primary-foreground">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div>
            <p class="text-3xl sm:text-4xl font-bold">10K+</p>
            <p class="text-sm opacity-80 mt-1">Shipments Completed</p>
          </div>
          <div>
            <p class="text-3xl sm:text-4xl font-bold">2K+</p>
            <p class="text-sm opacity-80 mt-1">Verified Drivers</p>
          </div>
          <div>
            <p class="text-3xl sm:text-4xl font-bold">50+</p>
            <p class="text-sm opacity-80 mt-1">Cities Connected</p>
          </div>
          <div>
            <p class="text-3xl sm:text-4xl font-bold">4.8</p>
            <p class="text-sm opacity-80 mt-1 flex items-center justify-center gap-1">
              <Star class="size-4 fill-current" /> Average Rating
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Trust Signals -->
    <section class="py-20 bg-muted/30 border-y">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-foreground mb-3">Why RoadLancer?</h2>
          <p class="text-muted-foreground">Built for India's logistics needs</p>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card class="border shadow-xs">
            <CardContent class="pt-6 space-y-3">
              <div class="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                <ShieldCheck class="size-5 text-primary" />
              </div>
              <h3 class="font-bold text-foreground">Aadhaar Verified</h3>
              <p class="text-sm text-muted-foreground">Every driver and shipper is identity-verified for safe transactions.</p>
            </CardContent>
          </Card>
          <Card class="border shadow-xs">
            <CardContent class="pt-6 space-y-3">
              <div class="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                <IndianRupee class="size-5 text-primary" />
              </div>
              <h3 class="font-bold text-foreground">Fair AI Pricing</h3>
              <p class="text-sm text-muted-foreground">Our AI estimates market rates so neither party overpays.</p>
            </CardContent>
          </Card>
          <Card class="border shadow-xs">
            <CardContent class="pt-6 space-y-3">
              <div class="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                <Clock class="size-5 text-primary" />
              </div>
              <h3 class="font-bold text-foreground">Real-Time Updates</h3>
              <p class="text-sm text-muted-foreground">Track shipments live from pickup to delivery with instant status changes.</p>
            </CardContent>
          </Card>
          <Card class="border shadow-xs">
            <CardContent class="pt-6 space-y-3">
              <div class="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                <Users class="size-5 text-primary" />
              </div>
              <h3 class="font-bold text-foreground">Competitive Bidding</h3>
              <p class="text-sm text-muted-foreground">Multiple drivers bid on your load — you pick the best offer.</p>
            </CardContent>
          </Card>
          <Card class="border shadow-xs">
            <CardContent class="pt-6 space-y-3">
              <div class="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                <MapPin class="size-5 text-primary" />
              </div>
              <h3 class="font-bold text-foreground">Pan-India Network</h3>
              <p class="text-sm text-muted-foreground">Connecting shippers and drivers across all major Indian cities.</p>
            </CardContent>
          </Card>
          <Card class="border shadow-xs">
            <CardContent class="pt-6 space-y-3">
              <div class="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                <Truck class="size-5 text-primary" />
              </div>
              <h3 class="font-bold text-foreground">All Vehicle Types</h3>
              <p class="text-sm text-muted-foreground">From Tempos to 32-ton trailers — find the right vehicle for any load.</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="py-20 bg-background">
      <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="text-3xl sm:text-4xl font-bold text-foreground mb-4">Ready to Move Your First Load?</h2>
        <p class="text-muted-foreground mb-8 max-w-xl mx-auto">
          Join thousands of shippers and drivers already using RoadLancer to transport goods across India.
        </p>
        <div class="flex flex-col sm:flex-row gap-3 justify-center">
          <Button size="lg" class="px-8 font-semibold" @click="router.push('/register')">
            Get Started Free
            <ArrowRight class="size-5 ml-2" />
          </Button>
          <Button size="lg" variant="outline" class="px-8 font-semibold" @click="router.push('/login')">
            Sign In
          </Button>
        </div>
      </div>
    </section>
  </div>
</template>
