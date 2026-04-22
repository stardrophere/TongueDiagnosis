import { apiBaseUrl, requestTimeout } from '@/config/appConfig'
import { http, createAuthHeaders, readJsonLinesStream } from '@/services/http'

export async function fetchDiagnosisSessions() {
  const { data } = await http.get('/model/session', {
    timeout: 40000,
  })

  return data
}

export async function fetchDiagnosisRecords(sessionId) {
  const { data } = await http.get(`/model/record/${sessionId}`, {
    timeout: 40000,
  })

  return data
}

export async function deleteDiagnosisSession(sessionId) {
  const { data } = await http.delete(`/model/session/${sessionId}`, {
    timeout: 40000,
  })

  if (data?.code !== 0) {
    throw new Error(data?.message || '删除会话失败')
  }

  return data
}

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
