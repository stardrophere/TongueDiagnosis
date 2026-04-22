import './assets/main.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

/**
 * 入口层只负责挂载应用与基础能力，
 * 鉴权与请求逻辑已迁移到 router / services 中统一管理。
 */
app.use(ElementPlus, {
  size: 'default',
  zIndex: 3000,
})
app.use(pinia)
app.use(router)
app.mount('#app')
