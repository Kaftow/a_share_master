<template>
  <div>
    <el-radio-group v-model="adjustType" size="small" style="margin-bottom: 10px;">
      <el-radio-button label="none">未复权</el-radio-button>
      <el-radio-button label="qfq">前复权</el-radio-button>
      <el-radio-button label="hfq">后复权</el-radio-button>
    </el-radio-group>

    <el-radio-group v-model="chartType" size="small" style="margin-bottom: 10px;">
      <el-radio-button label="kline">日线</el-radio-button>
      <el-radio-button label="macd">MACD</el-radio-button>
      <el-radio-button label="kdj">KDJ</el-radio-button>
    </el-radio-group>

    <component
      :is="currentChartComponent"
      :stockDaily="stockDaily"
      :adjustType="adjustType"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { StockDailyResponse } from '@/types/stockDaily'

import KlineChart from './KlineChart.vue'
import MacdChart from './MacdChart.vue'
import KdjChart from './KdjChart.vue'

const props = defineProps<{
  stockDaily: StockDailyResponse | null
}>()

const adjustType = ref<'none' | 'qfq' | 'hfq'>('none')
const chartType = ref<'kline' | 'macd' | 'kdj'>('kline')

const currentChartComponent = computed(() => {
  switch (chartType.value) {
    case 'kline': return KlineChart
    case 'macd': return MacdChart
    case 'kdj': return KdjChart
    default: return KlineChart
  }
})
</script>
