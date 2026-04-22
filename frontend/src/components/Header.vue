<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useStateStore } from '@/stores/stateStore'
import { appMeta } from '@/config/appConfig'
import { Moon, Sunny } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const stateStore = useStateStore()

const isScrolled = ref(false)
const isMobileMenuOpen = ref(false)

const navItems = [
  { label: '首页', path: '/home' },
  { label: '智能诊断', path: '/check' },
]

/**
 * 暴露部分计算属性与响应式状态
 */
const isAuthenticated = computed(() => authStore.isAuthenticated)
const userProfile = computed(() => authStore.profile || {})
const activePath = computed(() => route.path)
const displayName = computed(() => userProfile.value.name || userProfile.value.email || '已登录用户')
const userInitial = computed(() => String(displayName.value).slice(0, 1).toUpperCase())

function handleScroll() {
  isScrolled.value = window.scrollY > 16
}

function closeMobileMenu() {
  isMobileMenuOpen.value = false
}

function toggleMobileMenu() {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

/**
 * 静默获取用户资料
 */
async function ensureProfileSilently() {
  if (!authStore.token) {
    return
  }

  try {
    await authStore.ensureProfile()
  } catch (error) {
    console.error(error)
  }
}

/**
 * 退出登录并跳转
 */
function handleLogout() {
  authStore.logout()
  closeMobileMenu()
  ElMessage.success('您已安全退出登录。')
  router.push('/login')
}

onMounted(() => {
  handleScroll()
  ensureProfileSilently()
  window.addEventListener('scroll', handleScroll)
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
})

watch(
  () => route.fullPath,
  () => {
    closeMobileMenu()
    ensureProfileSilently()
  },
)
</script>

<template>
  <header class="app-header" :class="{ scrolled: isScrolled }">
    <div class="header-inner">
      <router-link to="/home" class="brand" @click="closeMobileMenu">
        <div class="brand-mark">舌</div>
        <div class="brand-copy">
          <strong>{{ appMeta.name }}</strong>
          <span>{{ appMeta.description }}</span>
        </div>
      </router-link>

      <nav class="desktop-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-link"
          :class="{ active: activePath === item.path }"
        >
          {{ item.label }}
        </router-link>
      </nav>

      <div class="header-actions">
        <!-- 黑白模式切换按钮 -->
        <button type="button" class="theme-toggle" @click="stateStore.toggleDarkMode" :title="stateStore.isDarkMode ? '切换到浅色模式' : '切换到深色模式'">
          <el-icon v-if="stateStore.isDarkMode"><Sunny /></el-icon>
          <el-icon v-else><Moon /></el-icon>
        </button>

        <div v-if="isAuthenticated" class="desktop-profile">
          <el-dropdown trigger="click">
            <button type="button" class="profile-trigger">
              <div class="profile-avatar">{{ userInitial }}</div>
              <div class="profile-copy">
                <strong>{{ displayName }}</strong>
                <span>智能诊断工作台</span>
              </div>
              <el-icon><ArrowDown /></el-icon>
            </button>

            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>
                  {{ userProfile.email || '当前账号已登录' }}
                </el-dropdown-item>
                <el-dropdown-item @click="router.push('/check')">进入诊断页</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <div v-else class="auth-entry">
          <router-link to="/login" class="ghost-link">登录</router-link>
          <router-link to="/register" class="primary-link">注册体验</router-link>
        </div>

        <button type="button" class="mobile-toggle" @click="toggleMobileMenu">
          <el-icon v-if="!isMobileMenuOpen"><Menu /></el-icon>
          <el-icon v-else><Close /></el-icon>
        </button>
      </div>
    </div>

    <div class="mobile-panel" :class="{ open: isMobileMenuOpen }">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="mobile-link"
        :class="{ active: activePath === item.path }"
        @click="closeMobileMenu"
      >
        {{ item.label }}
      </router-link>

      <template v-if="isAuthenticated">
        <div class="mobile-profile-card">
          <div class="profile-avatar">{{ userInitial }}</div>
          <div>
            <strong>{{ displayName }}</strong>
            <p>{{ userProfile.email || '欢迎回来，继续您的诊断工作。' }}</p>
          </div>
        </div>
        <el-button type="danger" plain @click="handleLogout">退出登录</el-button>
      </template>

      <template v-else>
        <router-link to="/login" class="mobile-auth-link" @click="closeMobileMenu">登录账号</router-link>
        <router-link to="/register" class="mobile-auth-link primary" @click="closeMobileMenu">
          注册新账号
        </router-link>
      </template>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  position: fixed;
  top: 14px;
  left: 50%;
  z-index: 1000;
  width: min(calc(100% - 24px), var(--td-max-width));
  transform: translateX(-50%);
  border: 1px solid var(--td-border-color);
  border-radius: 24px;
  background: var(--td-bg-elevated);
  box-shadow: var(--td-header-shadow);
  backdrop-filter: blur(22px);
  transition: 0.25s ease;
}

