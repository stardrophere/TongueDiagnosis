import { defineStore } from 'pinia'
import { appMeta, uploadMaxSizeMb } from '@/config/appConfig'

/**
 * 全局 UI 状态管理
 */
export const useStateStore = defineStore('appState', {
  state: () => ({
    appName: appMeta.name,
    appDescription: appMeta.description,
    defaultSessionPrefix: appMeta.defaultSessionPrefix,
    uploadMaxSizeMb,
    userAvatarSeed: 'USER',
    aiAvatarSeed: 'AI',
    enableSpeechInput: typeof window !== 'undefined' && 'webkitSpeechRecognition' in window,
    enableSpeechPlayback: typeof window !== 'undefined' && 'speechSynthesis' in window,
    isDarkMode: false,
  }),

  actions: {
    /**
     * 切换黑白模式并持久化
     */
    toggleDarkMode() {
      this.isDarkMode = !this.isDarkMode
      if (this.isDarkMode) {
        document.documentElement.classList.add('dark')
        localStorage.setItem('theme', 'dark')
      } else {
        document.documentElement.classList.remove('dark')
        localStorage.setItem('theme', 'light')
      }
    },

    /**
     * 初始化黑白模式
     */
    initTheme() {
      const savedTheme = localStorage.getItem('theme')
      const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      this.isDarkMode = savedTheme === 'dark' || (!savedTheme && prefersDark)
      
      if (this.isDarkMode) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    },

    /**
     * 设置用户头像种子
     */
    setUserAvatarSeed(value) {
      this.userAvatarSeed = value || 'USER'
    },

    /**
     * 自定义 AI 头像占位文案。
     */
    setAiAvatarSeed(value) {
      this.aiAvatarSeed = value || 'AI'
    },
  },
})
