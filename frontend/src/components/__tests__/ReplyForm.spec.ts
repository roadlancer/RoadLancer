import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/vue'
import ReplyForm from '../ReplyForm.vue'
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

describe('ReplyForm Component Unit Tests', () => {
  describe('1. ReplyForm Structure & Rendering', () => {
    it('renders the core title, sender notice, and form inputs correctly', () => {
      render(ReplyForm, {
        props: {
          senderEmail: 'john@driver.com',
          defaultSenderName: 'Sarah Jenkins (Support Lead)',
          showStatusNotice: true,
        },
      })

      // Title & Notice
      expect(screen.getByText('Post a Reply to Sender')).toBeTruthy()
      expect(screen.getByText(/Your response will be recorded in the thread and sent directly to john@driver\.com/)).toBeTruthy()

      // Inputs
      const senderInput = screen.getByTestId('reply-sender-name-input') as HTMLInputElement
      const messageTextarea = screen.getByTestId('reply-message-textarea') as HTMLTextAreaElement
      const polishButton = screen.getByTestId('reply-polish-button') as HTMLButtonElement
      const submitButton = screen.getByTestId('reply-submit-button') as HTMLButtonElement

      expect(senderInput).toBeTruthy()
      expect(messageTextarea).toBeTruthy()
      expect(polishButton).toBeTruthy()
      expect(polishButton.textContent).toContain('Polish')
      expect(submitButton).toBeTruthy()
      expect(submitButton.textContent).toContain('Send Reply')
    })

    it('renders the auto-update status notice when showStatusNotice is true and omits when false', async () => {
      const { rerender } = render(ReplyForm, {
        props: {
          showStatusNotice: true,
        },
      })

      expect(screen.queryByText(/Auto-updates ticket status from Open to In Progress/)).toBeTruthy()

      await rerender({ showStatusNotice: false })
      expect(screen.queryByText(/Auto-updates ticket status from Open to In Progress/)).toBeNull()
    })
  })

  describe('2. Auto-Population & Watcher Behavior', () => {
    it('auto-populates the senderName input with defaultSenderName on mount', () => {
      render(ReplyForm, {
        props: {
          defaultSenderName: 'Rahul Sharma (Dispatch Specialist)',
        },
      })

      const senderInput = screen.getByTestId('reply-sender-name-input') as HTMLInputElement
      expect(senderInput.value).toBe('Rahul Sharma (Dispatch Specialist)')
    })

    it('falls back to Sarah Jenkins (Support Lead) when defaultSenderName is not provided or empty', () => {
      render(ReplyForm, {
        props: {
          defaultSenderName: '',
        },
      })

      const senderInput = screen.getByTestId('reply-sender-name-input') as HTMLInputElement
      expect(senderInput.value).toBe('Sarah Jenkins (Support Lead)')
    })

    it('updates senderName dynamically when defaultSenderName prop changes if untouched by user', async () => {
      const { rerender } = render(ReplyForm, {
        props: {
          defaultSenderName: 'Sarah Jenkins (Support Lead)',
        },
      })

      const senderInput = screen.getByTestId('reply-sender-name-input') as HTMLInputElement
      expect(senderInput.value).toBe('Sarah Jenkins (Support Lead)')

      await rerender({ defaultSenderName: 'Pooja Nair (KYC Verification Team)' })
      expect(senderInput.value).toBe('Pooja Nair (KYC Verification Team)')
    })
  })

  describe('3. Button Disabled State & Validation', () => {
    it('disables the submit button when message text is empty or only whitespace', async () => {
      render(ReplyForm, {
        props: {
          defaultSenderName: 'Sarah Jenkins',
        },
      })

      const submitButton = screen.getByTestId('reply-submit-button') as HTMLButtonElement
      const polishButton = screen.getByTestId('reply-polish-button') as HTMLButtonElement
      const messageTextarea = screen.getByTestId('reply-message-textarea') as HTMLTextAreaElement

      // Initially empty -> disabled
      expect(submitButton.disabled).toBe(true)
      expect(polishButton.disabled).toBe(true)

      // Type whitespace -> still disabled
      await fireEvent.update(messageTextarea, '   \n  \t  ')
      expect(submitButton.disabled).toBe(true)
      expect(polishButton.disabled).toBe(true)
    })

    it('enables the submit button once message has non-whitespace characters', async () => {
      render(ReplyForm, {
        props: {
          defaultSenderName: 'Sarah Jenkins',
        },
      })

      const submitButton = screen.getByTestId('reply-submit-button') as HTMLButtonElement
      const messageTextarea = screen.getByTestId('reply-message-textarea') as HTMLTextAreaElement

      await fireEvent.update(messageTextarea, 'We have verified your documents.')
      expect(submitButton.disabled).toBe(false)
    })

    it('disables the submit button and shows loading text when isSubmitting is true', async () => {
      const { rerender } = render(ReplyForm, {
        props: {
          isSubmitting: false,
        },
      })

      const submitButton = screen.getByTestId('reply-submit-button') as HTMLButtonElement
      const messageTextarea = screen.getByTestId('reply-message-textarea') as HTMLTextAreaElement

      await fireEvent.update(messageTextarea, 'Hello team!')
      expect(submitButton.disabled).toBe(false)
      expect(submitButton.textContent).toContain('Send Reply')

      await rerender({ isSubmitting: true })
      expect(submitButton.disabled).toBe(true)
      expect(submitButton.textContent).toContain('Sending Reply...')
    })
  })

  describe('4. Form Submission & Event Emits', () => {
    it('emits submit event with trimmed message and senderName upon form submission', async () => {
      const { emitted } = render(ReplyForm, {
        props: {
          defaultSenderName: 'Sarah Jenkins (Support Lead)',
        },
      })

      const senderInput = screen.getByTestId('reply-sender-name-input') as HTMLInputElement
      const messageTextarea = screen.getByTestId('reply-message-textarea') as HTMLTextAreaElement
      const submitButton = screen.getByTestId('reply-submit-button') as HTMLButtonElement

      await fireEvent.update(senderInput, '   Vikram Mehta (Billing)   ')
      await fireEvent.update(messageTextarea, '   Your refund has been processed.   ')

      await fireEvent.click(submitButton)

      const submitEmitted = emitted()['submit']
      expect(submitEmitted).toBeTruthy()
      expect(submitEmitted.length).toBe(1)
      expect(submitEmitted[0]).toEqual([
        {
          message: 'Your refund has been processed.',
          senderName: 'Vikram Mehta (Billing)',
        },
      ])
    })

    it('clears the textarea message after a successful submit emission', async () => {
      render(ReplyForm, {
        props: {
          defaultSenderName: 'Sarah Jenkins',
        },
      })

      const messageTextarea = screen.getByTestId('reply-message-textarea') as HTMLTextAreaElement
      const submitButton = screen.getByTestId('reply-submit-button') as HTMLButtonElement

      await fireEvent.update(messageTextarea, 'Thank you for contacting us!')
      expect(messageTextarea.value).toBe('Thank you for contacting us!')

      await fireEvent.click(submitButton)
      expect(messageTextarea.value).toBe('')
    })
  })

  describe('5. AI Polishing, Greeting & Signature Features', () => {
    beforeEach(() => {
      vi.clearAllMocks()
    })

    it('sends draft, senderName, and extracted customerName to the backend polish API and updates message with polished text', async () => {
      vi.mocked(api.post).mockResolvedValueOnce({
        data: {
          polished: 'Hi John,\n\nWe have investigated your ticket and issued the refund.\n\nBest regards,\nSarah Jenkins\nRoadLancer Support Team\nhttps://roadlancer.com',
          success: true,
        },
      })

      render(ReplyForm, {
        props: {
          senderEmail: 'john.smith@example.com',
          customerName: 'John Smith',
          defaultSenderName: 'Sarah Jenkins (Support Lead)',
        },
      })

      const messageTextarea = screen.getByTestId('reply-message-textarea') as HTMLTextAreaElement
      const polishButton = screen.getByTestId('reply-polish-button') as HTMLButtonElement

      await fireEvent.update(messageTextarea, 'we looked into your ticket and refunded.')
      await fireEvent.click(polishButton)

      expect(api.post).toHaveBeenCalledWith(
        '/auth/ai/polish',
        expect.objectContaining({
          draft: 'we looked into your ticket and refunded.',
          senderName: 'Sarah Jenkins (Support Lead)',
          customerName: 'John',
          senderEmail: 'john.smith@example.com',
        }),
        expect.any(Object)
      )

      expect(messageTextarea.value).toContain('Hi John,')
      expect(messageTextarea.value).toContain('https://roadlancer.com')
    })

    it('automatically prepends customer first name greeting and appends agent signature with domain name during client-side fallback if missing from model output', async () => {
      vi.mocked(api.post).mockRejectedValueOnce(new Error('Network Error'))
      vi.mocked(generateText).mockResolvedValueOnce({
        text: 'We have resolved the billing discrepancy.',
      } as any)

      render(ReplyForm, {
        props: {
          senderEmail: 'mike@logistics.com',
          customerName: 'Mike Ross',
          defaultSenderName: 'Sarah Jenkins',
        },
      })

      const messageTextarea = screen.getByTestId('reply-message-textarea') as HTMLTextAreaElement
      const polishButton = screen.getByTestId('reply-polish-button') as HTMLButtonElement

      await fireEvent.update(messageTextarea, 'resolved the billing issue')
      await fireEvent.click(polishButton)

      // Post-processing should prepend "Hi Mike,\n\n" and append signature
      expect(messageTextarea.value).toContain('Hi Mike,')
      expect(messageTextarea.value).toContain('Best regards,\nSarah Jenkins\nRoadLancer Support Team\nhttps://roadlancer.com')
    })

    it('displays rate limit / quota exceeded error banner when polishing fails with 429 quota error', async () => {
      vi.mocked(api.post).mockRejectedValueOnce(new Error('Network Error'))
      vi.mocked(generateText).mockRejectedValueOnce({
        status: 429,
        message: 'Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 5',
      })

      render(ReplyForm, {
        props: {
          defaultSenderName: 'Sarah Jenkins',
        },
      })

      const messageTextarea = screen.getByTestId('reply-message-textarea') as HTMLTextAreaElement
      const polishButton = screen.getByTestId('reply-polish-button') as HTMLButtonElement

      await fireEvent.update(messageTextarea, 'checking status')
      await fireEvent.click(polishButton)

      const errorAlert = await screen.findByTestId('reply-ai-status-banner')
      expect(errorAlert.textContent).toContain('Model Rate Limit / Quota Exceeded')
      expect(errorAlert.textContent).toContain('You have exceeded the free tier rate limit on Gemini 2.5 Flash')
    })

    it('displays API key incorrect banner when backend returns API_KEY_INVALID error', async () => {
      vi.mocked(api.post).mockRejectedValueOnce({
        response: {
          status: 401,
          data: { code: 'API_KEY_INVALID' },
        },
      })

      render(ReplyForm, {
        props: {
          defaultSenderName: 'Sarah Jenkins',
        },
      })

      const messageTextarea = screen.getByTestId('reply-message-textarea') as HTMLTextAreaElement
      const polishButton = screen.getByTestId('reply-polish-button') as HTMLButtonElement

      await fireEvent.update(messageTextarea, 'checking status')
      await fireEvent.click(polishButton)

      const errorAlert = await screen.findByTestId('reply-ai-status-banner')
      expect(errorAlert.textContent).toContain('Gemini API Key Incorrect / Unauthorized')
    })
  })
})

