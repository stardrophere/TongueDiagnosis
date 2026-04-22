<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()

const ctaTarget = computed(() => (authStore.isAuthenticated ? '/check' : '/register'))
const ctaLabel = computed(() => (authStore.isAuthenticated ? '进入工作台' : '免费开始使用'))

const features = [
  {
    icon: '✨',
    title: 'AI 驱动诊断',
    description: '上传舌象图片，毫秒级生成多维度的中医证候分析报告。'
  },
  {
    icon: '💬',
    title: '会话式追问',
    description: '不仅是结果呈现，更支持随时追问细节，获取深度健康指导。'
  },
  {
    icon: '📊',
    title: '云端档案',
    description: '所有诊断记录安全归档，轻松进行历史对比与病情复盘。'
  }
]
</script>

<template>
  <div class="premium-home">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-background">
        <div class="glow-orb primary"></div>
        <div class="glow-orb secondary"></div>
      </div>
      <div class="hero-content">
        <div class="badge">全新升级 2.0</div>
        <h1 class="main-title">
          懂你的<span class="gradient-text">中医 AI 助手</span>
        </h1>
        <p class="subtitle">
          将传统舌诊与先进人工智能相结合。提供上传即分析、结果可追问、记录可回看的一站式个人健康管理体验。
        </p>
        <div class="action-group">
          <router-link :to="ctaTarget" class="btn-premium">
            {{ ctaLabel }} <span class="arrow">→</span>
          </router-link>
          <a href="#features" class="btn-outline">
            了解详情
          </a>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="features-section">
      <div class="section-header">
        <h2 class="section-title">重塑舌诊体验</h2>
        <p class="section-desc">每一个细节，都为了更精准、更流畅的诊断过程。</p>
      </div>
      <div class="feature-grid">
        <div v-for="(item, idx) in features" :key="idx" class="feature-card">
          <div class="feature-icon">{{ item.icon }}</div>
          <h3 class="feature-title">{{ item.title }}</h3>
          <p class="feature-desc">{{ item.description }}</p>
        </div>
      </div>
    </section>

    <!-- Showcase / Workflow Section -->
    <section class="workflow-section">
      <div class="workflow-container">
        <div class="workflow-text">
          <h2>化繁为简，三步即达</h2>
          <ul class="step-list">
            <li>
              <div class="step-number">01</div>
              <div class="step-content">
                <h4>创建会话记录</h4>
                <p>为每一次诊断建立专属档案，方便日后回溯。</p>
              </div>
            </li>
            <li>
              <div class="step-number">02</div>
              <div class="step-content">
                <h4>上传舌象图片</h4>
                <p>一键上传，系统自动提取特征，生成分析报告。</p>
              </div>
            </li>
            <li>
              <div class="step-number">03</div>
              <div class="step-content">
                <h4>自由追问建议</h4>
                <p>针对体质、饮食、作息，向 AI 进一步获取调理方案。</p>
              </div>
            </li>
          </ul>
        </div>
        <div class="workflow-visual">
          <div class="mockup-card">
            <div class="mockup-header">
              <span class="dot red"></span>
              <span class="dot yellow"></span>
              <span class="dot green"></span>
            </div>
            <div class="mockup-body">
              <div class="mockup-chat">
                <div class="mockup-msg ai">正在分析您的舌象特征...</div>
                <div class="mockup-msg ai">
                  <strong>诊断结果</strong><br/>
                  舌色：淡红舌<br/>
                  舌苔：薄白苔<br/>
                  体质建议：建议保持规律作息...
                </div>
                <div class="mockup-msg user">这种体质适合吃什么？</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.premium-home {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  overflow-x: hidden;
  padding-bottom: 120px;
}

/* --- Hero Section --- */
.hero-section {
  position: relative;
  width: 100%;
  min-height: 85vh;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 120px 24px;
}

.hero-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: -1;
  pointer-events: none;
}

.glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
  animation: float 10s ease-in-out infinite alternate;
}

.glow-orb.primary {
  width: 50vw;
  height: 50vw;
  max-width: 600px;
  max-height: 600px;
  background: var(--td-primary-500);
  top: -10%;
  left: -10%;
}

.glow-orb.secondary {
  width: 40vw;
  height: 40vw;
  max-width: 500px;
  max-height: 500px;
  background: var(--td-secondary-500);
  bottom: 10%;
  right: -5%;
  animation-delay: -5s;
}

@keyframes float {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(30px, 50px) scale(1.1); }
}

.hero-content {
  max-width: 800px;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 1;
}

.badge {
  display: inline-flex;
  padding: 6px 16px;
  border-radius: 999px;
  background: var(--td-primary-soft);
  color: var(--td-primary-600);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.05em;
  margin-bottom: 32px;
  border: 1px solid rgba(31, 138, 112, 0.1);
}

.main-title {
  font-size: clamp(42px, 5vw, 68px);
  font-weight: 800;
  line-height: 1.15;
  color: var(--td-text-main);
  margin: 0 0 24px;
  letter-spacing: -0.02em;
}

