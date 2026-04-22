import { defineStore } from 'pinia'
import { appMeta, uploadMaxSizeMb } from '@/config/appConfig'

/**
 * 全局界面与展示偏好状态。
 * 旧版 `stateStore` 承担了过多业务职责，这里将它收敛为“全局 UI 配置”用途。
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
  }),

  actions: {
    /**
     * 自定义用户头像占位文案。
     * 当前项目未接入真实头像资源时，可以通过种子文案生成首字母头像。
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
