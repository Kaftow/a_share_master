<template>
  <el-card class="box-card" style="max-width: 700px; margin: 20px auto;">
    <template #header>
      <div class="clearfix">
        <span>股票基本信息查询</span>
      </div>
    </template>

    <!-- 查询参数输入组件 -->
    <stock-info-query @search="handleSearch" />

    <el-divider />

    <!-- 查询结果展示组件 -->
    <stock-info-display v-if="stockInfo" :info="stockInfo.info" />

    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      closable
      @close="error = null"
      style="margin-top: 10px;"
    />
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import StockInfoQuery from './StockInfoQuery.vue'
import StockInfoDisplay from './StockInfoDisplay.vue'
import type { StockInfoResponse } from '@/types/stockInfo'

const stockInfo = ref<StockInfoResponse | null>(null)
const error = ref<string | null>(null)

function handleSearch(response: StockInfoResponse) {
  stockInfo.value = response
  error.value = null
}
</script>

<style scoped>
.box-card {
  max-width: 700px;
}
</style>