import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/vue'
import { ref } from 'vue'
import TicketsTable from '../TicketsTable.vue'
import {
  parseAssignedAgent,
  formatAssignedAgentNotes,
  type SupportTicket,
} from '@/composables/useSupportTickets'

// --- Mock Router ---
const mockRouterPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockRouterPush,
  }),
}))

// --- Mock useSupportAgents ---
vi.mock('@/composables/useSupportTickets', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/composables/useSupportTickets')>()
  return {
    ...actual,
    useSupportAgents: () => ref([
      { id: '', name: 'Unassigned (No Agent)' },
      { id: 'admin-lead', name: 'Sarah Jenkins (Support Lead)' },
      { id: 'admin-dispatch', name: 'Rahul Sharma (Dispatch Specialist)' },
      { id: 'admin-kyc', name: 'Pooja Nair (KYC Verification Team)' },
      { id: 'admin-billing', name: 'Vikram Mehta (Billing & Accounts)' },
    ]),
  }
})

describe('TicketsTable & Agent Assignment Unit Tests', () => {
  const sampleTickets: SupportTicket[] = [
    {
      id: 't-101',
      ticket_number: 'SUP-101',
      sender_name: 'John Driver',
      sender_email: 'john@driver.com',
      subject: 'Issue with KYC Upload',
      message: 'My license verification is stuck on pending.',
      category: 'verification',
      status: 'open',
      priority: 'high',
      source: 'email',
      admin_notes: 'User tried uploading twice.',
      created_at: '2026-07-09T10:00:00Z',
      updated_at: '2026-07-09T10:00:00Z',
      user: {
        id: 'user-1',
        name: 'John Driver',
        email: 'john@driver.com',
        role: 'driver',
        phone: '+1 555-0101',
      },
    },
    {
      id: 't-102',
      ticket_number: 'SUP-102',
      sender_name: 'Sara Shipper',
      sender_email: 'sara@shipper.com',
      subject: 'Payment discrepancy on shipment #44',
      message: 'The AI estimated price did not match the invoice.',
      category: 'billing',
      status: 'in_progress',
      priority: 'urgent',
      source: 'web',
      admin_notes: '[ASSIGNED_TO:admin-billing|Vikram Mehta (Billing & Accounts)] Investigating payment logs.',
      created_at: '2026-07-08T14:30:00Z',
      updated_at: '2026-07-09T09:15:00Z',
      user: {
        id: 'user-2',
        name: 'Sara Shipper',
        email: 'sara@shipper.com',
        role: 'shipper',
        phone: null,
      },
    },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('1. Table Layout & Structure Validation', () => {
    it('renders all core column headers while omitting Sender & Account', () => {
      render(TicketsTable, {
        props: {
          tickets: sampleTickets,
          sorting: [],
        },
      })

      // Verify core columns exist
      expect(screen.getByText('Ticket #')).toBeInTheDocument()
      expect(screen.getByText('Subject')).toBeInTheDocument()
      expect(screen.getByText('Source')).toBeInTheDocument()
      expect(screen.getByText('Priority')).toBeInTheDocument()
      expect(screen.getByText('Status')).toBeInTheDocument()
      expect(screen.getByText('Assigned Agent')).toBeInTheDocument()
      expect(screen.getByText('Actions')).toBeInTheDocument()

      // Verify "Sender & Account" header is NOT rendered
      expect(screen.queryByText('Sender & Account')).not.toBeInTheDocument()
    })

    it('renders ticket rows without "Sender & Account" email or phone data in the grid', () => {
      render(TicketsTable, {
        props: {
          tickets: sampleTickets,
          sorting: [],
        },
      })

      // Ticket number and subject should be clearly rendered
      expect(screen.getByText('SUP-101')).toBeInTheDocument()
      expect(screen.getByText('Issue with KYC Upload')).toBeInTheDocument()
      expect(screen.getByText('SUP-102')).toBeInTheDocument()
      expect(screen.getByText('Payment discrepancy on shipment #44')).toBeInTheDocument()

      // Sender email / phone from the old column should NOT be rendered in table cells
      expect(screen.queryByText('john@driver.com')).not.toBeInTheDocument()
      expect(screen.queryByText('+1 555-0101')).not.toBeInTheDocument()
    })

    it('does NOT render the "Assign to Me" button in row actions', () => {
      render(TicketsTable, {
        props: {
          tickets: sampleTickets,
          sorting: [],
        },
      })

      expect(screen.queryByText('Assign to Me')).not.toBeInTheDocument()
    })
  })

  describe('2. Interactive Inline Agent Assignment', () => {
    it('renders an inline select element populated with active support agents', () => {
      render(TicketsTable, {
        props: {
          tickets: sampleTickets,
          sorting: [],
        },
      })

      const selects = screen.getAllByRole('combobox')
      expect(selects.length).toBeGreaterThanOrEqual(2)

      // First ticket has no assigned agent in admin_notes, so default value should be empty string
      expect((selects[0] as HTMLSelectElement).value).toBe('')
      // Second ticket is assigned to 'admin-billing'
      expect((selects[1] as HTMLSelectElement).value).toBe('admin-billing')
    })

    it('emits "assign" event with correct payload and formatted notes when an agent is selected', async () => {
      const { emitted } = render(TicketsTable, {
        props: {
          tickets: sampleTickets,
          sorting: [],
        },
      })

      const selects = screen.getAllByRole('combobox')
      const firstSelect = selects[0]

      // Select Sarah Jenkins (Support Lead)
      await fireEvent.change(firstSelect, { target: { value: 'admin-lead' } })

      expect(emitted().assign).toBeTruthy()
      expect(emitted().assign.length).toBe(1)

      const payload = emitted().assign[0][0] as any
      expect(payload.ticket.id).toBe('t-101')
      expect(payload.agentId).toBe('admin-lead')
      expect(payload.agentName).toBe('Sarah Jenkins (Support Lead)')
      expect(payload.newNotes).toContain('[ASSIGNED_TO:admin-lead|Sarah Jenkins (Support Lead)]')
      expect(payload.newNotes).toContain('User tried uploading twice.')
    })

    it('emits "assign" event with null agentId when unassigned option is selected', async () => {
      const { emitted } = render(TicketsTable, {
        props: {
          tickets: sampleTickets,
          sorting: [],
        },
      })

      const selects = screen.getAllByRole('combobox')
      const secondSelect = selects[1] // Currently assigned to Vikram Mehta

      await fireEvent.change(secondSelect, { target: { value: '' } })

      expect(emitted().assign).toBeTruthy()
      const payload = emitted().assign[0][0] as any
      expect(payload.ticket.id).toBe('t-102')
      expect(payload.agentId).toBeNull()
      expect(payload.newNotes).not.toContain('[ASSIGNED_TO')
      expect(payload.newNotes).toContain('Investigating payment logs.')
    })
  })

  describe('3. Row Actions & Navigation', () => {
    it('emits "resolve" event when clicking the Resolve button on unresolved ticket', async () => {
      const { emitted } = render(TicketsTable, {
        props: {
          tickets: sampleTickets,
          sorting: [],
        },
      })

      const resolveBtns = screen.getAllByRole('button', { name: /^resolve$/i })
      await fireEvent.click(resolveBtns[0])

      expect(emitted().resolve).toBeTruthy()
      expect((emitted().resolve[0][0] as SupportTicket).id).toBe('t-101')
    })

    it('navigates to /admin/support/:id when clicking Inspect button or Subject cell', async () => {
      render(TicketsTable, {
        props: {
          tickets: sampleTickets,
          sorting: [],
        },
      })

      const inspectBtns = screen.getAllByRole('button', { name: /^inspect$/i })
      await fireEvent.click(inspectBtns[0])
      expect(mockRouterPush).toHaveBeenCalledWith('/admin/support/t-101')

      const subjectCell = screen.getByText('Payment discrepancy on shipment #44')
      await fireEvent.click(subjectCell)
      expect(mockRouterPush).toHaveBeenCalledWith('/admin/support/t-102')
    })
  })

  describe('4. Agent Metadata Helper Functions (useSupportTickets utilities)', () => {
    it('parseAssignedAgent cleanly parses assigned metadata and strips tags from clean notes', () => {
      const raw = '[ASSIGNED_TO:admin-dispatch|Rahul Sharma (Dispatch Specialist)] Customer requested urgent status.'
      const parsed = parseAssignedAgent(raw)

      expect(parsed.agentId).toBe('admin-dispatch')
      expect(parsed.agentName).toBe('Rahul Sharma (Dispatch Specialist)')
      expect(parsed.cleanNotes).toBe('Customer requested urgent status.')
    })

    it('formatAssignedAgentNotes formats new notes correctly and replaces old metadata tag if present', () => {
      const oldNotes = '[ASSIGNED_TO:admin-kyc|Pooja Nair (KYC Team)] Checking uploaded documents.'
      const updated = formatAssignedAgentNotes(
        'admin-lead',
        'Sarah Jenkins (Support Lead)',
        parseAssignedAgent(oldNotes).cleanNotes
      )

      expect(updated).toBe('[ASSIGNED_TO:admin-lead|Sarah Jenkins (Support Lead)]\nChecking uploaded documents.')
    })
  })
})
