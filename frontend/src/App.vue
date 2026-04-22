<script setup>
import Header from '@/components/Header.vue'
</script>

<template>
  <div class="app-shell">
    <Header />
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>
