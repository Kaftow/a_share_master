<template>
  <el-form :model="form" label-width="80px" @submit.prevent="onSubmit">
    <el-form-item label="股票代码">
      <el-input
        v-model="form.stock_code"
        placeholder="请输入股票代码"
        clearable
        @keyup.enter="onSubmit"
      />
    </el-form-item>

    <el-form-item label="开始日期">
      <el-date-picker
        v-model="form.start_date"
        type="date"
        placeholder="选择开始日期"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
        clearable
      />
    </el-form-item>

    <el-form-item label="结束日期">
      <el-date-picker
        v-model="form.end_date"
        type="date"
        placeholder="选择结束日期"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
        clearable
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
import type { StockDailyRequest, StockDailyResponse } from '@/types/stockDaily'
import { ElMessage } from 'element-plus'
import { getStockDaily } from '@/api/stock'

const emits = defineEmits<{
  (e: 'search', stockDailyData: StockDailyResponse): void
}>()

const form = ref<StockDailyRequest>({
  stock_code: '',
  start_date: undefined,
  end_date: undefined
})

const loading = ref(false)

async function onSubmit() {
  const symbol = form.value.stock_code.trim()
  if (!symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }

  // 简单校验开始和结束日期
  if (form.value.start_date && form.value.end_date) {
    if (form.value.start_date > form.value.end_date) {
      ElMessage.warning('开始日期不能晚于结束日期')
      return
    }
  }
  
  loading.value = true
  try {
    const request: StockDailyRequest = {
      stock_code: symbol,
      start_date: form.value.start_date,
      end_date: form.value.end_date,
    }

    const response = await getStockDaily(request)

    if (response && response.stock_code && response.daily) {
      emits('search', response)
    } else {
      throw new Error('返回数据格式不正确')
    }
  } catch (error) {
    console.error('获取股票日线数据失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '获取股票日线数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>
