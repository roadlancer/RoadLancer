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
const mockVerifiedCount = ref(0)
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
    verifiedCount: { data: mockVerifiedCount },
    suspendMutation: {
      mutate: mockSuspendMutate,
      isPending: mockSuspendIsPending,
    },
    refetchAll: mockRefetchAll,
  }),
}))

// --- Mock Admin Agents Composable ---
const mockAgents = ref<any[]>([])
const mockLoadingAgents = ref(false)
const mockDeactivateAgent = { mutate: vi.fn(), isPending: ref(false) }
const mockActivateAgent = { mutate: vi.fn(), isPending: ref(false) }

vi.mock('@/composables/useAdminAgents', () => ({
  useAdminAgents: () => ({
    data: mockAgents,
    isLoading: mockLoadingAgents,
    deactivateAgent: mockDeactivateAgent,
    activateAgent: mockActivateAgent,
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
      isSupreme: true,
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
    mockVerifiedCount.value = 15
    mockSuspendIsPending.value = false
  })

  describe('Authentication & Access Control', () => {
    it('renders skeleton loaders while auth session is loading', () => {
      mockAuthLoading.value = true
      mockAuthUser.value = null

      renderDashboard()

      expect(screen.queryByText('Total Users')).not.toBeInTheDocument()
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

    it('renders dashboard content when authenticated as admin', () => {
      renderDashboard()

      expect(screen.getByText('Total Users')).toBeInTheDocument()
      expect(mockRouterReplace).not.toHaveBeenCalled()
    })
  })

  describe('Summary Stats Cards', () => {
    it('computes and renders correct counts across statistics cards', () => {
      mockUsers.value = [
        { id: '1', role: 'driver', suspended: false, verification_status: 'approved' },
        { id: '2', role: 'driver', suspended: true, verification_status: 'none' },
        { id: '3', role: 'shipper', suspended: false, verification_status: 'pending' },
        { id: '4', role: 'admin', suspended: false, verification_status: 'approved' },
      ]
      mockPendingCount.value = 12
      mockRejectedCount.value = 3

      renderDashboard()

      expect(screen.getByText('Total Users')).toBeInTheDocument()
      expect(screen.getAllByText('Drivers').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('Shippers').length).toBeGreaterThanOrEqual(1)
      expect(screen.queryByText('Admins')).not.toBeInTheDocument()
      expect(screen.getAllByText('Pending').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('Rejected').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('Suspended').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('Unverified').length).toBeGreaterThanOrEqual(1)

      // Total users: 3 (admin excluded)
      expect(screen.getAllByText('3').length).toBeGreaterThanOrEqual(1)
      // Pending: 12
      expect(screen.getByText('12')).toBeInTheDocument()
      // Rejected: 3
      expect(screen.getAllByText('3').length).toBeGreaterThanOrEqual(1)
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
      expect(screen.getAllByText('—').length).toBeGreaterThanOrEqual(1)
      const suspendedBadges = screen.getAllByText('Suspended')
      expect(suspendedBadges.length).toBeGreaterThanOrEqual(1)
    })
  })

  describe('Search & Role Tab Filtering', () => {
    beforeEach(() => {
      mockUsers.value = [
        {
          id: 'u-1',
          name: 'Alice Driver',
          email: 'alice@transporter.com',
          role: 'driver',
          phone: null,
          suspended: false,
        },
        {
          id: 'u-2',
          name: 'Bob Shipper',
          email: 'bob@cargo.com',
          role: 'shipper',
          phone: null,
          suspended: false,
        },
      ]
    })

    it('filters users by active role tab', async () => {
      renderDashboard()

      expect(screen.getByText('Alice Driver')).toBeInTheDocument()
      expect(screen.getByText('Bob Shipper')).toBeInTheDocument()

      mockActiveTab.value = 'driver'
      await nextTick()

      expect(screen.getByText('Alice Driver')).toBeInTheDocument()
      expect(screen.queryByText('Bob Shipper')).not.toBeInTheDocument()
    })

    it('filters users by search query (name or email)', async () => {
      renderDashboard()

      mockSearchQuery.value = 'cargo'
      await nextTick()

      expect(screen.queryByText('Alice Driver')).not.toBeInTheDocument()
      expect(screen.getByText('Bob Shipper')).toBeInTheDocument()
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
      mockError.value = { message: 'Database connection failed' }

      renderDashboard()

      expect(screen.getByText('Database connection failed')).toBeInTheDocument()
    })
  })

  describe('User Suspension Workflows', () => {
    beforeEach(() => {
      mockUsers.value = [
        { id: 'driver-99', name: 'Fast Driver', role: 'driver', suspended: false },
        { id: 'shipper-88', name: 'Reliable Shipper', role: 'shipper', suspended: false },
        { id: 'suspended-77', name: 'Bad Driver', role: 'driver', suspended: true },
      ]
    })

    it('clicking Suspend opens dialog with driver-specific reasons', async () => {
      renderDashboard()

      const driverRow = screen.getByText('Fast Driver').closest('tr')!
      const suspendBtn = driverRow.querySelector('button')!
      await fireEvent.click(suspendBtn)

      expect(screen.getByText('Suspend User')).toBeInTheDocument()
      expect(screen.getByText('Repeated late deliveries')).toBeInTheDocument()
      expect(screen.getByText('Poor driving behavior reported')).toBeInTheDocument()
      expect(screen.getByText('Vehicle safety violations')).toBeInTheDocument()
    })

    it('clicking Suspend on shipper opens dialog with shipper-specific reasons', async () => {
      renderDashboard()

      const shipperRow = screen.getByText('Reliable Shipper').closest('tr')!
      const suspendBtn = shipperRow.querySelector('button')!
      await fireEvent.click(suspendBtn)

      expect(screen.getByText('Fraudulent shipment listings')).toBeInTheDocument()
      expect(screen.getByText('Non-payment for completed deliveries')).toBeInTheDocument()
    })

    it('requires a reason before confirm button is enabled and triggers suspend mutation', async () => {
      renderDashboard()

      const driverRow = screen.getByText('Fast Driver').closest('tr')!
      const suspendBtn = driverRow.querySelector('button')!
      await fireEvent.click(suspendBtn)

      const confirmBtn = screen.getByText('Confirm Suspension').closest('button')!
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

  describe('Clickable Dashboard Cards & Status/Role Filtering (All 8 Cards)', () => {
    beforeEach(() => {
      mockUsers.value = [
        { id: '1', name: 'Alice Driver', email: 'alice@driver.com', role: 'driver', verification_status: 'approved', suspended: false },
        { id: '2', name: 'Bob Shipper', email: 'bob@shipper.com', role: 'shipper', verification_status: 'pending', suspended: false },
        { id: '3', name: 'Charlie Admin', email: 'charlie@admin.com', role: 'admin', verification_status: 'approved', suspended: false },
        { id: '4', name: 'Dave Rejected', email: 'dave@driver.com', role: 'driver', verification_status: 'rejected', suspended: false },
        { id: '5', name: 'Eve Suspended', email: 'eve@shipper.com', role: 'shipper', verification_status: 'approved', suspended: true },
        { id: '6', name: 'Frank New', email: 'frank@driver.com', role: 'driver', verification_status: 'none', suspended: false },
      ]
      mockPendingCount.value = 1
      mockRejectedCount.value = 1
      mockVerifiedCount.value = 3
    })

    it('renders all 8 summary cards with their respective titles and counts', () => {
      renderDashboard()

      expect(screen.getByText('Total Users')).toBeInTheDocument()
      expect(screen.getAllByText('Drivers').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('Shippers').length).toBeGreaterThanOrEqual(1)
      expect(screen.queryByText('Admins')).not.toBeInTheDocument()
      expect(screen.getAllByText('Unverified').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('Verified').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('Pending').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('Rejected').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('Suspended').length).toBeGreaterThanOrEqual(1)
    })

    it('clicking Total Users card sets activeTab to "all" and shows all users', async () => {
      mockActiveTab.value = 'driver'
      renderDashboard()

      const totalCard = screen.getByText('Total Users').closest('.cursor-pointer')!
      await fireEvent.click(totalCard)

      expect(mockActiveTab.value).toBe('all')
    })

    it('clicking Drivers card sets activeTab to "driver" and filters table to only drivers', async () => {
      renderDashboard()

      const driversCard = screen.getAllByText('Drivers').find(el => el.closest('.cursor-pointer'))!.closest('.cursor-pointer')!
      await fireEvent.click(driversCard)

      expect(mockActiveTab.value).toBe('driver')
      expect(screen.getByText('Alice Driver')).toBeInTheDocument()
      expect(screen.getByText('Dave Rejected')).toBeInTheDocument()
      expect(screen.queryByText('Bob Shipper')).not.toBeInTheDocument()
      expect(screen.queryByText('Charlie Admin')).not.toBeInTheDocument()
    })

    it('clicking Shippers card sets activeTab to "shipper" and filters table to only shippers', async () => {
      renderDashboard()

      const shippersCard = screen.getAllByText('Shippers').find(el => el.closest('.cursor-pointer'))!.closest('.cursor-pointer')!
      await fireEvent.click(shippersCard)

      expect(mockActiveTab.value).toBe('shipper')
      expect(screen.getByText('Bob Shipper')).toBeInTheDocument()
      expect(screen.getByText('Eve Suspended')).toBeInTheDocument()
      expect(screen.queryByText('Alice Driver')).not.toBeInTheDocument()
    })

    it('clicking Unverified card sets activeTab to "unverified" and filters table to users with no verification', async () => {
      renderDashboard()

      const unverifiedCard = screen.getAllByText('Unverified').find(el => el.closest('.cursor-pointer'))!.closest('.cursor-pointer')!
      await fireEvent.click(unverifiedCard)

      expect(mockActiveTab.value).toBe('unverified')
      expect(screen.getByText('Frank New')).toBeInTheDocument()
      expect(screen.queryByText('Alice Driver')).not.toBeInTheDocument()
      expect(screen.queryByText('Bob Shipper')).not.toBeInTheDocument()
    })

    it('clicking Verified card sets activeTab to "verified" and filters table to approved users', async () => {
      renderDashboard()

      const verifiedCard = screen.getAllByText('Verified').find(el => el.closest('.cursor-pointer'))!.closest('.cursor-pointer')!
      await fireEvent.click(verifiedCard)

      expect(mockActiveTab.value).toBe('verified')
      expect(screen.getByText('Alice Driver')).toBeInTheDocument()
      expect(screen.queryByText('Charlie Admin')).not.toBeInTheDocument()
      expect(screen.getByText('Eve Suspended')).toBeInTheDocument()
      expect(screen.queryByText('Bob Shipper')).not.toBeInTheDocument()
      expect(screen.queryByText('Dave Rejected')).not.toBeInTheDocument()
    })

    it('clicking Pending card sets activeTab to "pending" and filters table to pending users', async () => {
      renderDashboard()

      const pendingCard = screen.getAllByText('Pending').find(el => el.closest('.cursor-pointer'))!.closest('.cursor-pointer')!
      await fireEvent.click(pendingCard)

      expect(mockActiveTab.value).toBe('pending')
      expect(screen.getByText('Bob Shipper')).toBeInTheDocument()
      expect(screen.queryByText('Alice Driver')).not.toBeInTheDocument()
    })

    it('clicking Rejected card sets activeTab to "rejected" and filters table to rejected users', async () => {
      renderDashboard()

      const rejectedCard = screen.getAllByText('Rejected').find(el => el.closest('.cursor-pointer'))!.closest('.cursor-pointer')!
      await fireEvent.click(rejectedCard)

      expect(mockActiveTab.value).toBe('rejected')
      expect(screen.getByText('Dave Rejected')).toBeInTheDocument()
      expect(screen.queryByText('Alice Driver')).not.toBeInTheDocument()
    })

    it('clicking Suspended card sets activeTab to "suspended" and filters table to suspended users', async () => {
      renderDashboard()

      const suspendedCard = screen.getAllByText('Suspended').find(el => el.closest('.cursor-pointer'))!.closest('.cursor-pointer')!
      await fireEvent.click(suspendedCard)

      expect(mockActiveTab.value).toBe('suspended')
      expect(screen.getByText('Eve Suspended')).toBeInTheDocument()
      expect(screen.queryByText('Alice Driver')).not.toBeInTheDocument()
    })

    it('applies active highlight border/ring styling class to whichever card is active', async () => {
      mockActiveTab.value = 'verified'
      renderDashboard()

      const verifiedCard = screen.getAllByText('Verified').find(el => el.closest('.cursor-pointer'))!.closest('.cursor-pointer')!
      expect(verifiedCard.className).toContain('ring-2')
      expect(verifiedCard.className).toContain('ring-green-600')

      mockActiveTab.value = 'rejected'
      await nextTick()
      const rejectedCard = screen.getAllByText('Rejected').find(el => el.closest('.cursor-pointer'))!.closest('.cursor-pointer')!
      expect(rejectedCard.className).toContain('ring-2')
      expect(rejectedCard.className).toContain('ring-destructive')
    })
  })

  describe('Non-Supreme Agent Card Visibility', () => {
    it('hides status-based cards (Unverified, Verified, Pending, Rejected, Suspended) for non-supreme agents', () => {
      mockAuthUser.value = {
        id: 'agent-1',
        name: 'John Agent',
        email: 'john@roadlancer.com',
        role: 'admin',
        isSupreme: false,
      }
      renderDashboard()

      expect(screen.getByText('Total Users')).toBeInTheDocument()
      expect(screen.getAllByText('Drivers').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('Shippers').length).toBeGreaterThanOrEqual(1)
      expect(screen.queryByText('Unverified')).not.toBeInTheDocument()
      expect(screen.queryByText('Verified')).not.toBeInTheDocument()
      expect(screen.queryByText('Pending')).not.toBeInTheDocument()
      expect(screen.queryByText('Rejected')).not.toBeInTheDocument()
      expect(screen.queryByText('Suspended')).not.toBeInTheDocument()
    })
  })
})
