<script setup>
import { ref, watch } from 'vue'
import DialogBox from './dialogBox.vue'
import Main from './main.vue'

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
    <Main class="message-panel" :messages="messages" :mode="mode" :loading="loading" />
    <DialogBox
      ref="dialogRef"
      class="composer-panel"
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
  min-height: 0;
  height: 100%;
}

.message-panel {
  flex: 1;
  min-height: 0;
}

.composer-panel {
  flex-shrink: 0;
}
</style>
