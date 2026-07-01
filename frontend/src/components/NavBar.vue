<script lang="ts" setup>
import { useAuth } from '@/composables/useAuth'
import { useVerificationStatus } from '@/composables/useVerificationStatus'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Truck, LayoutDashboard, LogOut, ShieldCheck } from '@lucide/vue'

const { user, loading, signOut } = useAuth()
const { isVerified } = useVerificationStatus()
</script>

<template>
  <nav class="sticky top-0 z-50 bg-background/80 backdrop-blur-md border-b border-gray-200 px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between h-16 items-center">
      <router-link to="/" class="flex items-center gap-2.5">
        <div class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
          <Truck class="size-4 text-primary-foreground" />
        </div>
        <span class="text-lg font-bold text-foreground hidden sm:block">RoadLancer</span>
      </router-link>

      <router-link
        v-if="!loading && user && (user.role === 'driver' || user.role === 'shipper' || user.role === 'admin')"
        :to="user.role === 'admin' ? '/admin' : user.role === 'driver' ? '/driver' : '/shipper'"
        class="flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground transition"
      >
        <LayoutDashboard class="size-4" />
        <span class="hidden sm:inline">Dashboard</span>
      </router-link>

      <div v-if="!loading && user" class="flex items-center gap-3">
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

      <div v-else-if="loading" class="flex items-center gap-3">
        <Avatar>
          <AvatarFallback class="animate-pulse" />
        </Avatar>
      </div>

      <router-link v-else to="/login">
        <Button size="sm">Sign in</Button>
      </router-link>
    </div>
  </nav>
</template>
