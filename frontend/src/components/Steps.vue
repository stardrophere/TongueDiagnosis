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
 * 启动模拟进度动画
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
 * 停止模拟进度动画
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
      <svg class="progress-svg" viewBox="0 0 100 100">
        <circle class="progress-bg" cx="50" cy="50" r="40"></circle>
        <circle class="progress-bar" cx="50" cy="50" r="40" :stroke-dashoffset="251 - (251 * progress) / 100"></circle>
      </svg>
      <div class="progress-text">{{ Math.round(progress) }}%</div>
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
  background: var(--td-panel-bg);
  border: 1px solid var(--td-border-color);
}

.progress-ring {
  flex-shrink: 0;
  position: relative;
  width: 80px;
  height: 80px;
}

.progress-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.progress-bg {
  fill: none;
  stroke: var(--td-border-color);
  stroke-width: 8;
}

.progress-bar {
  fill: none;
  stroke: var(--td-primary-500);
  stroke-width: 8;
  stroke-linecap: round;
  stroke-dasharray: 251;
  transition: stroke-dashoffset 0.3s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 14px;
  font-weight: bold;
  color: var(--td-text-main);
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
