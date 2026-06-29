<script lang="ts" setup>
import { watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { user, loading } = useAuth()

watch([user, loading], ([u, l]) => {
  if (!l) {
    if (!u) router.replace('/login')
    else if (u.role !== 'shipper') router.replace('/')
  }
})
</script>

<template>
  <div class="flex-1 flex items-center justify-center p-8">
    <div v-if="loading" class="text-center">
      <p class="text-muted-foreground">Loading...</p>
    </div>
    <div v-else-if="user?.role === 'shipper'" class="text-center max-w-lg">
      <h1 class="text-3xl font-bold text-foreground mb-2">Shipper Dashboard</h1>
      <p class="text-muted-foreground">Welcome, {{ user.name }}. This is your shipper portal.</p>
    </div>
  </div>
</template>
