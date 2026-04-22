<script setup>
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import 'github-markdown-css'
import 'highlight.js/styles/github.css'
import { renderMarkdown } from '@/utils/markdown'
import { useStateStore } from '@/stores/stateStore'

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

/**
 * 每次消息变化后自动滚动到底部，让用户始终看到最新输出。
 * 使用 `nextTick` 是为了确保 DOM 已经完成渲染。
 */
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

/**
 * 播放 AI 回复时优先使用浏览器自带语音能力。
 * 如果浏览器不支持，则直接静默返回，不额外抛出脚本异常。
 */
function playMessage(message) {
  if (!stateStore.enableSpeechPlayback || message.role !== 'assistant') {
    return
  }

  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(message.content)
  utterance.lang = 'zh-CN'

  utterance.onstart = () => {
    playingMessageId.value = message.id
  }

  utterance.onend = () => {
    playingMessageId.value = ''
  }

  utterance.onerror = () => {
    playingMessageId.value = ''
  }

  window.speechSynthesis.speak(utterance)
}

/**
 * 离开页面时主动取消语音播放，避免消息在后台继续朗读。
 */
onBeforeUnmount(() => {
  if (stateStore.enableSpeechPlayback) {
    window.speechSynthesis.cancel()
  }
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
      <h3>准备开始一次新的舌诊分析</h3>
      <p>点击左侧“新建诊断”创建会话草稿，然后上传舌象图片即可生成首轮分析。</p>
    </div>

    <div v-else ref="chatContainer" class="message-list" v-loading="loading">
      <article
        v-for="message in messages"
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

          <div
            v-else
            class="markdown-body message-content"
            v-html="renderMarkdown(message.content || '')"
          />

          <div class="message-footer">
            <span v-if="message.status === 'streaming'" class="message-status">AI 正在持续生成内容...</span>
            <span v-else-if="message.status === 'error'" class="message-status error">本轮回复出现异常</span>
            <button
              v-if="message.role === 'assistant' && message.content"
              type="button"
              class="voice-button"
              @click="playMessage(message)"
            >
              {{ playingMessageId === message.id ? '朗读中...' : '朗读本条回复' }}
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
  min-height: 640px;
  padding: 24px;
}

.message-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
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
  min-height: 420px;
  text-align: center;
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.7), rgba(245, 250, 248, 0.95));
  border: 1px dashed rgba(31, 138, 112, 0.24);
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
  height: 100%;
  min-height: 520px;
  overflow-y: auto;
  padding-right: 4px;
}

.message-row {
  display: flex;
  align-items: flex-start;
  gap: 14px;
}

.message-row.is-user {
  flex-direction: row-reverse;
}

.message-avatar {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(31, 138, 112, 0.16), rgba(95, 167, 255, 0.18));
  color: var(--td-primary-700);
  font-weight: 800;
  flex-shrink: 0;
}

.message-bubble {
  width: min(100%, 820px);
  padding: 18px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(23, 52, 47, 0.08);
  box-shadow: 0 12px 24px rgba(22, 74, 62, 0.06);
}

.is-user .message-bubble {
  background: linear-gradient(135deg, rgba(31, 138, 112, 0.12), rgba(95, 167, 255, 0.08));
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
}

.image-message {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.image-message img {
  width: min(100%, 280px);
  border-radius: 18px;
  border: 1px solid rgba(23, 52, 47, 0.08);
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
    min-height: auto;
    padding: 18px;
  }

  .message-header {
    flex-direction: column;
  }

  .message-bubble {
    width: 100%;
  }

  .message-footer,
  .message-meta {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
