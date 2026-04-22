<script setup>
import { computed, ref } from 'vue'
import { Message as ElMessage } from '@/utils/message'
import UploadPicture from '@/components/UploadPicture.vue'
import Steps from '@/components/Steps.vue'
import { useStateStore } from '@/stores/stateStore'

const props = defineProps({
  mode: {
    type: String,
    default: 'empty',
  },
  canSend: {
    type: Boolean,
    default: false,
  },
  canUpload: {
    type: Boolean,
    default: false,
  },
  uploading: {
    type: Boolean,
    default: false,
  },
  streaming: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['submit-message', 'submit-image', 'request-draft'])
const stateStore = useStateStore()

const inputValue = ref('')
const selectedImage = ref(null)
const uploadProgressRef = ref(null)
const isListening = ref(false)
let recognition = null

const canStartImageAnalysis = computed(() => props.canUpload && Boolean(selectedImage.value) && !props.uploading)

/**
 * 暂存选中的图片
 */
function handleImageSelected(payload) {
  selectedImage.value = payload
}

/**
 * 提交图片并开始分析
 */
function submitImage() {
  if (!selectedImage.value) {
    ElMessage.warning('请先选择一张清晰的舌象图片。')
    return
  }

  emit('submit-image', selectedImage.value)
}

/**
 * 提交追问消息
 */
function submitMessage() {
  const content = inputValue.value.trim()

  if (!content) {
    return
  }

  emit('submit-message', content)
  inputValue.value = ''
}

function handleEnter(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    submitMessage()
  }
}

/**
 * 初始化语音识别 (Web Speech API)
 */
function ensureRecognition() {
  if (!stateStore.enableSpeechInput || recognition) {
    return
  }

  if (!('webkitSpeechRecognition' in window)) {
    return
  }

  recognition = new webkitSpeechRecognition()
  recognition.continuous = false
  recognition.interimResults = false
  recognition.lang = 'zh-CN'

  recognition.onstart = () => {
    isListening.value = true
  }

  recognition.onresult = (event) => {
    inputValue.value = `${inputValue.value}${event.results[0][0].transcript}`
  }

  recognition.onerror = () => {
    isListening.value = false
    ElMessage.error('语音识别失败，请检查浏览器权限后重试。')
  }

  recognition.onend = () => {
    isListening.value = false
  }
}

function toggleSpeechInput() {
  ensureRecognition()

  if (!recognition) {
    ElMessage.warning('当前浏览器暂不支持语音输入。')
    return
  }

  if (isListening.value) {
    recognition.stop()
  } else {
    recognition.start()
  }
}

/**
 * 暴露方法给父组件控制进度与清理
 */
defineExpose({
  startProgress() {
    uploadProgressRef.value?.start?.()
  },
  stopProgress() {
    uploadProgressRef.value?.stop?.()
  },
  clearSelectedImage() {
    selectedImage.value = null
  },
})
</script>

<template>
  <section class="composer-shell page-card">
    <template v-if="mode === 'empty'">
      <div class="empty-actions">
        <p>还没有创建诊断草稿，点击按钮开始一次新的舌诊分析。</p>
        <button type="button" class="btn-primary btn-large" @click="emit('request-draft')">
          新建诊断并上传图片
        </button>
      </div>
    </template>

    <template v-else-if="mode === 'draft'">
      <div class="upload-zone">
        <div class="upload-copy">
          <h3>上传本次舌象图片</h3>
          <p>请选择一张清晰、无遮挡的舌象图片。选中图片后，点击“开始分析”即可创建正式会话。</p>
        </div>

        <UploadPicture @selected="handleImageSelected" />

        <div v-if="selectedImage" class="selected-preview glass-card">
          <img :src="selectedImage.previewUrl" alt="当前选择的图片预览" />
          <div>
            <strong>{{ selectedImage.name }}</strong>
            <p>已完成本地预览，确认无误后即可开始分析。</p>
          </div>
        </div>

        <button type="button" class="btn-primary btn-large" :disabled="!canStartImageAnalysis" @click="submitImage">
          开始分析图片
        </button>

        <Steps v-if="uploading" ref="uploadProgressRef" />
      </div>
    </template>

    <template v-else>
      <div class="chat-composer">
        <textarea
          v-model="inputValue"
          rows="3"
          placeholder="请输入要继续追问的问题，例如：这种舌象通常说明什么体质？后续应如何调理？"
          @keydown="handleEnter"
          class="custom-textarea"
        ></textarea>

        <div class="composer-actions">
          <div class="action-hint">
            <span class="text-muted">支持继续追问症状、体质、作息建议与饮食方向。</span>
          </div>

          <div class="action-buttons">
            <button
              v-if="stateStore.enableSpeechInput"
              type="button"
              class="btn-outline btn-large"
              :class="{ 'is-listening': isListening }"
              @click="toggleSpeechInput"
            >
              {{ isListening ? '结束语音输入' : '语音输入' }}
            </button>

            <button type="button" class="btn-primary btn-large" :disabled="!canSend || streaming" @click="submitMessage">
              {{ streaming ? '回复生成中...' : '发送追问' }}
            </button>
          </div>
        </div>
      </div>
    </template>
  </section>
</template>

<style scoped>
.composer-shell {
  padding: 20px;
}

.empty-actions,
.upload-zone,
.chat-composer {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.empty-actions {
  align-items: center;
  justify-content: center;
  min-height: 180px;
  text-align: center;
}

.empty-actions p,
.upload-copy p {
  margin: 0;
  color: var(--td-text-secondary);
}

.upload-copy h3 {
  margin: 0 0 6px;
  color: var(--td-text-main);
}

.selected-preview {
  display: flex;
  gap: 14px;
  padding: 14px;
  border-radius: 22px;
}

.selected-preview img {
  width: 112px;
  height: 112px;
  object-fit: cover;
  border-radius: 18px;
}

.selected-preview strong {
  color: var(--td-text-main);
}

.selected-preview p {
  margin: 6px 0 0;
  color: var(--td-text-muted);
}

.composer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.btn-large {
  min-height: 40px;
  padding: 0 24px;
  font-size: 15px;
  border-radius: 8px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  font-weight: 500;
}

.btn-primary {
  background: var(--td-primary-500);
  color: white;
  border: none;
}
.btn-primary:hover:not(:disabled) {
  background: var(--td-primary-600);
}
.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-outline {
  background: transparent;
  color: var(--td-text-main);
  border: 1px solid var(--td-border-color);
}
.btn-outline:hover {
  border-color: var(--td-primary-500);
  color: var(--td-primary-500);
}
.btn-outline.is-listening {
  color: var(--td-warning-500);
  border-color: var(--td-warning-500);
}

.custom-textarea {
  width: 100%;
  padding: 12px 16px;
  border-radius: 12px;
  background: var(--td-surface);
  border: 1px solid var(--td-border-color);
  color: var(--td-text-main);
  font-size: 15px;
  line-height: 1.5;
  resize: vertical;
  min-height: 80px;
  max-height: 200px;
  font-family: inherit;
  transition: border-color 0.2s;
}

.custom-textarea:focus {
  outline: none;
  border-color: var(--td-primary-500);
}

@media (max-width: 768px) {
  .composer-shell {
    padding: 16px;
  }

  .selected-preview,
  .composer-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .selected-preview img {
    width: 100%;
    height: auto;
    max-height: 220px;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-buttons button {
    width: 100%;
    margin: 0;
  }

  .action-buttons button + button {
    margin-top: 12px;
  }
}
</style>
