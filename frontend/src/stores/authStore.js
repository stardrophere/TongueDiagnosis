import { defineStore } from 'pinia'
import { fetchUserProfile, loginByPassword, registerByPassword } from '@/services/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    profile: null,
    profileLoaded: false,
    loadingProfile: false,
  }),

  getters: {
    /**
     * 用统一 getter 暴露登录状态，避免组件自己判断 token 是否为空。
     */
    isAuthenticated(state) {
      return Boolean(state.token)
    },
  },

  actions: {
    /**
     * 登录成功后统一写入 token。
     * 这样无论是表单页、刷新恢复还是未来第三方登录，都能复用同一套状态入口。
     */
    setToken(token) {
      this.token = token || ''

      if (this.token) {
        localStorage.setItem('token', this.token)
      } else {
        localStorage.removeItem('token')
      }
    },

    /**
     * 清理登录态并重置用户资料。
     */
    clearAuth() {
      this.setToken('')
      this.profile = null
      this.profileLoaded = false
    },

    /**
     * 统一封装密码登录流程。
     */
    async login(payload) {
      const result = await loginByPassword(payload)

      if (result.code === 0 && result.data?.token) {
        this.setToken(result.data.token)
      }

      return result
    },

    /**
     * 统一封装注册流程，页面只负责展示结果。
     */
    async register(payload) {
      return registerByPassword(payload)
    },

    /**
     * 获取当前用户资料。
     * force 为 true 时会强制重新请求，适合登录成功后立即刷新头像/昵称。
     */
    async ensureProfile(force = false) {
      if (!this.token) {
        this.profile = null
        this.profileLoaded = true
        return null
      }

      if (this.profileLoaded && !force) {
        return this.profile
      }

      this.loadingProfile = true

      try {
        const result = await fetchUserProfile()

        if (result.code === 0) {
          this.profile = result.data || {}
          this.profileLoaded = true
          return this.profile
        }

        throw new Error(result.message || '获取用户信息失败')
      } catch (error) {
        this.clearAuth()
        throw error
      } finally {
        this.loadingProfile = false
      }
    },

    /**
     * 主动退出登录。
     */
    logout() {
      this.clearAuth()
    },
  },
})