.app-header.scrolled {
  background: var(--td-panel-strong);
  border-color: var(--td-border-strong);
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 72px;
  padding: 0 20px;
  gap: 16px;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
  text-decoration: none;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--td-primary-600), var(--td-secondary-500));
  color: #fff;
  font-size: 20px;
  font-weight: 800;
  box-shadow: 0 12px 24px rgba(31, 138, 112, 0.18);
}

.brand-copy {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.brand-copy strong {
  color: var(--td-text-main);
  font-size: 15px;
}

.brand-copy span {
  color: var(--td-text-muted);
  font-size: 12px;
  white-space: nowrap;
}

.desktop-nav,
.header-actions,
.auth-entry {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-link {
  padding: 10px 16px;
  border-radius: 999px;
  color: var(--td-text-secondary);
  text-decoration: none;
  transition: 0.2s ease;
}

.nav-link.active,
.nav-link:hover {
  background: var(--td-primary-soft);
  color: var(--td-primary-700);
}

.ghost-link,
.primary-link,
.mobile-auth-link {
  text-decoration: none;
}

.ghost-link {
  color: var(--td-text-secondary);
  padding: 10px 16px;
}

.primary-link,
.mobile-auth-link.primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 42px;
  padding: 0 18px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--td-primary-600), var(--td-secondary-500));
  color: #fff;
  box-shadow: 0 12px 24px rgba(31, 138, 112, 0.18);
}

.profile-trigger {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border: 0;
  border-radius: 18px;
  background: transparent;
  cursor: pointer;
  color: var(--td-text-main);
}

.profile-avatar {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--td-primary-soft), rgba(95, 167, 255, 0.22));
  color: var(--td-primary-700);
  font-weight: 800;
}

.profile-copy {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.profile-copy strong {
  font-size: 14px;
}

.profile-copy span {
  color: var(--td-text-muted);
  font-size: 12px;
}

.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border: 0;
  border-radius: 50%;
  background: rgba(31, 138, 112, 0.08);
  color: var(--td-text-main);
  cursor: pointer;
  transition: 0.2s ease;
}

.theme-toggle:hover {
  background: rgba(31, 138, 112, 0.15);
}

.mobile-toggle {
  display: none;
  width: 42px;
  height: 42px;
  border: 0;
  border-radius: 14px;
  background: rgba(31, 138, 112, 0.08);
  color: var(--td-primary-700);
  cursor: pointer;
}

.mobile-panel {
  display: none;
  padding: 0 16px 16px;
}

.mobile-link,
.mobile-auth-link {
  display: flex;
  align-items: center;
  min-height: 46px;
  padding: 0 14px;
  border-radius: 16px;
  color: var(--td-text-main);
}

.mobile-link.active {
  background: var(--td-primary-soft);
  color: var(--td-primary-700);
}

.mobile-profile-card {
  display: flex;
  gap: 12px;
  padding: 14px;
  margin: 8px 0 12px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.75);
}

.mobile-profile-card p {
  margin: 4px 0 0;
  color: var(--td-text-muted);
  font-size: 13px;
}

@media (max-width: 900px) {
  .desktop-nav,
  .desktop-profile,
  .auth-entry {
    display: none;
  }

  .mobile-toggle {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .mobile-panel {
    display: grid;
    gap: 8px;
    max-height: 0;
    overflow: hidden;
    padding-top: 0;
    opacity: 0;
    transition: 0.25s ease;
  }

  .mobile-panel.open {
    max-height: 360px;
    padding-top: 0;
    opacity: 1;
  }
}

@media (max-width: 640px) {
  .brand-copy span {
    display: none;
  }

  .header-inner {
    padding: 0 14px;
  }

  .app-header {
    top: 10px;
    width: calc(100% - 16px);
  }
}
</style>
