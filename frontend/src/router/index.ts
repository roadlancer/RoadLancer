import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import HomeView from '@/views/HomeView.vue'
import DriverDashboard from '@/views/DriverDashboard.vue'
import ShipperDashboard from '@/views/ShipperDashboard.vue'
import AdminDashboard from '@/views/AdminDashboard.vue'
import AdminProfile from '@/views/AdminProfile.vue'
import GetValidated from '@/views/GetValidated.vue'
import AdminVerificationReview from '@/views/AdminVerificationReview.vue'
import ShipmentDetailView from '@/views/ShipmentDetailView.vue'
import UserProfile from '@/views/UserProfile.vue'
import AdminSupportDesk from '@/views/AdminSupportDesk.vue'
import { user, loading, fetchSession } from '@/composables/useAuth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {},
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { guest: true },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
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
      path: '/driver/profile',
      name: 'driver-profile',
      component: UserProfile,
      meta: { requiresAuth: true, role: 'driver' },
    },
    {
      path: '/shipper/profile',
      name: 'shipper-profile',
      component: UserProfile,
      meta: { requiresAuth: true, role: 'shipper' },
    },
    {
      path: '/get-validated',
      name: 'get-validated',
      component: GetValidated,
      meta: { requiresAuth: true },
    },
    {
      path: '/get-validated-shipper',
      redirect: '/get-validated',
    },
    {
      path: '/shipments/:id',
      name: 'shipment-detail',
      component: ShipmentDetailView,
      meta: { requiresAuth: true },
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminDashboard,
      meta: { requiresAuth: true, role: 'admin' },
    },
    {
      path: '/admin/profile',
      name: 'admin-profile',
      component: AdminProfile,
      meta: { requiresAuth: true, role: 'admin' },
    },
    {
      path: '/admin/pending',
      redirect: '/admin/verifications',
    },
    {
      path: '/admin/verifications',
      name: 'admin-verifications',
      component: AdminVerificationReview,
      meta: { requiresAuth: true, role: 'admin' },
    },
    {
      path: '/admin/support',
      name: 'admin-support',
      component: AdminSupportDesk,
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
