<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import 'github-markdown-css'
import 'highlight.js/styles/github.css'
import { renderMarkdown } from '@/utils/markdown'
import { useStateStore } from '@/stores/stateStore'
import { getSpeakableAssistantContent, splitAssistantMessageContent } from '@/utils/chatMessage'

const props = defineProps({
  messages: {
    type: Array,
    default: () => [],
  },
  mode: {
    type: String,
    default: 'empty',
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const chatContainer = ref(null)
const stateStore = useStateStore()
const playingMessageId = ref('')
const expandedThinking = ref({})
let currentUtterance = null

const decoratedMessages = computed(() =>
  props.messages.map((message) => ({
    ...message,
    assistantParts:
      message.role === 'assistant' ? splitAssistantMessageContent(message.content || '') : null,
  })),
)

async function scrollToBottom() {
  await nextTick()

  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

watch(
  () => props.messages,
  () => {
    scrollToBottom()
  },
  { deep: true, immediate: true },
)

function stopPlayback() {
  if (!stateStore.enableSpeechPlayback) {
    return
  }

  window.speechSynthesis.cancel()
  playingMessageId.value = ''
  currentUtterance = null
}

function playMessage(message) {
  if (!stateStore.enableSpeechPlayback || message.role !== 'assistant') {
    return
  }

  if (playingMessageId.value === message.id) {
    stopPlayback()
    return
  }

  const content = getSpeakableAssistantContent(message.content || '')
  if (!content) {
    return
  }

  stopPlayback()

  const utterance = new SpeechSynthesisUtterance(content)
  utterance.lang = 'zh-CN'
  currentUtterance = utterance

  utterance.onstart = () => {
    playingMessageId.value = message.id
  }

  utterance.onend = () => {
    if (currentUtterance === utterance) {
      playingMessageId.value = ''
      currentUtterance = null
    }
  }

  utterance.onerror = () => {
    if (currentUtterance === utterance) {
      playingMessageId.value = ''
      currentUtterance = null
    }
  }

  window.speechSynthesis.speak(utterance)
}

function isThinkingExpanded(message) {
  if (Object.prototype.hasOwnProperty.call(expandedThinking.value, message.id)) {
    return expandedThinking.value[message.id]
  }

  return message.status === 'streaming'
}

function handleThinkingToggle(messageId, event) {
  expandedThinking.value = {
    ...expandedThinking.value,
    [messageId]: event.target.open,
  }
}

onBeforeUnmount(() => {
  stopPlayback()
})
</script>

<template>
  <section class="message-shell page-card">
    <header class="message-header">
      <div>
        <p class="panel-label">诊断对话区</p>
        <h2>舌诊分析与追问记录</h2>
      </div>
      <span v-if="mode === 'chat'" class="status-chip">已进入诊断会话</span>
      <span v-else-if="mode === 'draft'" class="status-chip">等待上传图片</span>
      <span v-else class="status-chip">请先新建诊断</span>
    </header>

    <div v-if="mode === 'empty'" class="empty-panel">
      <div>
        <h3>准备开始一次新的舌诊分析</h3>
        <p>点击左侧“新建诊断”创建会话草稿，然后上传舌象图片即可生成首轮分析。</p>
      </div>
    </div>

    <div v-else ref="chatContainer" class="message-list" v-loading="loading">
      <article
        v-for="message in decoratedMessages"
        :key="message.id"
        class="message-row"
        :class="message.role === 'user' ? 'is-user' : 'is-assistant'"
      >
        <div class="message-avatar">
          {{ message.role === 'user' ? stateStore.userAvatarSeed.slice(0, 1) : stateStore.aiAvatarSeed.slice(0, 1) }}
        </div>

        <div class="message-bubble">
          <div class="message-meta">
            <strong>{{ message.role === 'user' ? '您' : 'AI 舌诊助手' }}</strong>
            <span>{{ message.createdAt }}</span>
          </div>

          <div v-if="message.type === 'image'" class="image-message">
            <img :src="message.previewUrl" alt="舌象图片预览" />
            <p>{{ message.content }}</p>
          </div>

          <template v-else-if="message.role === 'assistant' && message.assistantParts?.hasThink">
            <details
              class="think-panel"
              :open="isThinkingExpanded(message)"
              @toggle="handleThinkingToggle(message.id, $event)"
            >
              <summary>
                {{ message.assistantParts.thinkClosed ? '查看 AI 思考过程' : 'AI 思考中...' }}
              </summary>
              <div
                class="markdown-body think-content"
                v-html="renderMarkdown(message.assistantParts.thinkContent || '')"
              />
            </details>

            <div
              v-if="message.assistantParts.answerContent"
              class="markdown-body message-content"
              v-html="renderMarkdown(message.assistantParts.answerContent)"
            />
          </template>

          <div
            v-else
            class="markdown-body message-content"
            v-html="renderMarkdown(message.content || '')"
          />

          <div class="message-footer">
            <span v-if="message.status === 'streaming'" class="message-status">AI 正在持续生成内容...</span>
            <span v-else-if="message.status === 'error'" class="message-status error">本轮回复出现异常</span>
            <button
              v-if="message.role === 'assistant' && getSpeakableAssistantContent(message.content || '')"
              type="button"
              class="voice-button"
              @click="playMessage(message)"
            >
              {{ playingMessageId === message.id ? '停止朗读' : '朗读本条回复' }}
            </button>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.message-shell {
  display: flex;
  flex-direction: column;
  min-height: 0;
  height: 100%;
  padding: 24px;
  overflow: hidden;
}

.message-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
  flex-shrink: 0;
}

.panel-label {
  margin: 0 0 8px;
  color: var(--td-primary-600);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
}

.message-header h2 {
  margin: 0;
  color: var(--td-text-main);
}

.empty-panel {
  display: grid;
  place-items: center;
  min-height: 0;
  flex: 1;
  text-align: center;
  border-radius: 24px;
  background: var(--td-panel-bg);
  border: 1px dashed var(--td-border-strong);
}

.empty-panel h3 {
  margin: 0 0 10px;
  color: var(--td-text-main);
}

.empty-panel p {
  margin: 0;
  max-width: 460px;
  color: var(--td-text-secondary);
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 4px;
}

.message-row {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.message-row.is-user {
  flex-direction: row-reverse;
}

.message-avatar {
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--td-primary-soft), rgba(95, 167, 255, 0.18));
  color: var(--td-primary-700);
  font-size: 16px;
  font-weight: 800;
  flex-shrink: 0;
}

.message-bubble {
  max-width: 86%;
  padding: 20px;
  border-radius: 24px;
  background: var(--td-panel-strong);
  border: 1px solid var(--td-border-color);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.04);
}

.is-user .message-bubble {
  background: linear-gradient(135deg, var(--td-primary-soft), rgba(95, 167, 255, 0.08));
}

.message-meta,
.message-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.message-meta {
  margin-bottom: 12px;
}

.message-meta strong {
  color: var(--td-text-main);
}

.message-meta span,
.message-status {
  color: var(--td-text-muted);
  font-size: 13px;
}

.message-status.error {
  color: var(--td-danger-500);
}

.message-content {
  padding: 0;
  border-radius: 12px;
  background: transparent !important;
  color: inherit !important;
}

.markdown-body {
  background-color: transparent !important;
  color: inherit !important;
  font-family: inherit !important;
}

.markdown-body pre, .markdown-body code {
  border-radius: 8px;
}

.think-panel {
  margin-bottom: 14px;
  border: 1px solid rgba(95, 167, 255, 0.18);
  border-radius: 18px;
  background: rgba(95, 167, 255, 0.06);
  overflow: hidden;
}

.think-panel summary {
  cursor: pointer;
  list-style: none;
  padding: 12px 14px;
  font-size: 13px;
  font-weight: 600;
  color: var(--td-primary-700);
}

.think-panel summary::-webkit-details-marker {
  display: none;
}

.think-content {
  padding: 0 14px 14px;
}

.image-message {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.image-message img {
  width: min(100%, 280px);
  border-radius: 18px;
  border: 1px solid var(--td-border-color);
}

.image-message p {
  margin: 0;
  color: var(--td-text-secondary);
}

.voice-button {
  border: 0;
  background: transparent;
  color: var(--td-primary-700);
  cursor: pointer;
  font-size: 13px;
}

@media (max-width: 768px) {
  .message-shell {
    height: auto;
    min-height: 420px;
    padding: 18px;
  }

  .message-header {
    flex-direction: column;
  }

  .message-bubble {
    width: 100%;
    max-width: 100%;
  }

  .message-footer,
  .message-meta {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
