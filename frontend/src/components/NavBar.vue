<template>
  <div class="header-inner">
    <el-button
      icon="Menu"
      @click="$emit('toggle-collapse')"
      circle
      type="primary"
    />
    <span class="header-title">A股大王</span>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.header-inner {
  background-color: #409eff;
  color: white;
  display: flex;
  align-items: center;
  height: 64px;
  padding: 0 20px;
}
.header-title {
  margin-left: 16px;
  font-size: 18px;
  font-weight: 600;
}
</style>