import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/vue'
import ReplyThread, { type ReplyItem } from '../ReplyThread.vue'

describe('ReplyThread Component Unit Tests', () => {
  const sampleReplies: ReplyItem[] = [
    {
      id: 'reply-1',
      sender_name: 'Sarah Jenkins (Support Lead)',
      sender_type: 'agent',
      sender_role: 'admin',
      message: 'Hello Priya, we have reset your bank verification status. Please try saving now.',
      created_at: '2026-07-10T09:00:00Z',
    },
    {
      id: 'reply-2',
      sender_name: 'Priya Sharma',
      sender_type: 'user',
      sender_role: 'transporter',
      message: 'Thank you! I just updated my IFSC code and it worked.',
      created_at: '2026-07-10T09:15:00Z',
    },
  ]

  describe('1. Empty State & No Replies', () => {
    it('displays 0 Replies badge and empty state message when replies prop is empty', () => {
      render(ReplyThread, {
        props: {
          replies: [],
        },
      })

      expect(screen.getByText('Discussion & Reply Thread')).toBeTruthy()
      expect(screen.getByTestId('reply-count-badge').textContent).toContain('0 Replies')
      expect(screen.getByTestId('no-replies-empty-state')).toBeTruthy()
      expect(screen.getByText('No Replies Yet')).toBeTruthy()
      expect(screen.queryByTestId('replies-list')).toBeNull()
    })

    it('displays empty state when replies prop is undefined/not provided', () => {
      render(ReplyThread)

      expect(screen.getByTestId('reply-count-badge').textContent).toContain('0 Replies')
      expect(screen.getByTestId('no-replies-empty-state')).toBeTruthy()
    })
  })

  describe('2. Rendering Reply Items', () => {
    it('renders singular 1 Reply badge when exactly one reply exists', () => {
      render(ReplyThread, {
        props: {
          replies: [sampleReplies[0]],
        },
      })

      expect(screen.getByTestId('reply-count-badge').textContent).toContain('1 Reply')
      expect(screen.queryByTestId('no-replies-empty-state')).toBeNull()
    })

    it('renders plural count badge and displays all reply messages and sender names', () => {
      render(ReplyThread, {
        props: {
          replies: sampleReplies,
        },
      })

      expect(screen.getByTestId('reply-count-badge').textContent).toContain('2 Replies')
      expect(screen.getByTestId('replies-list')).toBeTruthy()

      // Reply 1 (Agent)
      expect(screen.getByTestId('reply-sender-reply-1').textContent).toContain('Sarah Jenkins (Support Lead)')
      expect(screen.getByTestId('reply-message-reply-1').textContent).toContain('Hello Priya, we have reset your bank verification status')
      expect(screen.getByTestId('reply-badge-reply-1').textContent).toContain('Agent')

      // Reply 2 (Customer)
      expect(screen.getByTestId('reply-sender-reply-2').textContent).toContain('Priya Sharma')
      expect(screen.getByTestId('reply-message-reply-2').textContent).toContain('Thank you! I just updated my IFSC code and it worked.')
      expect(screen.getByTestId('reply-badge-reply-2').textContent).toContain('Customer')
    })
  })

  describe('3. Role-Based Styling Differentiation', () => {
    it('applies distinct background and border styles for agents vs customers', () => {
      render(ReplyThread, {
        props: {
          replies: sampleReplies,
        },
      })

      const agentItem = screen.getByTestId('reply-item-reply-1')
      const customerItem = screen.getByTestId('reply-item-reply-2')

      expect(agentItem.className).toContain('bg-primary/5')
      expect(agentItem.className).toContain('border-primary/25')

      expect(customerItem.className).toContain('bg-card')
      expect(customerItem.className).toContain('border-border/80')
    })
  })
})
