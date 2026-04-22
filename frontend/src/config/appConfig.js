const fallbackServerUrl = 'http://10.252.133.135:5000'

/**
 * 统一处理后端地址，避免业务组件中继续散落硬编码地址。
 * 生产环境默认直接请求完整后端地址，开发环境通过 Vite 代理走 `/api`。
 */
export const serverUrl = (import.meta.env.VITE_SERVER_URL || fallbackServerUrl).replace(/\/$/, '')

/**
 * 浏览器侧请求基地址。
 * 开发环境走代理，生产/打包环境直接拼接服务端地址，减少跨域与部署差异。
 */
export const apiBaseUrl = import.meta.env.DEV ? '/api' : `${serverUrl}/api`

/**
 * 统一请求超时时间，方便后续在服务层复用。
 */
export const requestTimeout = Number(import.meta.env.VITE_REQUEST_TIMEOUT || 20000)

/**
 * 上传图片的体积限制，单位 MB。
 */
export const uploadMaxSizeMb = Number(import.meta.env.VITE_UPLOAD_MAX_SIZE_MB || 10)

/**
 * 项目级展示文案与默认值集中在这里，避免页面里出现“魔法字符串”。
 */
export const appMeta = {
  name: 'AI 舌诊助手',
  shortName: '舌诊助手',
  description: '基于 AI 与中医舌象分析的智能诊断辅助平台',
  defaultSessionPrefix: '舌诊记录',
}
