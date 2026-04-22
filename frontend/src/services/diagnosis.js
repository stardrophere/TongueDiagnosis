import { apiBaseUrl, requestTimeout } from '@/config/appConfig'
import { http, createAuthHeaders, readJsonLinesStream } from '@/services/http'

/**
 * 获取诊断会话列表。
 */
export async function fetchDiagnosisSessions() {
  const { data } = await http.get('/model/session', {
    timeout: 40000,
  })

  return data
}

/**
 * 获取单个会话的历史记录。
 */
export async function fetchDiagnosisRecords(sessionId) {
  const { data } = await http.get(`/model/record/${sessionId}`, {
    timeout: 40000,
  })

  return data
}

/**
 * 发送文字追问，并通过回调把流式 token 持续交给界面层。
 */
export async function streamDiagnosisReply({ sessionId, input, onChunk }) {
  const response = await Promise.race([
    fetch(`${apiBaseUrl}/model/session/${sessionId}`, {
      method: 'POST',
      headers: createAuthHeaders({
        'Content-Type': 'application/json',
      }),
      body: JSON.stringify({ input }),
    }),
    new Promise((_, reject) => {
      setTimeout(() => reject(new Error('请求超时')), requestTimeout * 2)
    }),
  ])

  if (!response.ok) {
    throw new Error(`会话追问失败，状态码：${response.status}`)
  }

  await readJsonLinesStream(response, onChunk)
}

/**
 * 上传舌象图片并创建新会话。
 * 后端会流式返回首轮诊断内容，因此这里和追问接口统一走流式处理。
 */
export async function streamDiagnosisCreation({ file, sessionName, onChunk }) {
  const formData = new FormData()
  formData.append('file_data', file)
  formData.append('user_input', '请结合舌象特征，给出结构化诊断建议。')
  formData.append('name', sessionName)

  const response = await Promise.race([
    fetch(`${apiBaseUrl}/model/session`, {
      method: 'POST',
      headers: createAuthHeaders(),
      body: formData,
    }),
    new Promise((_, reject) => {
      setTimeout(() => reject(new Error('请求超时')), requestTimeout * 2)
    }),
  ])

  if (!response.ok) {
    throw new Error(`创建诊断会话失败，状态码：${response.status}`)
  }

  await readJsonLinesStream(response, onChunk)
}
