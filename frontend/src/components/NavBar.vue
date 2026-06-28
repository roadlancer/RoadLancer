<script lang="ts" setup>
import { useAuth } from '@/composables/useAuth'

const { user, loading, signOut } = useAuth()
</script>

<template>
  <nav class="bg-white border-b border-gray-200 px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between h-16 items-center">
      <!-- Logo -->
      <router-link to="/" class="flex items-center gap-2.5">
        <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
          <svg class="w-4.5 h-4.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 18.75a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 0 1-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m3 0h1.125c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H18.75m-7.5-3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
          </svg>
        </div>
        <span class="text-lg font-bold text-gray-900 hidden sm:block">RoadLancer</span>
      </router-link>

      <!-- Right side — User info -->
      <div v-if="!loading && user" class="flex items-center gap-4">
        <div class="text-right hidden sm:block">
          <p class="text-sm font-medium text-gray-900">{{ user.name }}</p>
          <p class="text-xs text-gray-500 capitalize">{{ user.role }}</p>
        </div>

        <!-- User avatar -->
        <div class="w-9 h-9 bg-blue-100 rounded-full flex items-center justify-center">
          <span class="text-sm font-semibold text-blue-700">
            {{ user.name?.charAt(0)?.toUpperCase() }}
          </span>
        </div>

        <!-- Sign out button -->
        <button
          @click="signOut"
          class="text-sm text-gray-500 hover:text-gray-700 hover:bg-gray-100 px-3 py-1.5 rounded-lg transition font-medium"
        >
          Sign out
        </button>
      </div>

      <!-- Loading state -->
      <div v-else-if="loading" class="flex items-center gap-3">
        <div class="w-9 h-9 bg-gray-200 rounded-full animate-pulse" />
      </div>

      <!-- Not logged in -->
      <router-link
        v-else
        to="/login"
        class="text-sm font-medium text-blue-600 hover:text-blue-700"
      >
        Sign in
      </router-link>
    </div>
  </nav>
</template>
