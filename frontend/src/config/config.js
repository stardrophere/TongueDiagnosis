import { serverUrl } from '@/config/appConfig'

/**
 * 兼容旧代码的配置导出。
 * 新代码请优先使用 `appConfig.js`，这里仅保留向后兼容能力。
 */
export const settings = {
  ServerUrl: serverUrl,
}

export default settings
