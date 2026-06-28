<script lang="ts" setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from '@/components/NavBar.vue'

const route = useRoute()
const showNavBar = computed(() => route.name !== 'login')
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <NavBar v-if="showNavBar" />
    <main>
      <router-view />
    </main>
  </div>
</template>
