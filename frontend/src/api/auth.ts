import api from './index'
import type { UserInfo } from '@/stores/auth'

export interface LoginResponse {
  access_token: string
  token_type: string
  user: UserInfo
}

export async function login(username: string, password: string) {
  const { data } = await api.post<LoginResponse>('/users/login', { username, password })
  return data
}

export async function register(username: string, email: string, password: string) {
  const { data } = await api.post<UserInfo>('/users/register', { username, email, password })
  return data
}

export async function getUserProfile() {
  const { data } = await api.get<UserInfo>('/users/me')
  return data
}

export async function updateProfile(fields: { username?: string; bio?: string; avatar_url?: string }) {
  const { data } = await api.patch<UserInfo>('/users/me', fields)
  return data
}
