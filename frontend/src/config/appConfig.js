const fallbackServerUrl = 'http://10.252.130.135:5000'

/**
 * 基础后端地址
 */
export const serverUrl = (import.meta.env.VITE_SERVER_URL || fallbackServerUrl).replace(/\/$/, '')

/**
 * 接口请求基地址
 */
export const apiBaseUrl = import.meta.env.DEV ? '/api' : `${serverUrl}/api`

/**
 * 接口请求超时时间
 */
export const requestTimeout = Number(import.meta.env.VITE_REQUEST_TIMEOUT || 20000)

/**
 * 上传图片的体积限制，单位 MB。
 */
export const uploadMaxSizeMb = Number(import.meta.env.VITE_UPLOAD_MAX_SIZE_MB || 10)

/**
 * 全局应用配置
 */
export const appMeta = {
  name: 'AI 舌诊助手',
  shortName: '舌诊助手',
  description: '基于 AI 与中医舌象分析的智能诊断辅助平台',
  defaultSessionPrefix: '舌诊记录',
}
