import { computed, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  deleteDiagnosisSession,
  fetchDiagnosisRecords,
  fetchDiagnosisSessions,
  streamDiagnosisCreation,
  streamDiagnosisReply,
} from '@/services/diagnosis'
import { useStateStore } from '@/stores/stateStore'
import { parseStoredImageMessage } from '@/utils/chatMessage'
import { createSessionName, formatDateTime } from '@/utils/formatters'

function createMessage({
  id = `${Date.now()}-${Math.random().toString(16).slice(2)}`,
  role,
  content = '',
  type = 'text',
  createdAt = Date.now(),
  status = 'done',
  previewUrl = '',
}) {
  return {
    id,
    role,
    content,
    type,
    status,
    previewUrl,
    createdAt: formatDateTime(createdAt),
  }
}

function normalizeSessions(rawList = []) {
  return rawList.map((item) => ({
    id: item.session_id,
    name: item.name || `诊断记录 ${item.session_id}`,
  }))
}

function normalizeRecords(rawRecords = []) {
  return rawRecords.map((item) => {
    const imagePayload = parseStoredImageMessage(item.content || '')
    if (imagePayload) {
      return createMessage({
        role: 'user',
        type: 'image',
        content: imagePayload.text || '已上传舌象图片，请开始分析。',
        previewUrl: imagePayload.preview_url,
        createdAt: item.create_at || Date.now(),
      })
    }

    return createMessage({
      role: Number(item.role) === 1 ? 'user' : 'assistant',
      content: item.content || '',
      createdAt: item.create_at || Date.now(),
    })
  })
}

