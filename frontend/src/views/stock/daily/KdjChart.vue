<template>
  <div ref="chartRef" style="width: 100%; height: 300px;"></div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import type { StockDailyResponse } from '@/types/stockDaily'
import { calculateKDJ } from '@/utils/technicalIndicators'

const props = defineProps<{
  stockDaily: StockDailyResponse | null
  adjustType: 'none' | 'qfq' | 'hfq'
}>()

const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null

function getAdjustedData(data: StockDailyResponse['daily'], adjust: typeof props.adjustType) {
  return {
    highPrices: data.map(item => {
      let factor = 1
      if (adjust === 'qfq') factor = item.qfq_factor
      else if (adjust === 'hfq') factor = item.hfq_factor
      return +(item.high * factor).toFixed(2)
    }),
    lowPrices: data.map(item => {
      let factor = 1
      if (adjust === 'qfq') factor = item.qfq_factor
      else if (adjust === 'hfq') factor = item.hfq_factor
      return +(item.low * factor).toFixed(2)
    }),
    closePrices: data.map(item => {
      let factor = 1
      if (adjust === 'qfq') factor = item.qfq_factor
      else if (adjust === 'hfq') factor = item.hfq_factor
      return +(item.close * factor).toFixed(2)
    }),
  }
}

function renderChart() {
  if (!chartRef.value) return
  if (!chartInstance) chartInstance = echarts.init(chartRef.value)

  if (!props.stockDaily) {
    chartInstance.clear()
    return
  }

  const daily = props.stockDaily.daily
  const dates = daily.map(item => item.date)
  const { highPrices, lowPrices, closePrices } = getAdjustedData(daily, props.adjustType)
  const { k, d, j } = calculateKDJ(highPrices, lowPrices, closePrices)

  chartInstance.setOption({
    title: { text: `${props.stockDaily.stock_code} KDJ` },
    tooltip: { trigger: 'axis' },
    legend: { data: ['K', 'D', 'J'] },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: 'K',
        type: 'line',
        data: k,
        smooth: true,
        lineStyle: { width: 1 }
      },
      {
        name: 'D',
        type: 'line',
        data: d,
        smooth: true,
        lineStyle: { width: 1 }
      },
      {
        name: 'J',
        type: 'line',
        data: j,
        smooth: true,
        lineStyle: { width: 1 }
      }
    ]
  }, true) // 传 true 强制不合并，重新渲染
}

watch(
  () => [props.stockDaily, props.adjustType],
  () => {
    renderChart()
  },
  { immediate: true }
)

onMounted(() => {
  window.addEventListener('resize', () => chartInstance?.resize())
})

onBeforeUnmount(() => {
  chartInstance?.dispose()
})
</script>
