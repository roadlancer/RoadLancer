import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, fireEvent } from '@testing-library/vue'
import { ref, nextTick } from 'vue'
import { renderDashboard } from './renderDashboard'

// --- Mock Router ---
const mockRouterReplace = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({
    replace: mockRouterReplace,
  }),
}))

// --- Mock Auth Composable ---
const mockAuthUser = ref<any>(null)
const mockAuthLoading = ref(true)
vi.mock('@/composables/useAuth', () => ({
  useAuth: () => ({
    user: mockAuthUser,
    loading: mockAuthLoading,
  }),
}))

// --- Mock Admin Users Composable ---
const mockUsers = ref<any[]>([])
const mockLoadingUsers = ref(false)
const mockError = ref<any>(null)
const mockSearchQuery = ref('')
const mockActiveTab = ref('all')
const mockPendingCount = ref(0)
const mockRejectedCount = ref(0)
const mockSuspendMutate = vi.fn()
const mockSuspendIsPending = ref(false)
const mockRefetchAll = vi.fn()

vi.mock('@/composables/useAdminUsers', () => ({
  useAdminUsers: () => ({
    data: mockUsers,
    isLoading: mockLoadingUsers,
    error: mockError,
    searchQuery: mockSearchQuery,
    activeTab: mockActiveTab,
    pendingCount: { data: mockPendingCount },
    rejectedCount: { data: mockRejectedCount },
    suspendMutation: {
      mutate: mockSuspendMutate,
      isPending: mockSuspendIsPending,
    },
    refetchAll: mockRefetchAll,
  }),
}))

