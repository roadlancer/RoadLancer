import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import HomeView from '@/views/HomeView.vue'
import { user, loading, fetchSession } from '@/composables/useAuth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { guest: true },
    },
  ],
})

router.beforeEach(async (to) => {
  // Ensure session is loaded on first navigation
  if (loading.value && !user.value) {
    await fetchSession()
  }

  const isAuthenticated = !!user.value
  const isLoading = loading.value

  // Authenticated user trying to access login → redirect to home
  if (to.meta.guest && isAuthenticated) {
    return { name: 'home' }
  }

  // Protected route and not authenticated → redirect to login
  if (to.meta.requiresAuth && !isAuthenticated && !isLoading) {
    return { name: 'login' }
  }
})

export default router
