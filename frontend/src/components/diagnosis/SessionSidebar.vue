<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  sessions: {
    type: Array,
    default: () => [],
  },
  activeSessionId: {
    type: [String, Number, null],
    default: null,
  },
  draftSessionName: {
    type: String,
    default: '',
  },
  hasDraft: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  deletingSessionId: {
    type: [String, Number, null],
    default: null,
  },
})

const emit = defineEmits(['create-draft', 'select-session', 'update-draft-name', 'delete-session'])
const localDraftName = ref(props.draftSessionName)

watch(
  () => props.draftSessionName,
  (value) => {
    localDraftName.value = value
  },
  { immediate: true },
)

const isEmpty = computed(() => !props.loading && !props.hasDraft && props.sessions.length === 0)

function handleDraftNameChange(value) {
  emit('update-draft-name', value)
}
</script>

<template>
  <aside class="session-sidebar">
    <div class="sidebar-header panel-surface">
      <div>
        <p class="eyebrow">诊断记录</p>
        <h2>管理您的舌诊会话</h2>
        <p class="sidebar-desc">新建记录后上传图片，即可自动生成首轮分析并继续追问。</p>
      </div>
      <button type="button" class="btn-primary btn-round" @click="emit('create-draft')">新建诊断</button>
    </div>

    <div v-if="hasDraft" class="draft-editor panel-surface">
      <div class="draft-head">
        <span class="draft-badge">未保存草稿</span>
        <span class="draft-tip">上传图片后会自动生成正式记录</span>
      </div>
      <input
        class="form-input"
        v-model="localDraftName"
        placeholder="请输入本次诊断名称"
        maxlength="30"
        @input="handleDraftNameChange($event.target.value)"
      />
    </div>

    <div class="session-list panel-surface" v-loading="loading">
      <div class="list-header">
        <span>历史记录</span>
        <span class="list-count">{{ sessions.length }}</span>
      </div>

      <div
        v-if="hasDraft"
        class="session-item draft-item"
        :class="{ active: activeSessionId === null }"
      >
        <div class="session-meta">
          <strong>{{ draftSessionName }}</strong>
          <small>等待上传图片</small>
        </div>
      </div>

      <div
        v-for="session in sessions"
        :key="session.id"
        class="session-entry"
        :class="{ active: activeSessionId === session.id }"
      >
        <button
          type="button"
          class="session-item"
          :class="{ active: activeSessionId === session.id }"
          @click="emit('select-session', session.id)"
        >
          <div class="session-meta">
            <strong>{{ session.name }}</strong>
            <small>ID: {{ session.id }}</small>
          </div>
          <span class="icon-right">›</span>
        </button>

        <button
          type="button"
          class="delete-button"
          :disabled="deletingSessionId === session.id"
          @click.stop="emit('delete-session', session.id)"
        >
          {{ deletingSessionId === session.id ? '删除中...' : '删除' }}
        </button>
      </div>

      <div v-if="isEmpty" class="empty-state">
        <p>还没有任何诊断记录。</p>
        <span>点击上方“新建诊断”开始第一次舌象分析。</span>
      </div>
    </div>

    <div class="sidebar-footer panel-surface">
      <h3>拍摄提醒</h3>
      <ul>
        <li>自然光线下拍摄，避免滤镜和强反光。</li>
        <li>尽量保证舌面完整、清晰、无遮挡。</li>
        <li>本结果仅供参考，不替代专业面诊。</li>
      </ul>
    </div>
  </aside>
</template>

<style scoped>
.session-sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 320px;
  min-width: 280px;
  height: 100%;
  min-height: 0;
}

.panel-surface {
  border: 1px solid var(--td-border-color);
  background: var(--td-panel-bg);
  border-radius: 24px;
  box-shadow: var(--td-soft-shadow);
  backdrop-filter: blur(18px);
}

.sidebar-header,
.draft-editor,
.sidebar-footer {
  padding: 20px;
}

.eyebrow {
  margin-bottom: 8px;
  color: var(--td-primary-600);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
}

.sidebar-header h2,
.sidebar-footer h3 {
  margin: 0;
  color: var(--td-text-main);
}

.sidebar-desc,
.draft-tip,
.sidebar-footer li,
.empty-state span,
.session-meta small {
  color: var(--td-text-muted);
}

.sidebar-header {
  display: grid;
  gap: 16px;
}

.draft-head {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-bottom: 14px;
  gap: 8px;
}

.draft-tip {
  font-size: 13px;
  color: var(--td-text-muted);
  line-height: 1.4;
}

.draft-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  background: var(--td-primary-soft);
  color: var(--td-primary-700);
  font-size: 12px;
  font-weight: 600;
}

.session-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 6px 10px;
  color: var(--td-text-main);
  font-weight: 600;
}

.list-count {
  display: inline-flex;
  min-width: 28px;
  justify-content: center;
  padding: 4px 8px;
  border-radius: 999px;
  background: var(--td-primary-soft);
  color: var(--td-primary-700);
  font-size: 12px;
}

.session-entry {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px;
  align-items: stretch;
}

.session-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 14px 16px;
  border: 1px solid transparent;
  border-radius: 18px;
  background: var(--td-surface);
  color: var(--td-text-main);
  text-align: left;
  cursor: pointer;
  transition: 0.25s ease;
}

.session-item:hover {
  border-color: var(--td-primary-soft);
  transform: translateY(-1px);
}

.session-item.active {
  border-color: var(--td-primary-500);
  background: var(--td-primary-soft);
  box-shadow: inset 0 0 0 1px var(--td-primary-soft);
}

.draft-item {
  cursor: default;
}

.session-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.delete-button {
  align-self: center;
  min-width: 64px;
  height: 40px;
  padding: 0 12px;
  border: 0;
  border-radius: 12px;
  background: rgba(224, 62, 62, 0.08);
  color: var(--td-danger-500);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.delete-button:hover:not(:disabled) {
  background: rgba(224, 62, 62, 0.15);
  transform: translateY(-1px);
}

.delete-button:disabled {
  cursor: wait;
  opacity: 0.7;
}

.empty-state {
  padding: 32px 20px;
  text-align: center;
  border-radius: 18px;
  background: var(--td-panel-bg);
}

.sidebar-footer ul {
  margin: 12px 0 0;
  padding-left: 18px;
}

.sidebar-footer li + li {
  margin-top: 8px;
}

.btn-primary {
  background: var(--td-primary-500);
  color: white;
  border: none;
  cursor: pointer;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  transition: 0.2s;
}
.btn-primary:hover {
  background: var(--td-primary-600);
}
.btn-round {
  border-radius: 999px;
}

.form-input {
  width: 100%;
  height: 40px;
  padding: 0 12px;
  border-radius: 8px;
  border: 1px solid var(--td-border-color);
  background: var(--td-surface);
  color: var(--td-text-main);
  font-size: 14px;
  box-sizing: border-box;
  transition: 0.2s;
}
.form-input:focus {
  outline: none;
  border-color: var(--td-primary-500);
}

.icon-right {
  font-size: 20px;
  color: var(--td-text-muted);
  line-height: 1;
}

@media (max-width: 900px) {
  .session-sidebar {
    width: 100%;
    min-width: 0;
    height: auto;
  }

  .session-list {
    max-height: 320px;
  }
}
</style>
