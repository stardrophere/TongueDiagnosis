<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Microphone, Promotion, UploadFilled } from '@element-plus/icons-vue'
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
 * 选择图片后只在本地暂存，真正发起诊断由用户点击按钮确认。
 */
function handleImageSelected(payload) {
  selectedImage.value = payload
}

/**
 * 草稿模式下点击“开始分析”才会真正触发上传，避免用户刚选错图就立即发请求。
 */
function submitImage() {
  if (!selectedImage.value) {
    ElMessage.warning('请先选择一张清晰的舌象图片。')
    return
  }

  emit('submit-image', selectedImage.value)
}

/**
 * 发送追问前统一做空值清洗，避免把纯空格提交到后端。
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
 * 初始化浏览器语音识别能力。
 * 当前仅在 Chrome 系内核浏览器中较稳定，因此保留能力检测。
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
 * 上传状态切换时同步控制底部的步骤提示组件，让视觉反馈始终准确。
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
        <el-button type="primary" size="large" @click="emit('request-draft')">
          <el-icon><UploadFilled /></el-icon>
          新建诊断并上传图片
        </el-button>
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

        <el-button type="primary" size="large" :disabled="!canStartImageAnalysis" @click="submitImage">
          开始分析图片
        </el-button>

        <Steps v-if="uploading" ref="uploadProgressRef" />
      </div>
    </template>

    <template v-else>
      <div class="chat-composer">
        <el-input
          v-model="inputValue"
          type="textarea"
          resize="none"
          :autosize="{ minRows: 3, maxRows: 6 }"
          placeholder="请输入要继续追问的问题，例如：这种舌象通常说明什么体质？后续应如何调理？"
          @keydown="handleEnter"
        />

        <div class="composer-actions">
          <div class="action-hint">
            <span class="text-muted">支持继续追问症状、体质、作息建议与饮食方向。</span>
          </div>

          <div class="action-buttons">
            <el-button
              v-if="stateStore.enableSpeechInput"
              size="large"
              plain
              :type="isListening ? 'warning' : 'default'"
              @click="toggleSpeechInput"
            >
              <el-icon><Microphone /></el-icon>
              {{ isListening ? '结束语音输入' : '语音输入' }}
            </el-button>

            <el-button type="primary" size="large" :disabled="!canSend || streaming" @click="submitMessage">
              <el-icon><Promotion /></el-icon>
              {{ streaming ? '回复生成中...' : '发送追问' }}
            </el-button>
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
}
</style>
