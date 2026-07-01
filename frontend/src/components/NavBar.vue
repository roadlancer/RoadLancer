<script lang="ts" setup>
import { ref, onMounted, watch } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { authClient } from '@/lib/auth-client'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Truck, LayoutDashboard, LogOut, ShieldCheck } from '@lucide/vue'

const { user, loading, signOut } = useAuth()
const isVerified = ref<boolean | null>(null)

async function checkVerification() {
  if (!user.value || user.value.role === 'admin') {
    isVerified.value = null
    return
  }
  try {
    const session = await authClient.getSession()
    const token = (session.data as any)?.session?.token
    if (!token) return

    const res = await fetch('/api/verification/status', {
      headers: { Authorization: `Bearer ${token}` },
    })
    const data = await res.json()
    isVerified.value = data.status === 'approved'
  } catch {
    isVerified.value = false
  }
}

onMounted(() => {
  if (user.value) checkVerification()
})

watch(user, (u) => {
  if (u) checkVerification()
  else isVerified.value = null
})
</script>

<template>
  <nav class="sticky top-0 z-50 bg-background/80 backdrop-blur-md border-b border-gray-200 px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between h-16 items-center">
      <!-- Logo -->
      <router-link to="/" class="flex items-center gap-2.5">
        <div class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
          <Truck class="size-4 text-primary-foreground" />
        </div>
        <span class="text-lg font-bold text-foreground hidden sm:block">RoadLancer</span>
      </router-link>

      <!-- Center — Dashboard link (role-based) -->
      <router-link
        v-if="!loading && user && (user.role === 'driver' || user.role === 'shipper' || user.role === 'admin')"
        :to="user.role === 'admin' ? '/admin' : user.role === 'driver' ? '/driver' : '/shipper'"
        class="flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground transition"
      >
        <LayoutDashboard class="size-4" />
        <span class="hidden sm:inline">Dashboard</span>
      </router-link>

      <!-- Right side — User info -->
      <div v-if="!loading && user" class="flex items-center gap-3">
        <!-- Get Validated button (drivers & shippers who are not verified) -->
        <router-link
          v-if="(user.role === 'driver' || user.role === 'shipper') && isVerified === false"
          :to="user.role === 'driver' ? '/get-validated' : '/get-validated-shipper'"
        >
          <Button variant="outline" size="sm" class="border-primary/50 text-primary hover:bg-primary/5">
            <ShieldCheck class="size-4 mr-1" />
            <span class="hidden sm:inline">Get Validated</span>
          </Button>
        </router-link>

        <div class="text-right hidden sm:block">
          <p class="text-sm font-medium text-foreground capitalize">{{ user.role }}</p>
        </div>

        <Avatar>
          <AvatarFallback>{{ user.name?.charAt(0)?.toUpperCase() }}</AvatarFallback>
        </Avatar>

        <Button variant="ghost" size="sm" @click="signOut">
          <LogOut class="size-4" />
          <span class="hidden sm:inline">Sign out</span>
        </Button>
      </div>

      <!-- Loading state -->
      <div v-else-if="loading" class="flex items-center gap-3">
        <Avatar>
          <AvatarFallback class="animate-pulse" />
        </Avatar>
      </div>

      <!-- Not logged in -->
      <router-link v-else to="/login">
        <Button size="sm">Sign in</Button>
      </router-link>
    </div>
  </nav>
</template>
