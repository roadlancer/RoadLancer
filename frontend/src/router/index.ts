import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import HomeView from '@/views/HomeView.vue'
import DriverDashboard from '@/views/DriverDashboard.vue'
import ShipperDashboard from '@/views/ShipperDashboard.vue'
import AdminDashboard from '@/views/AdminDashboard.vue'
import PendingUsers from '@/views/PendingUsers.vue'
import GetValidated from '@/views/GetValidated.vue'
import AdminVerificationReview from '@/views/AdminVerificationReview.vue'
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
    {
      path: '/driver',
      name: 'driver',
      component: DriverDashboard,
      meta: { requiresAuth: true, role: 'driver' },
    },
    {
      path: '/shipper',
      name: 'shipper',
      component: ShipperDashboard,
      meta: { requiresAuth: true, role: 'shipper' },
    },
    {
      path: '/get-validated',
      name: 'get-validated',
      component: GetValidated,
      meta: { requiresAuth: true, role: 'driver' },
    },
    {
      path: '/get-validated-shipper',
      name: 'get-validated-shipper',
      component: GetValidated,
      meta: { requiresAuth: true, role: 'shipper' },
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminDashboard,
      meta: { requiresAuth: true, role: 'admin' },
    },
    {
      path: '/admin/pending',
      name: 'admin-pending',
      component: PendingUsers,
      meta: { requiresAuth: true, role: 'admin' },
    },
    {
      path: '/admin/verifications',
      name: 'admin-verifications',
      component: AdminVerificationReview,
      meta: { requiresAuth: true, role: 'admin' },
    },
  ],
})

router.beforeEach(async (to) => {
  if (loading.value && !user.value) {
    await fetchSession()
  }

  const isAuthenticated = !!user.value
  const isLoading = loading.value
  const userRole = user.value?.role

  if (to.meta.guest && isAuthenticated) {
    return { name: 'home' }
  }

  if (to.meta.requiresAuth && !isAuthenticated && !isLoading) {
    return { name: 'login' }
  }

  if (to.meta.role && userRole && to.meta.role !== userRole) {
    return { name: 'home' }
  }
})

export default router
