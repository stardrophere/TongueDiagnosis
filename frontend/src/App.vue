<script setup>
import { onMounted } from 'vue'
import Header from '@/components/Header.vue'
import { useStateStore } from '@/stores/stateStore'

const stateStore = useStateStore()

onMounted(() => {
  stateStore.initTheme()
})
</script>

<template>
  <div class="app-shell">
    <Header />
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>
