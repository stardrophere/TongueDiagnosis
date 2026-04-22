<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { appMeta } from '@/config/appConfig'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref()
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

/**
 * 登录和注册共用邮箱校验规则，避免两套表单分别维护同一段逻辑。
 */
function validateEmail(_rule, value, callback) {
  const email = String(value || '').trim()
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

  if (!email) {
    callback(new Error('请输入邮箱地址。'))
    return
  }

  if (!emailRegex.test(email)) {
    callback(new Error('请输入有效的邮箱地址。'))
    return
  }

  callback()
}

/**
 * 密码最少 6 位，并限制为英文/数字组合，尽量与现有后端兼容。
 */
function validatePassword(_rule, value, callback) {
  const password = String(value || '')
  const pattern = /^[a-zA-Z0-9]+$/

  if (!password) {
    callback(new Error('请输入密码。'))
    return
  }

  if (password.length < 6) {
    callback(new Error('密码长度不能少于 6 位。'))
    return
  }

  if (password.length > 20) {
    callback(new Error('密码长度不能超过 20 位。'))
    return
  }

  if (!pattern.test(password)) {
    callback(new Error('密码暂仅支持英文与数字组合。'))
    return
  }

  callback()
}

/**
 * 注册时二次确认密码，防止用户输入错误后直接提交。
 */
function validateConfirmPassword(_rule, value, callback) {
  if (!value) {
    callback(new Error('请再次输入密码。'))
    return
  }

  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致。'))
    return
  }

  callback()
}

const loginRules = {
  email: [{ validator: validateEmail, trigger: 'blur' }],
  password: [{ validator: validatePassword, trigger: 'blur' }],
}

const registerRules = {
  email: [{ validator: validateEmail, trigger: 'blur' }],
  password: [{ validator: validatePassword, trigger: 'blur' }],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }],
}

const currentRules = computed(() => (activeTab.value === 'login' ? loginRules : registerRules))
const currentForm = computed(() => (activeTab.value === 'login' ? loginForm : registerForm))
const redirectPath = computed(() => String(route.query.redirect || '/check'))

/**
 * 路由和页签保持同步，方便用户刷新页面后仍停留在正确的认证模式。
 */
function switchTab(tab) {
  activeTab.value = tab
  formRef.value?.clearValidate?.()

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

/**
 * 根据后端业务码给出更准确的中文反馈，而不是一律提示“失败”。
 */
function resolveAuthMessage(result, mode) {
  if (mode === 'login') {
    if (result.code === 101) {
      return '该账号尚未注册，请先完成注册。'
    }

    if (result.code === 102) {
      return '密码错误，请重新输入。'
    }

    return result.message || '登录失败，请稍后重试。'
  }

  if (result.code === 101) {
    return '该邮箱已经注册，请直接登录。'
  }

  return result.message || '注册失败，请稍后重试。'
}

/**
 * 登录成功后优先拉取用户资料，再跳转回目标页面。
 */
async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) {
    return
  }

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

/**
 * 注册成功后不直接强制跳转工作台，而是回到登录页让用户完成显式登录。
 */
async function handleRegister() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) {
    return
  }

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

/**
 * 提交入口统一根据当前页签切换，模板层只保留一个按钮事件。
 */
function handleSubmit() {
  if (activeTab.value === 'login') {
    handleLogin()
    return
  }

  handleRegister()
}
</script>

<template>
  <section class="auth-shell">
    <div class="auth-layout page-section">
      <div class="auth-copy page-card">
        <span class="status-chip">智能诊断入口</span>
        <h1 class="section-title">{{ appMeta.name }}</h1>
        <p class="section-subtitle">
          重新设计后的认证流程以“快速进入诊断工作台”为目标，减少跳转、混乱动画与无意义视觉噪音。
        </p>

        <div class="copy-list">
          <article class="copy-item glass-card">
            <strong>统一中文反馈</strong>
            <span>登录、注册、鉴权失效与异常情况都将给出明确中文提示。</span>
          </article>
          <article class="copy-item glass-card">
            <strong>移动端友好</strong>
            <span>认证卡片与说明区会自动折叠重排，避免旧版布局在小屏上挤压变形。</span>
          </article>
          <article class="copy-item glass-card">
            <strong>更稳定的跳转逻辑</strong>
            <span>未登录访问诊断页会自动回跳登录页，登录成功后继续回到目标页面。</span>
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

        <el-form
          ref="formRef"
          class="auth-form"
          :model="currentForm"
          :rules="currentRules"
          label-position="top"
        >
          <el-form-item label="邮箱地址" prop="email">
            <el-input
              v-model="currentForm.email"
              size="large"
              placeholder="请输入常用邮箱"
              clearable
            />
          </el-form-item>

          <el-form-item label="登录密码" prop="password">
            <el-input
              v-model="currentForm.password"
              size="large"
              placeholder="请输入密码"
              type="password"
              show-password
            />
          </el-form-item>

          <el-form-item v-if="activeTab === 'register'" label="确认密码" prop="confirmPassword">
            <el-input
              v-model="registerForm.confirmPassword"
              size="large"
              placeholder="请再次输入密码"
              type="password"
              show-password
            />
          </el-form-item>

          <div class="auth-actions">
            <el-button type="primary" size="large" :loading="submitting" @click="handleSubmit">
              {{ activeTab === 'login' ? '登录并进入工作台' : '注册账号' }}
            </el-button>
            <p class="helper-text">
              {{
                activeTab === 'login'
                  ? '还没有账号？点击上方“注册”即可立即创建。'
                  : '已有账号？切回“登录”即可进入诊断工作台。'
              }}
            </p>
          </div>
        </el-form>
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
  background: rgba(31, 138, 112, 0.08);
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
  background: #fff;
  color: var(--td-primary-700);
  box-shadow: 0 8px 16px rgba(31, 138, 112, 0.1);
}

.auth-form {
  display: flex;
  flex-direction: column;
}

.auth-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
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
