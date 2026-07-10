import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/vue'
import TicketDetail from '../TicketDetail.vue'
import type { SupportTicket } from '@/composables/useSupportTickets'

const mockRouterPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockRouterPush,
  }),
}))

describe('TicketDetail Component Unit Tests', () => {
  const sampleTicket: SupportTicket = {
    id: 't-202',
    ticket_number: 'SUP-202',
    sender_name: 'Priya Sharma',
    sender_email: 'priya@transporter.in',
    subject: 'Cannot update bank details',
    message: 'Whenever I try to save my bank account number, it gives an error.',
    category: 'billing',
    status: 'open',
    priority: 'high',
    source: 'web',
    admin_notes: '',
    created_at: '2026-07-10T08:30:00Z',
    updated_at: '2026-07-10T08:30:00Z',
    user: {
      id: 'user-88',
      name: 'Priya Sharma',
      email: 'priya@transporter.in',
      role: 'transporter',
      phone: '+91 9876543210',
    },
  }

  describe('1. Subject Card Rendering', () => {
    it('renders ticket created date, source badge, subject, and message content accurately', () => {
      render(TicketDetail, {
        props: {
          ticket: sampleTicket,
        },
      })

      expect(screen.getByTestId('ticket-subject-title').textContent).toContain('Cannot update bank details')
      expect(screen.getByTestId('ticket-message-content').textContent).toContain('Whenever I try to save my bank account number')
      expect(screen.getByTestId('ticket-source-badge').textContent).toContain('web')
      expect(screen.getByTestId('ticket-created-date')).toBeTruthy()
    })
  })

  describe('2. Sender & Linked Account Card Rendering', () => {
    it('displays sender email and sender name correctly when provided', () => {
      render(TicketDetail, {
        props: {
          ticket: sampleTicket,
        },
      })

      expect(screen.getByTestId('ticket-sender-email').textContent).toContain('priya@transporter.in')
      expect(screen.getByTestId('ticket-sender-name').textContent).toContain('Priya Sharma')
    })

    it('displays fallback Not Provided when sender_name is empty', () => {
      const ticketWithoutName: SupportTicket = {
        ...sampleTicket,
        sender_name: '',
      }

      render(TicketDetail, {
        props: {
          ticket: ticketWithoutName,
        },
      })

      expect(screen.getByTestId('ticket-sender-name').textContent).toContain('Not Provided')
    })

    it('shows linked user profile information when ticket.user is present', () => {
      render(TicketDetail, {
        props: {
          ticket: sampleTicket,
        },
      })

      expect(screen.getByTestId('ticket-linked-role-badge').textContent).toContain('Linked transporter Profile')
      expect(screen.getByTestId('ticket-linked-user-name').textContent).toContain('Priya Sharma')
      expect(screen.getByTestId('ticket-linked-user-email').textContent).toContain('priya@transporter.in')
      expect(screen.getByTestId('ticket-linked-user-phone').textContent).toContain('+91 9876543210')
      expect(screen.getByTestId('ticket-inspect-button')).toBeTruthy()
    })

    it('displays fallback message when no linked user profile matched', () => {
      const ticketNoUser: SupportTicket = {
        ...sampleTicket,
        user: null,
      }

      render(TicketDetail, {
        props: {
          ticket: ticketNoUser,
        },
      })

      expect(screen.getByTestId('ticket-no-linked-user').textContent).toContain('No registered RoadLancer account matched')
    })

    it('hides the entire sender card when showSenderCard is false', () => {
      render(TicketDetail, {
        props: {
          ticket: sampleTicket,
          showSenderCard: false,
        },
      })

      expect(screen.queryByTestId('ticket-detail-sender-card')).toBeNull()
    })
  })

  describe('3. Interactions & Emits', () => {
    it('emits inspect-account event and navigates when Inspect Account button is clicked', async () => {
      const { emitted } = render(TicketDetail, {
        props: {
          ticket: sampleTicket,
        },
      })

      const inspectButton = screen.getByTestId('ticket-inspect-button')
      await fireEvent.click(inspectButton)

      const inspectEmitted = emitted()['inspect-account']
      expect(inspectEmitted).toBeTruthy()
      expect(inspectEmitted[0]).toEqual(['user-88'])
      expect(mockRouterPush).toHaveBeenCalledWith('/admin')
    })
  })
})
