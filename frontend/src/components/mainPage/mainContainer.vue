<script setup>
import { ref, watch } from 'vue'
import Main from './main.vue'
import DialogBox from './dialogBox.vue'

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
const dialogRef = ref(null)

/**
 * 上传状态变化时，让底部进度提示组件同步开始或结束。
 * 这个同步放在容器层，避免消息区和输入区互相直接依赖。
 */
watch(
  () => props.uploading,
  (uploading) => {
    if (uploading) {
      dialogRef.value?.startProgress?.()
      return
    }

    dialogRef.value?.stopProgress?.()
  },
)
</script>

<template>
  <div class="workspace-column">
    <Main :messages="messages" :mode="mode" :loading="loading" />
    <DialogBox
      ref="dialogRef"
      :mode="mode"
      :can-send="canSend"
      :can-upload="canUpload"
      :uploading="uploading"
      :streaming="streaming"
      @submit-message="emit('submit-message', $event)"
      @submit-image="emit('submit-image', $event)"
      @request-draft="emit('request-draft')"
    />
  </div>
</template>

<style scoped>
.workspace-column {
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-width: 0;
}
</style>
