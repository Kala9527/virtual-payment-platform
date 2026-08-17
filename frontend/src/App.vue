<template>
  <div class="app-shell">
    <SiteHeader />
    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import SiteHeader from './components/layout/SiteHeader.vue'
</script>

