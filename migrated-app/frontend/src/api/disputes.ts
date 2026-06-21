import apiClient from '@/lib/api-client'

export interface Dispute {
  id: string
  owner_id: string
  name: string
  status: 'setting_up' | 'bidding' | 'finalizing' | 'finalized' | 'rejected'
  resolution_method: 'bids' | 'ratings'
  bounds_percentage: number
  rating_weight: number
  block_id?: string
  created_at: string
  updated_at: string
  agents: Agent[]
  goods: Good[]
}

export interface Agent {
  id: string
  email: string
  name: string
  share_of_entitlement: number
  validated: string
}

export interface Good {
  id: string
  name: string
  estimated_value: number
  indivisible: boolean
}

export interface CreateDisputeRequest {
  name: string
  resolution_method: 'bids' | 'ratings'
  bounds_percentage?: number
  rating_weight?: number
}

export const disputesApi = {
  list: async (): Promise<Dispute[]> => {
    const response = await apiClient.get('/disputes/')
    return response.data
  },

  get: async (id: string): Promise<Dispute> => {
    const response = await apiClient.get(`/disputes/${id}`)
    return response.data
  },

  create: async (data: CreateDisputeRequest): Promise<Dispute> => {
    const response = await apiClient.post('/disputes/', data)
    return response.data
  },

  update: async (id: string, data: Partial<CreateDisputeRequest>): Promise<Dispute> => {
    const response = await apiClient.put(`/disputes/${id}`, data)
    return response.data
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/disputes/${id}`)
  },

  solve: async (id: string): Promise<any> => {
    const response = await apiClient.post(`/disputes/${id}/solve`)
    return response.data
  },

  finalize: async (id: string): Promise<void> => {
    await apiClient.post(`/disputes/${id}/finalize`)
  },

  reject: async (id: string): Promise<void> => {
    await apiClient.post(`/disputes/${id}/reject`)
  },
}
