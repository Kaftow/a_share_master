<template>
  <el-container style="width: 100vw; height: 100vh;">
    <Sidebar v-if="!collapsed" />
    <el-container>
      <el-header style="height: 64px; line-height: 64px; padding: 0;">
        <NavBar @toggle-collapse="toggleCollapse" />
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Sidebar from '@/components/Sidebar.vue'
import NavBar from '@/components/NavBar.vue'

const collapsed = ref(false)
function toggleCollapse() {
  collapsed.value = !collapsed.value
}
</script>

<style>

html, body, #app {
  margin: 0;
  padding: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}


.main-content {
  padding: 0;
  background-color: #f0f2f5;
  min-height: calc(100vh - 64px);
}
</style>
