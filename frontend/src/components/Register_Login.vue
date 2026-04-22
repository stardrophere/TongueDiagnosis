<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { Message as ElMessage } from '@/utils/message'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { appMeta } from '@/config/appConfig'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const activeTab = ref(route.meta?.authMode === 'register' ? 'register' : 'login')
const submitting = ref(false)

const loginForm = reactive({
  email: '',
  password: '',
})

const registerForm = reactive({
  email: '',
  password: '',
  confirmPassword: '',
})

const errors = reactive({
  email: '',
  password: '',
  confirmPassword: ''
})

const currentForm = computed(() => (activeTab.value === 'login' ? loginForm : registerForm))
const redirectPath = computed(() => String(route.query.redirect || '/check'))

function validateForm() {
  let valid = true
  errors.email = ''
  errors.password = ''
  errors.confirmPassword = ''

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!currentForm.value.email.trim()) {
    errors.email = '请输入邮箱地址。'
    valid = false
  } else if (!emailRegex.test(currentForm.value.email.trim())) {
    errors.email = '请输入有效的邮箱地址。'
    valid = false
  }

  const pattern = /^[a-zA-Z0-9]+$/
  if (!currentForm.value.password) {
    errors.password = '请输入密码。'
    valid = false
  } else if (currentForm.value.password.length < 6) {
    errors.password = '密码长度不能少于 6 位。'
    valid = false
  } else if (currentForm.value.password.length > 20) {
    errors.password = '密码长度不能超过 20 位。'
    valid = false
  } else if (!pattern.test(currentForm.value.password)) {
    errors.password = '密码暂仅支持英文与数字组合。'
    valid = false
  }

  if (activeTab.value === 'register') {
    if (!registerForm.confirmPassword) {
      errors.confirmPassword = '请再次输入密码。'
      valid = false
    } else if (registerForm.confirmPassword !== registerForm.password) {
      errors.confirmPassword = '两次输入的密码不一致。'
      valid = false
    }
  }

  return valid
}

function switchTab(tab) {
  activeTab.value = tab
  errors.email = ''
  errors.password = ''
  errors.confirmPassword = ''

  const targetPath = tab === 'register' ? '/register' : '/login'
  if (route.path !== targetPath) {
    router.replace({
      path: targetPath,
      query: route.query,
    })
  }
}

watch(
  () => route.path,
  (path) => {
    activeTab.value = path === '/register' ? 'register' : 'login'
  },
  { immediate: true },
)

function resolveAuthMessage(result, mode) {
  if (mode === 'login') {
    if (result.code === 101) return '该账号尚未注册，请先完成注册。'
    if (result.code === 102) return '密码错误，请重新输入。'
    return result.message || '登录失败，请稍后重试。'
  }
  if (result.code === 101) return '该邮箱已经注册，请直接登录。'
  return result.message || '注册失败，请稍后重试。'
}

async function handleLogin() {
  if (!validateForm()) return

  submitting.value = true

  try {
    const result = await authStore.login({
      email: loginForm.email.trim(),
      password: loginForm.password,
    })

    if (result.code !== 0) {
      ElMessage.error(resolveAuthMessage(result, 'login'))
      return
    }

    await authStore.ensureProfile(true)
    ElMessage.success('登录成功，正在进入诊断工作台。')
    router.replace(redirectPath.value)
  } catch (error) {
    console.error(error)
    ElMessage.error('登录过程中发生异常，请稍后重试。')
  } finally {
    submitting.value = false
  }
}

async function handleRegister() {
  if (!validateForm()) return

  submitting.value = true

  try {
    const result = await authStore.register({
      email: registerForm.email.trim(),
      password: registerForm.password,
    })

    if (result.code !== 0) {
      ElMessage.error(resolveAuthMessage(result, 'register'))
      return
    }

    ElMessage.success('注册成功，请使用新账号登录。')
    switchTab('login')
    loginForm.email = registerForm.email.trim()
    loginForm.password = ''
    registerForm.password = ''
    registerForm.confirmPassword = ''
  } catch (error) {
    console.error(error)
    ElMessage.error('注册过程中发生异常，请稍后重试。')
  } finally {
    submitting.value = false
  }
}

function handleSubmit() {
  if (activeTab.value === 'login') {
    handleLogin()
  } else {
    handleRegister()
  }
}
</script>

