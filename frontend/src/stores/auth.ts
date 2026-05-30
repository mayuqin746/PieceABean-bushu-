import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as authApi from '@/api/auth'

export interface UserInfo {
  id: number
  username: string
  email: string
  avatar_url: string | null
  bio: string | null
  created_at: string
  patterns_count?: number
  favorites_count?: number
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  function setToken(t: string) {
    token.value = t
    localStorage.setItem('token', t)
  }

  function setUser(u: UserInfo) {
    user.value = u
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  async function fetchProfile() {
    if (!token.value) return
    try {
      const data = await authApi.getUserProfile()
      user.value = data
    } catch {
      logout()
    }
  }

  async function updateProfile(fields: { username?: string; bio?: string; avatar_url?: string }) {
    const data = await authApi.updateProfile(fields)
    user.value = { ...user.value!, ...data }
    return data
  }

  return { token, user, isLoggedIn, setToken, setUser, logout, fetchProfile, updateProfile }
})
