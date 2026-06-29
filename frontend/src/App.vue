<script lang="ts" setup>
import NavBar from '@/components/NavBar.vue'
import Footer from '@/components/Footer.vue'
</script>

<template>
  <div class="min-h-screen flex flex-col bg-background">
    <NavBar />
    <main class="flex-1 flex flex-col">
      <router-view />
    </main>
    <Footer />
  </div>
</template>
