import { render } from '@testing-library/vue'
import AdminDashboard from '../AdminDashboard.vue'

export function renderDashboard(options: Record<string, any> = {}) {
  return render(AdminDashboard, {
    ...options,
    global: {
      ...options.global,
      stubs: {
        RouterLink: {
          template: '<a><slot /></a>',
        },
        ...(options.global?.stubs || {}),
      },
    },
  })
}