<template>
  <section class="auth-shell">
    <div class="auth-layout page-section">
      <div class="auth-copy page-card">
        <span class="status-chip">智能诊断入口</span>
        <h1 class="section-title">{{ appMeta.name }}</h1>
        <p class="section-subtitle">
          欢迎使用中医舌象辅助分析平台。请登录或注册您的专属账号，开启智能诊断体验。
        </p>

        <div class="copy-list">
          <article class="copy-item glass-card">
            <strong>安全可靠</strong>
            <span>您的所有诊断记录和个人数据都将经过严格保护，保障您的隐私安全。</span>
          </article>
          <article class="copy-item glass-card">
            <strong>多端同步</strong>
            <span>支持在不同设备上登录，无缝同步您的舌象档案与历史会话记录。</span>
          </article>
          <article class="copy-item glass-card">
            <strong>智能高效</strong>
            <span>快速进入工作台，毫秒级获取中医证候分析与针对性的调理建议。</span>
          </article>
        </div>
      </div>

      <div class="auth-panel page-card">
        <div class="panel-head">
          <div>
            <p class="panel-label">账号认证</p>
            <h2>{{ activeTab === 'login' ? '登录账号' : '创建账号' }}</h2>
          </div>
          <div class="tab-switcher">
            <button
              type="button"
              class="tab-button"
              :class="{ active: activeTab === 'login' }"
              @click="switchTab('login')"
            >
              登录
            </button>
            <button
              type="button"
              class="tab-button"
              :class="{ active: activeTab === 'register' }"
              @click="switchTab('register')"
            >
              注册
            </button>
          </div>
        </div>

        <form class="auth-form" @submit.prevent="handleSubmit">
          <div class="form-group">
            <label class="form-label">邮箱地址</label>
            <input
              v-model="currentForm.email"
              type="text"
              class="form-input"
              placeholder="请输入常用邮箱"
              :class="{ 'is-error': errors.email }"
            />
            <span v-if="errors.email" class="error-msg">{{ errors.email }}</span>
          </div>

          <div class="form-group">
            <label class="form-label">登录密码</label>
            <input
              v-model="currentForm.password"
              type="password"
              class="form-input"
              placeholder="请输入密码"
              :class="{ 'is-error': errors.password }"
            />
            <span v-if="errors.password" class="error-msg">{{ errors.password }}</span>
          </div>

          <div v-if="activeTab === 'register'" class="form-group">
            <label class="form-label">确认密码</label>
            <input
              v-model="registerForm.confirmPassword"
              type="password"
              class="form-input"
              placeholder="请再次输入密码"
              :class="{ 'is-error': errors.confirmPassword }"
            />
            <span v-if="errors.confirmPassword" class="error-msg">{{ errors.confirmPassword }}</span>
          </div>

          <div class="auth-actions">
            <button type="submit" class="btn-primary btn-large" :disabled="submitting">
              {{ activeTab === 'login' ? '登录并进入工作台' : '注册账号' }}
            </button>
            <p class="helper-text">
              {{
                activeTab === 'login'
                  ? '还没有账号？点击上方“注册”即可立即创建。'
                  : '已有账号？切回“登录”即可进入诊断工作台。'
              }}
            </p>
          </div>
        </form>
      </div>
    </div>
  </section>
</template>

<style scoped>
.auth-shell {
  padding: 24px 0 48px;
}

.auth-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(360px, 460px);
  gap: 24px;
}

.auth-copy,
.auth-panel {
  padding: 32px;
}

.auth-copy {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.copy-list {
  display: grid;
  gap: 14px;
}

.copy-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px;
  border-radius: 20px;
}

.copy-item strong {
  color: var(--td-text-main);
}

.copy-item span {
  color: var(--td-text-secondary);
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 24px;
}

.panel-label {
  margin: 0 0 8px;
  color: var(--td-primary-600);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
}

.panel-head h2 {
  margin: 0;
  color: var(--td-text-main);
}

.tab-switcher {
  display: inline-flex;
  padding: 4px;
  border-radius: 999px;
  background: var(--td-primary-soft);
}

.tab-button {
  min-width: 72px;
  min-height: 38px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--td-text-secondary);
  cursor: pointer;
  transition: 0.2s ease;
}

.tab-button.active {
  background: var(--td-surface);
  color: var(--td-primary-700);
  box-shadow: 0 8px 16px var(--td-primary-soft);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  color: var(--td-text-main);
  font-weight: 500;
}

.form-input {
  width: 100%;
  height: 44px;
  padding: 0 16px;
  border-radius: 8px;
  border: 1px solid var(--td-border-color);
  background: var(--td-surface);
  color: var(--td-text-main);
  font-size: 15px;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: var(--td-primary-500);
}

.form-input.is-error {
  border-color: var(--td-danger-500);
}

.error-msg {
  color: var(--td-danger-500);
  font-size: 12px;
}

.auth-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.btn-large {
  width: 100%;
  height: 44px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
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

.helper-text {
  margin: 0;
  color: var(--td-text-muted);
  font-size: 13px;
}

@media (max-width: 1024px) {
  .auth-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .auth-copy,
  .auth-panel {
    padding: 22px;
  }

  .panel-head {
    flex-direction: column;
  }

  .tab-switcher {
    width: 100%;
  }

  .tab-button {
    flex: 1;
  }
}
</style>