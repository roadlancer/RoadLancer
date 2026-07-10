import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/vue'
import ReplyForm from '../ReplyForm.vue'

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
      const submitButton = screen.getByTestId('reply-submit-button') as HTMLButtonElement

      expect(senderInput).toBeTruthy()
      expect(messageTextarea).toBeTruthy()
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
      const messageTextarea = screen.getByTestId('reply-message-textarea') as HTMLTextAreaElement

      // Initially empty -> disabled
      expect(submitButton.disabled).toBe(true)

      // Type whitespace -> still disabled
      await fireEvent.update(messageTextarea, '   \n  \t  ')
      expect(submitButton.disabled).toBe(true)
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
})
