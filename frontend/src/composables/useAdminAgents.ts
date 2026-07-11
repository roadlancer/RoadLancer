import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import api from '@/lib/api'

export interface AgentRecord {
  id: string
  name: string
  email: string
  role: string
  suspended: boolean
  isSupreme: boolean
  created_at: string | null
}

export function useAdminAgents() {
  const queryClient = useQueryClient()

  const query = useQuery({
    queryKey: ['admin-agents'],
    queryFn: async () => {
      const { data } = await api.get('/admin/users', { params: { role: 'admin' } })
      return data as AgentRecord[]
    },
  })

  const deactivateAgent = useMutation({
    mutationFn: async (userId: string) => {
      const { data } = await api.post(`/admin/users/${userId}/deactivate-agent`)
      return data as AgentRecord
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-agents'] })
      queryClient.invalidateQueries({ queryKey: ['support-agents'] })
      queryClient.invalidateQueries({ queryKey: ['admin-support-tickets'] })
    },
  })

  const activateAgent = useMutation({
    mutationFn: async (userId: string) => {
      const { data } = await api.post(`/admin/users/${userId}/activate-agent`)
      return data as AgentRecord
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-agents'] })
      queryClient.invalidateQueries({ queryKey: ['support-agents'] })
    },
  })

  const createAgent = useMutation({
    mutationFn: async (payload: { name: string; email: string; password: string }) => {
      const { data } = await api.post('/admin/users/create-agent', payload)
      return data as AgentRecord
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-agents'] })
      queryClient.invalidateQueries({ queryKey: ['support-agents'] })
    },
  })

  return {
    ...query,
    data: query.data,
    deactivateAgent,
    activateAgent,
    createAgent,
  }
}
