import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    tokenExpiresAt: Number(localStorage.getItem('tokenExpiresAt')) || 0,
  }),
  getters: {
    isTokenExpired: (state) => {
      if (!state.token) return true
      return Date.now() >= state.tokenExpiresAt
    },
  },
  actions: {
    setToken(token: string, expiresInSeconds: number) {
      this.token = token
      this.tokenExpiresAt = Date.now() + expiresInSeconds * 1000

      localStorage.setItem('token', token)
      localStorage.setItem('tokenExpiresAt', this.tokenExpiresAt.toString())
    },
    clearToken() {
      this.token = ''
      this.tokenExpiresAt = 0
      localStorage.removeItem('token')
      localStorage.removeItem('tokenExpiresAt')
    },
    checkTokenExpired(): boolean {
      return !this.token || Date.now() >= this.tokenExpiresAt
    }
  }
})
