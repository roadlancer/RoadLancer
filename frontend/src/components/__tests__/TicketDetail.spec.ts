import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/vue'
import TicketDetail from '../TicketDetail.vue'
import type { SupportTicket } from '@/composables/useSupportTickets'
import api from '@/lib/api'
import { generateText } from 'ai'

vi.mock('@/lib/api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}))

vi.mock('ai', () => ({
  generateText: vi.fn(),
}))

vi.mock('@ai-sdk/google', () => ({
  createGoogleGenerativeAI: vi.fn(() => vi.fn()),
}))

const mockRouterPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockRouterPush,
  }),
}))

describe('TicketDetail Component Unit Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

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
    replies: [
      {
        id: 'r-1',
        ticket_id: 't-202',
        sender_name: 'Sarah Jenkins',
        sender_role: 'admin',
        sender_type: 'agent',
        message: 'Could you share the exact error code displayed on screen?',
        created_at: '2026-07-10T09:00:00Z',
      },
    ],
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

  describe('4. AI Summarize Ticket & Conversation Feature', () => {
    it('renders summarize button below message with sparkles icon', () => {
      render(TicketDetail, {
        props: {
          ticket: sampleTicket,
        },
      })

      const summarizeBtn = screen.getByTestId('ticket-summarize-button')
      expect(summarizeBtn).toBeTruthy()
      expect(summarizeBtn.textContent).toContain('Summarize Ticket & Conversation')
    })

    it('calls /auth/ai/summarize and displays summary text upon clicking button', async () => {
      vi.mocked(api.post).mockResolvedValueOnce({
        data: {
          summary: '1. **Issue Overview**: Customer cannot save bank account number.\n2. **Current Status**: Agent requested exact error code.\n3. **Next Action**: Await customer reply or check backend billing logs.',
          success: true,
        },
      })

      render(TicketDetail, {
        props: {
          ticket: sampleTicket,
        },
      })

      const summarizeBtn = screen.getByTestId('ticket-summarize-button')
      await fireEvent.click(summarizeBtn)

      expect(api.post).toHaveBeenCalledWith(
        '/auth/ai/summarize',
        expect.objectContaining({
          subject: 'Cannot update bank details',
          message: 'Whenever I try to save my bank account number, it gives an error.',
          replies: sampleTicket.replies,
        }),
        expect.any(Object)
      )

      const summaryBox = await screen.findByTestId('ticket-summary-box')
      expect(summaryBox.textContent).toContain('Customer cannot save bank account number')
      expect(summaryBox.textContent).toContain('RoadLancer AI')
      expect(summarizeBtn.textContent).toContain('Regenerate Summary')
    })

    it('re-generates summary every time summarize button is clicked even when summary already exists', async () => {
      vi.mocked(api.post)
        .mockResolvedValueOnce({
          data: { summary: 'First AI summary generation output.', success: true },
        })
        .mockResolvedValueOnce({
          data: { summary: 'Second regenerated summary after new context.', success: true },
        })

      render(TicketDetail, {
        props: {
          ticket: sampleTicket,
        },
      })

      const summarizeBtn = screen.getByTestId('ticket-summarize-button')
      await fireEvent.click(summarizeBtn)

      const summaryBox = await screen.findByTestId('ticket-summary-box')
      expect(summaryBox.textContent).toContain('First AI summary generation output')

      // Click button again -> re-generates
      await fireEvent.click(summarizeBtn)
      expect(api.post).toHaveBeenCalledTimes(2)
      expect(summaryBox.textContent).toContain('Second regenerated summary after new context')
    })

    it('falls back to client-side generateText if backend API call fails', async () => {
      vi.mocked(api.post).mockRejectedValueOnce(new Error('Server Error'))
      vi.mocked(generateText).mockResolvedValueOnce({
        text: 'Client-side fallback summary generation.',
      } as any)

      render(TicketDetail, {
        props: {
          ticket: sampleTicket,
        },
      })

      const summarizeBtn = screen.getByTestId('ticket-summarize-button')
      await fireEvent.click(summarizeBtn)

      const summaryBox = await screen.findByTestId('ticket-summary-box')
      expect(summaryBox.textContent).toContain('Client-side fallback summary generation')
    })
  })
})

