<template>
  <el-card class="box-card" style="max-width: 900px; margin: 20px auto;">
    <template #header>
      <div class="clearfix">
        <span>股票日线数据查询</span>
      </div>
    </template>

    <!-- 查询参数输入组件 -->
    <stock-daily-query @search="handleSearch" />

    <el-divider />

    <!-- 错误提示 -->
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      closable
      @close="error = null"
      style="margin-bottom: 10px;"
    />

    <!-- 查询结果展示组件 -->
    <stock-daily-display
      v-if="stockDaily"
      :stockDaily="stockDaily"
    />
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import StockDailyQuery from './StockDailyQuery.vue'
import StockDailyDisplay from './StockDailyDisplay.vue'
import type { StockDailyResponse } from '@/types/stockDaily'

const stockDaily = ref<StockDailyResponse | null>(null)
const error = ref<string | null>(null)

function handleSearch(response: StockDailyResponse) {
  stockDaily.value = response
  error.value = null
}
</script>

<style scoped>
.box-card {
  max-width: 900px;
}
</style>
