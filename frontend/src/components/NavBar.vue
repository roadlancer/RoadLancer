<script lang="ts" setup>
import { useAuth } from '@/composables/useAuth'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Truck, LayoutDashboard, LogOut, ShieldCheck } from '@lucide/vue'
import { ref } from 'vue'
import SupportEmailSimulatorModal from '@/components/SupportEmailSimulatorModal.vue'

const { user, loading, signOut } = useAuth()
const supportModalOpen = ref(false)
</script>

<template>
  <nav class="sticky top-0 z-50 bg-background/80 backdrop-blur-md border-b border-gray-200 px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between h-16 items-center">
      <div class="flex items-center gap-6 sm:gap-8">
        <router-link v-if="!loading && !user" to="/" class="flex items-center gap-2.5">
          <div class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <Truck class="size-4 text-primary-foreground" />
          </div>
          <span class="text-lg font-bold text-foreground hidden sm:block">RoadLancer</span>
        </router-link>

        <router-link
          v-if="!loading && user && (user.role === 'driver' || user.role === 'shipper' || user.role === 'admin')"
          :to="user.role === 'admin' ? '/admin' : user.role === 'driver' ? '/driver' : '/shipper'"
          class="flex items-center gap-2 text-base font-medium text-muted-foreground hover:text-foreground transition"
        >
          <LayoutDashboard class="size-5" />
          <span class="hidden sm:inline">Dashboard</span>
        </router-link>

        <template v-if="!loading && user && user.role === 'admin'">
          <router-link
            to="/admin/verifications"
            class="flex items-center gap-2 text-base font-medium text-muted-foreground hover:text-foreground transition"
            active-class="text-foreground font-semibold"
          >
            <ShieldCheck class="size-5 text-primary" />
            <span class="hidden md:inline">Document Verification</span>
          </router-link>
          <router-link
            to="/admin/support"
            class="flex items-center gap-2 text-base font-medium text-muted-foreground hover:text-foreground transition"
            active-class="text-foreground font-semibold"
          >
            <span class="text-base">🎧</span>
            <span class="hidden md:inline">Support Desk</span>
          </router-link>
        </template>

        <button
          v-if="!loading && user"
          @click="supportModalOpen = true"
          class="flex items-center gap-1.5 text-xs font-bold text-teal-700 hover:text-teal-900 transition bg-teal-50/80 hover:bg-teal-100 px-3 py-1.5 rounded-xl border border-teal-200/80 shadow-sm cursor-pointer"
        >
          <span>📧</span>
          <span class="hidden sm:inline">Help & Support</span>
        </button>
      </div>

      <div v-if="!loading && user" class="flex items-center gap-3">
        <a
          :href="user.role === 'admin' ? '/admin/profile' : user.role === 'driver' ? '/driver/profile' : '/shipper/profile'"
          class="inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium h-10 px-4 bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm flex items-center gap-2.5 no-underline"
        >
          <Avatar class="size-6 border border-primary-foreground/20">
            <AvatarFallback class="text-xs bg-primary-foreground text-primary font-bold">{{ (user.name || user.role || '?').charAt(0).toUpperCase() }}</AvatarFallback>
          </Avatar>
          <span class="text-sm font-medium capitalize hidden sm:inline">{{ user.name || user.role }}</span>
        </a>

        <Button class="h-10 px-4 bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm transition" @click="signOut">
          <LogOut class="size-4 mr-1 sm:mr-1.5" />
          <span class="hidden sm:inline">Sign out</span>
        </Button>
      </div>

      <div v-else-if="loading" class="flex items-center gap-3">
        <Avatar>
          <AvatarFallback class="animate-pulse" />
        </Avatar>
      </div>

      <a v-else href="/login" class="inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium h-10 px-4 bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm no-underline">
        Sign in
      </a>
    </div>

    <SupportEmailSimulatorModal
      :open="supportModalOpen"
      @update:open="supportModalOpen = $event"
    />
  </nav>
</template>
