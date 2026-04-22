import axios from 'axios'
import { ElMessage } from 'element-plus'
import { apiBaseUrl, requestTimeout } from '@/config/appConfig'

/**
 * 统一 axios 实例。
 * 所有普通 HTTP 请求都应走这里，便于统一注入 token、处理超时和 401。
 */
export const http = axios.create({
  baseURL: apiBaseUrl,
  timeout: requestTimeout,
})

/**
 * 请求前自动附带 token，避免每个调用方手写 Authorization 头。
 */
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')

  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

/**
 * 响应拦截器只负责兜底处理全局错误。
 * 业务层如果有更细粒度提示，可以继续在调用处追加 try/catch。
 */
http.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status
    const message = error?.message || ''

    if (status === 401) {
      localStorage.removeItem('token')
      ElMessage.error('登录状态已失效，请重新登录。')
    } else if (message.includes('timeout')) {
      ElMessage.error('请求超时，请稍后重试。')
    }

    return Promise.reject(error)
  },
)

/**
 * 为流式请求生成统一请求头。
 */
export function createAuthHeaders(extraHeaders = {}) {
  const token = localStorage.getItem('token')
  return {
    ...extraHeaders,
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

/**
 * 统一解析 JSON Lines 流。
 * 后端当前返回的是按行分隔的 JSON 字符串，因此这里做增量缓冲与逐行解析。
 */
export async function readJsonLinesStream(response, onMessage) {
  if (!response.body) {
    throw new Error('流式响应缺少 body。')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { value, done } = await reader.read()

    if (done) {
      break
    }

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    lines.forEach((line) => {
      const trimmed = line.trim()
      if (!trimmed) {
        return
      }

      try {
        onMessage(JSON.parse(trimmed))
      } catch (error) {
        console.warn('流式 JSON 解析失败，已忽略当前片段。', error)
      }
    })
  }

  if (buffer.trim()) {
    onMessage(JSON.parse(buffer.trim()))
  }
}
