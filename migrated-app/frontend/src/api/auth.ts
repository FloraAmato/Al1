import apiClient from '@/lib/api-client'

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
  name?: string
  surname?: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface User {
  id: string
  email: string
  username: string
  name?: string
  surname?: string
  is_active: boolean
  is_email_verified: boolean
}

export const authApi = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post('/auth/login', data)
    return response.data
  },

  register: async (data: RegisterRequest): Promise<User> => {
    const response = await apiClient.post('/auth/register', data)
    return response.data
  },

  refreshToken: async (refreshToken: string): Promise<AuthResponse> => {
    const response = await apiClient.post('/auth/refresh', { refresh_token: refreshToken })
    return response.data
  },
}