describe('AdminDashboard Component Tests', () => {

  beforeEach(() => {
    vi.clearAllMocks()

    // Default to authenticated admin user
    mockAuthUser.value = {
      id: 'admin-1',
      name: 'Super Admin',
      email: 'admin@roadlancer.com',
      role: 'admin',
    }
    mockAuthLoading.value = false

    // Default users and state
    mockUsers.value = []
    mockLoadingUsers.value = false
    mockError.value = null
    mockSearchQuery.value = ''
    mockActiveTab.value = 'all'
    mockPendingCount.value = 4
    mockRejectedCount.value = 1
    mockSuspendIsPending.value = false
  })

  describe('Authentication & Access Control', () => {
    it('renders skeleton loaders while auth session is loading', () => {
      mockAuthLoading.value = true
      mockAuthUser.value = null

      renderDashboard()

      expect(screen.queryByText('Admin Dashboard')).not.toBeInTheDocument()
      expect(mockRouterReplace).not.toHaveBeenCalled()
    })

    it('redirects unauthenticated user to /login when auth loading completes', async () => {
      renderDashboard()

      mockAuthLoading.value = false
      mockAuthUser.value = null
      await nextTick()

      expect(mockRouterReplace).toHaveBeenCalledWith('/login')
    })

    it('redirects non-admin user (e.g. driver) to /login', async () => {
      renderDashboard()

      mockAuthLoading.value = false
      mockAuthUser.value = {
        id: 'driver-1',
        name: 'Test Driver',
        email: 'driver@roadlancer.com',
        role: 'driver',
      }
      await nextTick()

      expect(mockRouterReplace).toHaveBeenCalledWith('/login')
    })

    it('renders dashboard heading and description when authenticated as admin', () => {
      renderDashboard()

      expect(screen.getByText('Admin Dashboard')).toBeInTheDocument()
      expect(screen.getByText('Manage drivers, shippers, and platform users')).toBeInTheDocument()
      expect(mockRouterReplace).not.toHaveBeenCalled()
    })
  })

  describe('Summary Stats Cards', () => {
    it('computes and renders correct counts across statistics cards', () => {
      mockUsers.value = [
        { id: '1', role: 'driver', suspended: false },
        { id: '2', role: 'driver', suspended: true },
        { id: '3', role: 'shipper', suspended: false },
        { id: '4', role: 'admin', suspended: false },
      ]
      mockPendingCount.value = 12
      mockRejectedCount.value = 3

      renderDashboard()

      expect(screen.getByText('Total Users')).toBeInTheDocument()
      expect(screen.getAllByText('Drivers').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('Shippers').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('Admins').length).toBeGreaterThanOrEqual(1)
      expect(screen.getByText('Pending')).toBeInTheDocument()
      expect(screen.getByText('Rejected')).toBeInTheDocument()
      expect(screen.getAllByText('Suspended').length).toBeGreaterThanOrEqual(1)

      // Total users: 4
      expect(screen.getByText('4')).toBeInTheDocument()
      // Pending: 12
      expect(screen.getByText('12')).toBeInTheDocument()
      // Rejected: 3
      expect(screen.getByText('3')).toBeInTheDocument()
    })
  })

  describe('User List Display & States', () => {
    it('shows loading skeleton rows while user list is fetching', () => {
      mockLoadingUsers.value = true

      renderDashboard()

      expect(screen.queryByText('No users found')).not.toBeInTheDocument()
      expect(screen.getByRole('button', { name: /refresh/i })).toBeDisabled()
    })

    it('shows empty state message when users array is empty', () => {
      mockUsers.value = []
      mockLoadingUsers.value = false

      renderDashboard()

      expect(screen.getByText('No users found')).toBeInTheDocument()
    })

    it('renders table headers and populated user rows with details', () => {
      mockUsers.value = [
        {
          id: 'u-101',
          name: 'John Driver',
          email: 'john@test.com',
          role: 'driver',
          phone: '+1 555-0101',
          suspended: false,
        },
        {
          id: 'u-102',
          name: 'Jane Shipper',
          email: 'jane@test.com',
          role: 'shipper',
          phone: null,
          suspended: true,
        },
      ]

      renderDashboard()

      // Table headers
      expect(screen.getByText('User')).toBeInTheDocument()
      expect(screen.getByText('Role')).toBeInTheDocument()
      expect(screen.getByText('Phone')).toBeInTheDocument()
      expect(screen.getByText('Status')).toBeInTheDocument()
      expect(screen.getByText('Actions')).toBeInTheDocument()

      // John Driver row
      expect(screen.getByText('John Driver')).toBeInTheDocument()
      expect(screen.getByText('john@test.com')).toBeInTheDocument()
      expect(screen.getByText('+1 555-0101')).toBeInTheDocument()
      expect(screen.getByText('Active')).toBeInTheDocument()

      // Jane Shipper row
      expect(screen.getByText('Jane Shipper')).toBeInTheDocument()
      expect(screen.getByText('jane@test.com')).toBeInTheDocument()
      expect(screen.getByText('—')).toBeInTheDocument()
      const suspendedBadges = screen.getAllByText('Suspended')
      expect(suspendedBadges.length).toBeGreaterThanOrEqual(1)
    })
  })

  describe('Search & Role Tab Filtering', () => {
    beforeEach(() => {
      mockUsers.value = [
        { id: '1', name: 'Alice Driver', email: 'alice@driver.com', role: 'driver', suspended: false },
        { id: '2', name: 'Bob Shipper', email: 'bob@shipper.com', role: 'shipper', suspended: false },
        { id: '3', name: 'Charlie Admin', email: 'charlie@admin.com', role: 'admin', suspended: false },
      ]
    })

    it('filters users by active role tab', async () => {
      renderDashboard()

      // Initially all users visible
      expect(screen.getByText('Alice Driver')).toBeInTheDocument()
      expect(screen.getByText('Bob Shipper')).toBeInTheDocument()
      expect(screen.getByText('Charlie Admin')).toBeInTheDocument()

      // Switch active tab to driver
      mockActiveTab.value = 'driver'
      await screen.findByText('Alice Driver')

      expect(screen.getByText('Alice Driver')).toBeInTheDocument()
      expect(screen.queryByText('Bob Shipper')).not.toBeInTheDocument()
      expect(screen.queryByText('Charlie Admin')).not.toBeInTheDocument()
    })

    it('filters users by search query (name or email)', async () => {
      renderDashboard()

      // Search by name
      mockSearchQuery.value = 'bob'
      await screen.findByText('Bob Shipper')

      expect(screen.queryByText('Alice Driver')).not.toBeInTheDocument()
      expect(screen.getByText('Bob Shipper')).toBeInTheDocument()
      expect(screen.queryByText('Charlie Admin')).not.toBeInTheDocument()

      // Search by email substring
      mockSearchQuery.value = 'admin.com'
      await screen.findByText('Charlie Admin')

      expect(screen.queryByText('Alice Driver')).not.toBeInTheDocument()
      expect(screen.queryByText('Bob Shipper')).not.toBeInTheDocument()
      expect(screen.getByText('Charlie Admin')).toBeInTheDocument()
    })
  })

  describe('Refresh & Error Handling', () => {
    it('calls refetchAll when clicking the Refresh button', async () => {
      renderDashboard()

      const refreshBtn = screen.getByRole('button', { name: /refresh/i })
      await fireEvent.click(refreshBtn)

      expect(mockRefetchAll).toHaveBeenCalledTimes(1)
    })

    it('displays error alert when query returns an error', () => {
      mockError.value = { message: 'Failed to fetch admin users data' }

      renderDashboard()

      expect(screen.getByText('Failed to fetch admin users data')).toBeInTheDocument()
    })
  })

  describe('User Suspension Workflows', () => {
    beforeEach(() => {
      mockUsers.value = [
        {
          id: 'driver-99',
          name: 'Dave Driver',
          email: 'dave@road.com',
          role: 'driver',
          suspended: false,
        },
        {
          id: 'shipper-88',
          name: 'Sara Shipper',
          email: 'sara@ship.com',
          role: 'shipper',
          suspended: false,
        },
        {
          id: 'suspended-77',
          name: 'Bad Driver',
          email: 'bad@road.com',
          role: 'driver',
          suspended: true,
        },
        {
          id: 'admin-66',
          name: 'Other Admin',
          email: 'other@admin.com',
          role: 'admin',
          suspended: false,
        },
      ]
    })

    it('does not display Suspend or Unsuspend buttons for admin role users', () => {
      renderDashboard()

      const adminRow = screen.getByText('Other Admin').closest('tr')!
      expect(adminRow.textContent).not.toContain('Suspend')
      expect(adminRow.textContent).not.toContain('Unsuspend')
    })

    it('clicking Suspend opens dialog with driver-specific reasons', async () => {
      renderDashboard()

      // Find Suspend button for Dave Driver
      const driverRow = screen.getByText('Dave Driver').closest('tr')!
      const suspendBtn = driverRow.querySelector('button')!
      await fireEvent.click(suspendBtn)

      // Dialog should be visible
      expect(screen.getByText('Suspend User')).toBeInTheDocument()
      expect(screen.getByText(/Select a reason for suspending/i)).toBeInTheDocument()
      expect(screen.getByText('Repeated late deliveries')).toBeInTheDocument()
      expect(screen.getByText('Poor driving behavior reported')).toBeInTheDocument()
    })

    it('clicking Suspend on shipper opens dialog with shipper-specific reasons', async () => {
      renderDashboard()

      const shipperRow = screen.getByText('Sara Shipper').closest('tr')!
      const suspendBtn = shipperRow.querySelector('button')!
      await fireEvent.click(suspendBtn)

      expect(screen.getByText('Fraudulent shipment listings')).toBeInTheDocument()
      expect(screen.getByText('Non-payment for completed deliveries')).toBeInTheDocument()
    })

    it('requires a reason before confirm button is enabled and triggers suspend mutation', async () => {
      renderDashboard()

      const driverRow = screen.getByText('Dave Driver').closest('tr')!
      await fireEvent.click(driverRow.querySelector('button')!)

      const confirmBtn = screen.getByRole('button', { name: /confirm suspension/i })
      expect(confirmBtn).toBeDisabled()

      // Select a reason radio input
      const radioInput = screen.getByDisplayValue('Repeated late deliveries')
      await fireEvent.click(radioInput)

      expect(confirmBtn).not.toBeDisabled()

      await fireEvent.click(confirmBtn)

      expect(mockSuspendMutate).toHaveBeenCalledWith(
        { userId: 'driver-99', suspended: true },
        expect.any(Object)
      )
    })

    it('clicking Unsuspend on a suspended user triggers unsuspend mutation directly', async () => {
      renderDashboard()

      const suspendedRow = screen.getByText('Bad Driver').closest('tr')!
      const unsuspendBtn = suspendedRow.querySelector('button')!
      await fireEvent.click(unsuspendBtn)

      expect(mockSuspendMutate).toHaveBeenCalledWith({
        userId: 'suspended-77',
        suspended: false,
      })
    })
  })
})
