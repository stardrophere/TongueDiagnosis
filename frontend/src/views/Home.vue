<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()

const ctaTarget = computed(() => (authStore.isAuthenticated ? '/check' : '/register'))
const ctaLabel = computed(() => (authStore.isAuthenticated ? '进入智能诊断' : '注册并开始体验'))

const highlights = [
  {
    title: 'AI 舌象分析',
    description: '上传舌象图片后，系统会自动生成首轮分析内容，并支持继续追问细节。',
  },
  {
    title: '会话式追问',
    description: '诊断结果不是一次性文本，而是可持续沟通的结构化诊断会话。',
  },
  {
    title: '记录可追溯',
    description: '所有诊断记录都会在左侧归档，便于后续复盘、对比与继续咨询。',
  },
]

const steps = [
  '创建新的诊断记录并命名本次会话。',
  '上传清晰的舌象图片，等待系统生成首轮分析。',
  '围绕症状、体质和建议继续追问，获取更完整的解释。',
]

const advantages = [
  '界面文案、提示语与按钮语义全面中文化，更贴合中医与国内用户场景。',
  '诊断页围绕“记录管理 + 上传分析 + 继续追问”进行整体重构，减少无效操作。',
  '请求层、鉴权流与核心逻辑统一收敛，后续维护和扩展会更稳定。',
]
</script>

<template>
  <div class="home-page">
    <section class="hero-section page-section">
      <div class="hero-shell page-card">
        <div class="hero-copy">
          <span class="status-chip">中医舌象辅助分析平台</span>
          <h1 class="section-title">让舌诊流程更专业、更清晰，也更适合持续追问。</h1>
          <p class="section-subtitle">
            面向舌象图像分析场景重构的 AI 前端工作台，聚焦“上传即分析、结果可追问、记录可回看”的完整使用闭环。
          </p>

          <div class="hero-actions">
            <router-link :to="ctaTarget" class="hero-primary">
              {{ ctaLabel }}
            </router-link>
            <router-link to="/home#workflow" class="hero-secondary">
              先了解诊断流程
            </router-link>
          </div>

          <div class="hero-metrics">
            <div class="metric-card glass-card">
              <strong>中文化</strong>
              <span>全站文案、提示语与操作反馈统一梳理</span>
            </div>
            <div class="metric-card glass-card">
              <strong>可追问</strong>
              <span>基于诊断会话继续补充症状、追问建议</span>
            </div>
            <div class="metric-card glass-card">
              <strong>可维护</strong>
              <span>请求层、鉴权流与诊断逻辑统一收敛</span>
            </div>
          </div>
        </div>

        <div class="hero-panel glass-card">
          <div class="panel-top">
            <div>
              <p class="panel-label">体验升级重点</p>
              <h2>从“能用”提升为“可信赖的医疗工具界面”</h2>
            </div>
            <span class="panel-badge">新版工作台</span>
          </div>

          <div class="panel-list">
            <article v-for="item in highlights" :key="item.title" class="panel-item">
              <h3>{{ item.title }}</h3>
              <p>{{ item.description }}</p>
            </article>
          </div>
        </div>
      </div>
    </section>

    <section id="workflow" class="workflow-section page-section">
      <div class="section-head">
        <span class="status-chip">操作流程</span>
        <h2 class="section-title">三步完成一次更顺畅的舌诊体验</h2>
        <p class="section-subtitle">
          诊断页已经围绕新建记录、上传图片、继续追问重新组织，不再依赖割裂的英文按钮和松散逻辑。
        </p>
      </div>

      <div class="workflow-grid">
        <article v-for="(item, index) in steps" :key="item" class="workflow-card page-card">
          <span class="workflow-index">0{{ index + 1 }}</span>
          <p>{{ item }}</p>
        </article>
      </div>
    </section>

    <section class="benefit-section page-section">
      <div class="benefit-layout">
        <div class="benefit-copy page-card">
          <span class="status-chip">为什么值得使用</span>
          <h2 class="section-title">不仅是视觉升级，更是整套诊断交互的重构</h2>
          <ul class="benefit-list">
            <li v-for="item in advantages" :key="item">{{ item }}</li>
          </ul>
        </div>

        <div class="disclaimer-card glass-card">
          <span class="panel-badge warning">使用提醒</span>
          <h3>本系统用于健康参考与辅助分析</h3>
          <p>
            舌象分析结果不应替代专业医师面诊、化验检查或正式医疗诊断。如存在明显不适或长期症状，请及时前往正规医疗机构就诊。
          </p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  gap: 32px;
  padding: 24px 0 48px;
}

.hero-shell {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(340px, 0.8fr);
  gap: 24px;
  padding: 32px;
}

.hero-copy,
.hero-panel,
.benefit-copy {
  padding: 28px;
}

.hero-copy {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.hero-primary,
.hero-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 46px;
  padding: 0 20px;
  border-radius: 999px;
  text-decoration: none;
  font-weight: 600;
}

.hero-primary {
  background: linear-gradient(135deg, var(--td-primary-600), var(--td-secondary-500));
  color: #fff;
  box-shadow: 0 14px 28px var(--td-primary-soft);
}

.hero-secondary {
  border: 1px solid var(--td-border-strong);
  background: var(--td-surface);
  color: var(--td-primary-700);
}

.hero-metrics,
.workflow-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.metric-card,
.disclaimer-card {
  padding: 20px;
  border-radius: 24px;
}

.metric-card strong,
.panel-item h3,
.workflow-card p,
.disclaimer-card h3 {
  color: var(--td-text-main);
}

.metric-card span,
.panel-item p,
.disclaimer-card p,
.benefit-list li {
  color: var(--td-text-secondary);
}

.panel-top,
.section-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.panel-label {
  margin: 0 0 8px;
  color: var(--td-primary-600);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
}

.panel-top h2 {
  margin: 0;
  font-size: 28px;
  line-height: 1.2;
}

.panel-badge {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  background: var(--td-primary-soft);
  color: var(--td-secondary-500);
  font-size: 12px;
  font-weight: 700;
}

.panel-badge.warning {
  background: rgba(229, 165, 51, 0.14);
  color: var(--td-warning-500);
}

.panel-list {
  display: grid;
  gap: 14px;
  margin-top: 20px;
}

.panel-item {
  padding: 18px;
  border-radius: 18px;
  background: var(--td-surface);
  border: 1px solid var(--td-border-color);
}

.panel-item h3 {
  margin: 0 0 8px;
}

.workflow-card {
  padding: 22px;
}

.workflow-index {
  display: inline-flex;
  margin-bottom: 14px;
  color: var(--td-accent-500);
  font-size: 24px;
  font-weight: 800;
}

.benefit-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 380px;
  gap: 24px;
}

.benefit-list {
  margin: 20px 0 0;
  padding-left: 18px;
}

.benefit-list li + li {
  margin-top: 12px;
}

@media (max-width: 1024px) {
  .hero-shell,
  .benefit-layout {
    grid-template-columns: 1fr;
  }

  .hero-metrics,
  .workflow-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .home-page {
    gap: 24px;
    padding-top: 16px;
  }

  .hero-shell,
  .hero-copy,
  .hero-panel,
  .benefit-copy {
    padding: 22px;
  }

  .panel-top,
  .section-head {
    flex-direction: column;
  }

  .hero-actions {
    flex-direction: column;
  }

  .hero-primary,
  .hero-secondary {
    width: 100%;
    margin-left: 0 !important;
  }
}
</style>