.gradient-text {
  background: linear-gradient(135deg, var(--td-primary-600), var(--td-secondary-500));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: clamp(16px, 2vw, 20px);
  color: var(--td-text-secondary);
  line-height: 1.6;
  margin: 0 0 48px;
  max-width: 600px;
}

.action-group {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  justify-content: center;
}

.btn-premium, .btn-outline {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 56px;
  padding: 0 32px;
  border-radius: 28px;
  font-size: 16px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.btn-premium {
  background: var(--td-primary-500);
  color: #fff;
  box-shadow: 0 10px 24px rgba(31, 138, 112, 0.2);
}
.btn-premium:hover {
  transform: translateY(-2px);
  background: var(--td-primary-600);
  box-shadow: 0 14px 32px rgba(31, 138, 112, 0.3);
  color: #fff;
}
.btn-premium .arrow {
  margin-left: 8px;
  transition: transform 0.3s;
}
.btn-premium:hover .arrow {
  transform: translateX(4px);
}

.btn-outline {
  background: transparent;
  color: var(--td-text-main);
  border: 1px solid var(--td-border-strong);
}
.btn-outline:hover {
  background: var(--td-surface);
  border-color: var(--td-text-main);
}

/* --- Features Section --- */
.features-section {
  max-width: 1200px;
  width: 100%;
  padding: 0 24px;
  margin-bottom: 120px;
}

.section-header {
  text-align: center;
  margin-bottom: 64px;
}

.section-title {
  font-size: 36px;
  font-weight: 700;
  color: var(--td-text-main);
  margin: 0 0 16px;
}

.section-desc {
  font-size: 18px;
  color: var(--td-text-secondary);
  margin: 0;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.feature-card {
  background: var(--td-surface);
  border: 1px solid var(--td-border-color);
  border-radius: 24px;
  padding: 40px 32px;
  transition: all 0.3s ease;
}

.feature-card:hover {
  border-color: var(--td-primary-500);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.04);
  transform: translateY(-4px);
}

.feature-icon {
  font-size: 32px;
  margin-bottom: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: var(--td-primary-soft);
}

.feature-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--td-text-main);
  margin: 0 0 12px;
}

.feature-desc {
  font-size: 15px;
  color: var(--td-text-secondary);
  line-height: 1.6;
  margin: 0;
}

/* --- Workflow Section --- */
.workflow-section {
  max-width: 1200px;
  width: 100%;
  padding: 0 24px;
}

.workflow-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 64px;
  align-items: center;
  background: var(--td-panel-bg);
  border: 1px solid var(--td-border-color);
  border-radius: 32px;
  padding: 64px;
  box-shadow: var(--td-soft-shadow);
}

.workflow-text h2 {
  font-size: 36px;
  font-weight: 700;
  color: var(--td-text-main);
  margin: 0 0 48px;
}

.step-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.step-list li {
  display: flex;
  gap: 20px;
}

.step-number {
  font-size: 14px;
  font-weight: 700;
  color: var(--td-primary-600);
  background: var(--td-primary-soft);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.step-content h4 {
  font-size: 18px;
  font-weight: 600;
  color: var(--td-text-main);
  margin: 0 0 8px;
}

.step-content p {
  font-size: 15px;
  color: var(--td-text-secondary);
  margin: 0;
  line-height: 1.5;
}

.workflow-visual {
  display: flex;
  justify-content: center;
  perspective: 1000px;
}

.mockup-card {
  width: 100%;
  max-width: 380px;
  background: var(--td-surface);
  border: 1px solid var(--td-border-strong);
  border-radius: 20px;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transform: rotateY(-5deg) rotateX(5deg);
  transition: transform 0.5s ease;
}
.mockup-card:hover {
  transform: rotateY(0) rotateX(0);
}

.mockup-header {
  display: flex;
  gap: 8px;
  padding: 16px;
  border-bottom: 1px solid var(--td-border-color);
  background: var(--td-panel-bg);
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.dot.red { background: #ff5f56; }
.dot.yellow { background: #ffbd2e; }
.dot.green { background: #27c93f; }

.mockup-body {
  padding: 20px;
  background: var(--td-bg-main);
}

.mockup-chat {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mockup-msg {
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 13px;
  line-height: 1.5;
  max-width: 85%;
}

.mockup-msg.ai {
  background: var(--td-panel-strong);
  color: var(--td-text-main);
  border: 1px solid var(--td-border-color);
  align-self: flex-start;
  border-bottom-left-radius: 4px;
}

.mockup-msg.user {
  background: var(--td-primary-500);
  color: #fff;
  align-self: flex-end;
  border-bottom-right-radius: 4px;
}

@media (max-width: 900px) {
  .workflow-container {
    grid-template-columns: 1fr;
    padding: 40px 24px;
    gap: 48px;
  }
  .mockup-card {
    transform: none;
  }
}

@media (max-width: 600px) {
  .main-title {
    font-size: 36px;
  }
  .hero-section {
    min-height: 70vh;
    padding-top: 100px;
  }
  .action-group {
    flex-direction: column;
    width: 100%;
  }
  .btn-premium, .btn-outline {
    width: 100%;
  }
}
</style>