import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/vue'
import UpdateTicket from '../UpdateTicket.vue'

describe('UpdateTicket Component Unit Tests', () => {
  const mockSupportAgents = [
    { id: 'agent-1', name: 'Sarah Jenkins (Support Lead)' },
    { id: 'agent-2', name: 'Rahul Sharma (Dispatch)' },
  ]

  describe('1. Rendering & Initial Values', () => {
    it('renders card title, selects, and textarea with passed props correctly', () => {
      render(UpdateTicket, {
        props: {
          status: 'in_progress',
          priority: 'high',
          category: 'billing',
          agentId: 'agent-2',
          agentName: 'Rahul Sharma (Dispatch)',
          notes: 'Checking bank transaction log...',
          isSaving: false,
          supportAgents: mockSupportAgents,
        },
      })

      expect(screen.getByText('Ticket Resolution Desk')).toBeTruthy()
      expect(screen.getByTestId('assigned-agent-notice').textContent).toContain('Assigned to Rahul Sharma')

      const statusSelect = screen.getByTestId('status-select') as HTMLSelectElement
      expect(statusSelect.value).toBe('in_progress')

      const prioritySelect = screen.getByTestId('priority-select') as HTMLSelectElement
      expect(prioritySelect.value).toBe('high')

      const categorySelect = screen.getByTestId('category-select') as HTMLSelectElement
      expect(categorySelect.value).toBe('billing')

      const notesTextarea = screen.getByTestId('notes-textarea') as HTMLTextAreaElement
      expect(notesTextarea.value).toBe('Checking bank transaction log...')

      const saveBtn = screen.getByTestId('save-resolution-btn') as HTMLButtonElement
      expect(saveBtn.disabled).toBe(false)
      expect(saveBtn.textContent).toContain('Save Ticket Resolution')
    })
  })

  describe('2. Button State & Loading Indicator', () => {
    it('disables save button and displays saving text when isSaving is true', () => {
      render(UpdateTicket, {
        props: {
          isSaving: true,
        },
      })

      const saveBtn = screen.getByTestId('save-resolution-btn') as HTMLButtonElement
      expect(saveBtn.disabled).toBe(true)
      expect(saveBtn.textContent).toContain('Saving Resolution...')
    })
  })

  describe('3. Interactions & Event Emits', () => {
    it('emits update:status when status dropdown is changed', async () => {
      const { emitted } = render(UpdateTicket, {
        props: { status: 'open' },
      })

      const statusSelect = screen.getByTestId('status-select')
      await fireEvent.update(statusSelect, 'resolved')

      const statusEmits = emitted()['update:status']
      expect(statusEmits).toBeTruthy()
      expect(statusEmits[0]).toEqual(['resolved'])
    })

    it('emits update:priority when priority dropdown is changed', async () => {
      const { emitted } = render(UpdateTicket, {
        props: { priority: 'normal' },
      })

      const prioritySelect = screen.getByTestId('priority-select')
      await fireEvent.update(prioritySelect, 'urgent')

      const priorityEmits = emitted()['update:priority']
      expect(priorityEmits).toBeTruthy()
      expect(priorityEmits[0]).toEqual(['urgent'])
    })

    it('emits update:category when category dropdown is changed', async () => {
      const { emitted } = render(UpdateTicket, {
        props: { category: 'general' },
      })

      const categorySelect = screen.getByTestId('category-select')
      await fireEvent.update(categorySelect, 'shipments')

      const categoryEmits = emitted()['update:category']
      expect(categoryEmits).toBeTruthy()
      expect(categoryEmits[0]).toEqual(['shipments'])
    })

    it('emits update:notes when text is typed in notes textarea', async () => {
      const { emitted } = render(UpdateTicket, {
        props: { notes: '' },
      })

      const textarea = screen.getByTestId('notes-textarea')
      await fireEvent.update(textarea, 'Verified driver license validity.')

      const notesEmits = emitted()['update:notes']
      expect(notesEmits).toBeTruthy()
      expect(notesEmits[0]).toEqual(['Verified driver license validity.'])
    })

    it('emits agent-selected with id and agent name when agent select is changed', async () => {
      const { emitted } = render(UpdateTicket, {
        props: {
          supportAgents: mockSupportAgents,
          agentId: 'agent-1',
        },
      })

      const agentSelect = screen.getByTestId('agent-select')
      await fireEvent.update(agentSelect, 'agent-2')

      const agentEmits = emitted()['agent-selected']
      expect(agentEmits).toBeTruthy()
      expect(agentEmits[0]).toEqual([{ id: 'agent-2', name: 'Rahul Sharma (Dispatch)' }])
    })

    it('emits assign-to-me when Assign to Me button is clicked', async () => {
      const { emitted } = render(UpdateTicket)

      const assignBtn = screen.getByTestId('assign-to-me-btn')
      await fireEvent.click(assignBtn)

      expect(emitted()['assign-to-me']).toBeTruthy()
    })

    it('emits save when save button is clicked', async () => {
      const { emitted } = render(UpdateTicket)

      const saveBtn = screen.getByTestId('save-resolution-btn')
      await fireEvent.click(saveBtn)

      expect(emitted()['save']).toBeTruthy()
    })
  })
})
