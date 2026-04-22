<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'

const totalSeconds = 40
const elapsedSeconds = ref(0)
let timer = null

const progress = computed(() => Math.min((elapsedSeconds.value / totalSeconds) * 100, 100))
const statusText = computed(() => {
  if (elapsedSeconds.value < 10) {
    return '正在接收图像并准备分析模型...'
  }

  if (elapsedSeconds.value < 24) {
    return '正在解析舌象特征，请稍候...'
  }

  return '正在生成结构化诊断建议...'
})

/**
 * 上传开始时启动进度提示。
 * 这里只做体验层模拟，不代表后端真实进度。
 */
function start() {
  stop()
  elapsedSeconds.value = 0

  timer = window.setInterval(() => {
    elapsedSeconds.value += 1
    if (elapsedSeconds.value >= totalSeconds) {
      stop()
    }
  }, 1000)
}

/**
 * 结束当前进度动画，避免组件卸载后仍持续计时。
 */
function stop() {
  if (timer) {
    window.clearInterval(timer)
    timer = null
  }
}

defineExpose({
  start,
  stop,
})

onBeforeUnmount(() => {
  stop()
})
</script>

<template>
  <div class="progress-card">
    <div class="progress-ring">
      <el-progress type="dashboard" :percentage="progress" :stroke-width="10" color="#1f8a70" />
    </div>
    <div class="progress-copy">
      <strong>图像分析处理中</strong>
      <p>{{ statusText }}</p>
      <span>通常会在 40 秒内返回首轮结果，请保持页面开启。</span>
    </div>
  </div>
</template>

<style scoped>
.progress-card {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 18px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(31, 138, 112, 0.1);
}

.progress-ring {
  flex-shrink: 0;
}

.progress-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.progress-copy strong {
  color: var(--td-text-main);
}

.progress-copy p {
  margin: 0;
  color: var(--td-text-secondary);
}

.progress-copy span {
  color: var(--td-text-muted);
  font-size: 13px;
}

@media (max-width: 640px) {
  .progress-card {
    flex-direction: column;
    text-align: center;
  }
}
</style>
