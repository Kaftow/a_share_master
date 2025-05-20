<template>
  <el-form :model="form" label-width="80px" @submit.prevent="onSubmit">
    <el-form-item label="股票代码">
      <el-input
        v-model="form.symbol"
        placeholder="请输入股票代码"
        clearable
        @keyup.enter="onSubmit"
      />
    </el-form-item>

    <el-form-item>
      <el-button
        type="primary"
        :loading="loading"
        @click="onSubmit"
      >查询</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { StockInfoResponse, StockInfoRequest } from '@/types/stockInfo'
import { ElMessage } from 'element-plus'
import { getStockInfo } from '@/api/stock' 

const emits = defineEmits<{
  (e: 'search', stockInfo: StockInfoResponse): void
}>()

const form = ref({
  symbol: ''
})

const loading = ref(false)

// 查询触发事件，获取数据并传给父组件
async function onSubmit() {
  const sym = form.value.symbol.trim()
  if (!sym) return
  
  loading.value = true
  try {
    const request: StockInfoRequest = {
      stock_code: sym
    }
    
    const response = await getStockInfo(request)
    if (response && response.stock_code && response.info) {
      emits('search', response as StockInfoResponse)
    } else {
      throw new Error('返回的数据格式不正确')
    }
  } catch (error) {
    console.error('获取股票信息失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '获取股票信息失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>