export function useDiagnosisWorkspace() {
  const stateStore = useStateStore()

  const sessions = ref([])
  const activeSessionId = ref(null)
  const activeMessages = ref([])
  const activeSessionName = ref('')
  const draftSessionName = ref(createSessionName(stateStore.defaultSessionPrefix))
  const hasDraft = ref(false)
  const loadingSessions = ref(false)
  const loadingMessages = ref(false)
  const uploadingImage = ref(false)
  const streamingReply = ref(false)
  const deletingSessionId = ref(null)
  const sessionCache = ref({})

  const hasActiveSession = computed(() => Boolean(activeSessionId.value))
  const isBusy = computed(
    () =>
      loadingMessages.value ||
      uploadingImage.value ||
      streamingReply.value ||
      Boolean(deletingSessionId.value),
  )
  const canUploadImage = computed(() => hasDraft.value && !uploadingImage.value && !streamingReply.value)
  const canSendMessage = computed(() => hasActiveSession.value && !streamingReply.value)
  const workspaceMode = computed(() => {
    if (hasActiveSession.value) {
      return 'chat'
    }

    if (hasDraft.value) {
      return 'draft'
    }

    return 'empty'
  })

  function createGuideMessage(sessionName = draftSessionName.value) {
    return createMessage({
      role: 'assistant',
      content: [
        `# ${sessionName}`,
        '',
        '请先上传一张清晰的舌象图片，我会基于图像分析给出第一轮智能解读。',
        '',
        '## 拍摄建议',
        '1. 尽量在自然光下拍摄，避免滤镜和强烈阴影。',
        '2. 镜头尽量正对舌面，保持画面清晰、不模糊。',
        '3. 拍摄前避免刚进食、饮有色饮料或口红影响舌象判断。',
        '',
        '## 使用提醒',
        '本系统结果仅用于健康参考，不能替代专业医生面诊与正式诊断。',
      ].join('\n'),
    })
  }

  function syncCurrentMessagesToCache() {
    if (!activeSessionId.value) {
      return
    }

    sessionCache.value = {
      ...sessionCache.value,
      [activeSessionId.value]: [...activeMessages.value],
    }
  }

  function appendUserMessage(content, options = {}) {
    activeMessages.value = [
      ...activeMessages.value,
      createMessage({
        role: 'user',
        content,
        type: options.type || 'text',
        previewUrl: options.previewUrl || '',
      }),
    ]
  }

  function appendStreamingAssistantMessage() {
    const message = createMessage({
      role: 'assistant',
      content: '',
      status: 'streaming',
    })

    activeMessages.value = [...activeMessages.value, message]
    return message.id
  }

  function patchAssistantMessage(messageId, patch) {
    activeMessages.value = activeMessages.value.map((item) => {
      if (item.id !== messageId) {
        return item
      }

      return {
        ...item,
        ...patch,
      }
    })
  }

  function clearDraft() {
    hasDraft.value = false
    activeSessionId.value = null
    activeSessionName.value = ''
    activeMessages.value = []
  }

  async function loadSessions() {
    loadingSessions.value = true

    try {
      const result = await fetchDiagnosisSessions()
      sessions.value = normalizeSessions(result.data || [])

      if (!activeSessionId.value && sessions.value.length && !hasDraft.value) {
        await openSession(sessions.value[0].id)
      }
    } catch (error) {
      console.error(error)
      ElMessage.error('获取诊断记录失败，请稍后重试。')
    } finally {
      loadingSessions.value = false
    }
  }

  function createDraft(name = createSessionName(stateStore.defaultSessionPrefix)) {
    activeSessionId.value = null
    activeSessionName.value = ''
    draftSessionName.value = name
    hasDraft.value = true
    activeMessages.value = [createGuideMessage(name)]
  }

  function updateDraftName(name) {
    draftSessionName.value = name || createSessionName(stateStore.defaultSessionPrefix)

    if (hasDraft.value && !hasActiveSession.value) {
      activeMessages.value = [createGuideMessage(draftSessionName.value)]
    }
  }

  async function openSession(sessionId) {
    const target = sessions.value.find((item) => item.id === sessionId)
    if (!target) {
      return
    }

    hasDraft.value = false
    activeSessionId.value = sessionId
    activeSessionName.value = target.name

    if (sessionCache.value[sessionId]) {
      activeMessages.value = sessionCache.value[sessionId]
      return
    }

    loadingMessages.value = true

    try {
      const result = await fetchDiagnosisRecords(sessionId)
      const records = normalizeRecords(result.data?.records || [])
      activeMessages.value = records
      sessionCache.value = {
        ...sessionCache.value,
        [sessionId]: records,
      }
    } catch (error) {
      console.error(error)
      ElMessage.error('读取会话详情失败，请稍后重试。')
    } finally {
      loadingMessages.value = false
    }
  }

  async function submitImage(file, previewUrl) {
    if (!hasDraft.value) {
      createDraft()
    }

    if (!file) {
      ElMessage.warning('请先选择要上传的舌象图片。')
      return
    }

    uploadingImage.value = true
    appendUserMessage('已上传舌象图片，请开始分析。', {
      type: 'image',
      previewUrl,
    })
    const assistantMessageId = appendStreamingAssistantMessage()

    try {
      await streamDiagnosisCreation({
        file,
        sessionName: draftSessionName.value,
        onChunk: (chunk) => {
          const currentText =
            activeMessages.value.find((item) => item.id === assistantMessageId)?.content || ''

          if (chunk.session_id && !activeSessionId.value) {
            activeSessionId.value = chunk.session_id
            activeSessionName.value = draftSessionName.value
            hasDraft.value = false

            if (!sessions.value.some((item) => item.id === chunk.session_id)) {
              sessions.value = [{ id: chunk.session_id, name: draftSessionName.value }, ...sessions.value]
            }
          }

          if (chunk.token) {
            patchAssistantMessage(assistantMessageId, {
              content: currentText + chunk.token,
              status: 'streaming',
            })
            syncCurrentMessagesToCache()
          }
        },
      })

      patchAssistantMessage(assistantMessageId, {
        status: 'done',
        content:
          activeMessages.value.find((item) => item.id === assistantMessageId)?.content ||
          '已完成诊断分析，但未返回详细文本。',
      })

      syncCurrentMessagesToCache()
      ElMessage.success('首轮舌诊分析已完成。')
    } catch (error) {
      console.error(error)
      patchAssistantMessage(assistantMessageId, {
        status: 'error',
        content: '图像分析失败，请确认网络与图片内容后重试。',
      })
      ElMessage.error(error.message || '创建诊断失败，请稍后重试。')
    } finally {
      uploadingImage.value = false
    }
  }

  async function submitMessage(text) {
    const content = String(text || '').trim()
    if (!content) {
      return
    }

    if (!activeSessionId.value) {
      ElMessage.warning('请先上传舌象图片，创建诊断会话后再继续追问。')
      return
    }

    streamingReply.value = true
    appendUserMessage(content)
    const assistantMessageId = appendStreamingAssistantMessage()
    syncCurrentMessagesToCache()

    try {
      await streamDiagnosisReply({
        sessionId: activeSessionId.value,
        input: content,
        onChunk: (chunk) => {
          const currentText =
            activeMessages.value.find((item) => item.id === assistantMessageId)?.content || ''

          if (chunk.token) {
            patchAssistantMessage(assistantMessageId, {
              content: currentText + chunk.token,
              status: 'streaming',
            })
            syncCurrentMessagesToCache()
          }
        },
      })

      patchAssistantMessage(assistantMessageId, {
        status: 'done',
        content:
          activeMessages.value.find((item) => item.id === assistantMessageId)?.content ||
          '本轮已处理完成，但未收到更多文本。',
      })
      syncCurrentMessagesToCache()
    } catch (error) {
      console.error(error)
      patchAssistantMessage(assistantMessageId, {
        status: 'error',
        content: '追问失败，请稍后重试。',
      })
      syncCurrentMessagesToCache()
      ElMessage.error(error.message || '发送追问失败，请稍后重试。')
    } finally {
      streamingReply.value = false
    }
  }

  async function deleteSession(sessionId) {
    const target = sessions.value.find((item) => item.id === sessionId)
    if (!target || deletingSessionId.value) {
      return
    }

    try {
      await ElMessageBox.confirm(
        `删除“${target.name}”后，聊天记录和上传图片都会被移除。确认继续吗？`,
        '删除会话',
        {
          confirmButtonText: '删除',
          cancelButtonText: '取消',
          type: 'warning',
        },
      )
    } catch {
      return
    }

    deletingSessionId.value = sessionId

    try {
      await deleteDiagnosisSession(sessionId)

      sessions.value = sessions.value.filter((item) => item.id !== sessionId)
      const nextCache = { ...sessionCache.value }
      delete nextCache[sessionId]
      sessionCache.value = nextCache

      if (activeSessionId.value === sessionId) {
        if (sessions.value.length > 0) {
          await openSession(sessions.value[0].id)
        } else {
          clearDraft()
        }
      }

      ElMessage.success('会话已删除。')
    } catch (error) {
      console.error(error)
      ElMessage.error(error.message || '删除会话失败，请稍后重试。')
    } finally {
      deletingSessionId.value = null
    }
  }

  return {
    sessions,
    activeSessionId,
    activeSessionName,
    draftSessionName,
    activeMessages,
    hasDraft,
    loadingSessions,
    loadingMessages,
    uploadingImage,
    streamingReply,
    deletingSessionId,
    workspaceMode,
    isBusy,
    canUploadImage,
    canSendMessage,
    loadSessions,
    createDraft,
    clearDraft,
    updateDraftName,
    openSession,
    submitImage,
    submitMessage,
    deleteSession,
  }
}
