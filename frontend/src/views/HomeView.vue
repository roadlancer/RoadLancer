<script lang="ts" setup>
import { watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { user, loading } = useAuth()

watch([user, loading], ([u, l]) => {
  if (!l && !u) {
    router.replace('/login')
  }
})
</script>

<template>
  <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center p-8">
    <div v-if="loading" class="text-center">
      <div class="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4" />
      <p class="text-gray-500">Loading...</p>
    </div>

    <div v-else-if="user" class="text-center max-w-lg">
      <div class="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
        <span class="text-2xl font-bold text-blue-700">{{ user.name?.charAt(0)?.toUpperCase() }}</span>
      </div>
      <h1 class="text-3xl font-bold text-gray-900 mb-2">
        Welcome back, {{ user.name }}!
      </h1>
      <p class="text-gray-500 mb-8">
        You are signed in as <span class="font-medium text-gray-700 capitalize">{{ user.role }}</span>.
      </p>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div class="bg-white rounded-xl border border-gray-200 p-5 text-center">
          <div class="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center mx-auto mb-3">
            <svg class="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z" />
            </svg>
          </div>
          <p class="text-sm font-medium text-gray-500">Role</p>
          <p class="text-lg font-bold text-gray-900 capitalize">{{ user.role }}</p>
        </div>

        <div class="bg-white rounded-xl border border-gray-200 p-5 text-center">
          <div class="w-10 h-10 bg-green-50 rounded-lg flex items-center justify-center mx-auto mb-3">
            <svg class="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75" />
            </svg>
          </div>
          <p class="text-sm font-medium text-gray-500">Email</p>
          <p class="text-sm font-bold text-gray-900 truncate">{{ user.email }}</p>
        </div>

        <div class="bg-white rounded-xl border border-gray-200 p-5 text-center">
          <div class="w-10 h-10 bg-purple-50 rounded-lg flex items-center justify-center mx-auto mb-3">
            <svg class="w-5 h-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 1.5H8.25A2.25 2.25 0 0 0 6 3.75v16.5a2.25 2.25 0 0 0 2.25 2.25h7.5A2.25 2.25 0 0 0 18 20.25V3.75a2.25 2.25 0 0 0-2.25-2.25H13.5m-3 0V3h3V1.5m-3 0h3m-3 18.75h3" />
            </svg>
          </div>
          <p class="text-sm font-medium text-gray-500">Phone</p>
          <p class="text-sm font-bold text-gray-900">{{ user.phone || 'Not set' }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
