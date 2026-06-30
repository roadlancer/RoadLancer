<script lang="ts" setup>
import { useAuth } from '@/composables/useAuth'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Truck, LayoutDashboard, LogOut } from '@lucide/vue'

const { user, loading, signOut } = useAuth()
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
      <div v-if="!loading && user" class="flex items-center gap-4">
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
