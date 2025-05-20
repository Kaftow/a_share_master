<template>
  <div ref="chartRef" style="width: 100%; height: 300px;"></div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import type { StockDailyResponse } from '@/types/stockDaily'
import { calculateMACD } from '@/utils/technicalIndicators.ts'

const props = defineProps<{
  stockDaily: StockDailyResponse | null
  adjustType: 'none' | 'qfq' | 'hfq'
}>()

const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null

function getAdjustedClose(data: StockDailyResponse['daily'], adjust: typeof props.adjustType): number[] {
  return data.map(item => {
    let factor = 1
    if (adjust === 'qfq') factor = item.qfq_factor
    else if (adjust === 'hfq') factor = item.hfq_factor
    return +(item.close * factor).toFixed(2)
  })
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
  const closePrices = getAdjustedClose(daily, props.adjustType)
  const { dif, dea, macd } = calculateMACD(closePrices)

  chartInstance.setOption({
    title: { text: `${props.stockDaily.stock_code} MACD` },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['DIF', 'DEA', 'MACD']
    },
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
        name: 'DIF',
        type: 'line',
        data: dif,
        smooth: true,
        lineStyle: { width: 1 }
      },
      {
        name: 'DEA',
        type: 'line',
        data: dea,
        smooth: true,
        lineStyle: { width: 1 }
      },
      {
        name: 'MACD',
        type: 'bar',
        data: macd.map(v => Math.abs(v)),
        itemStyle: {
          color: (params: any) => (macd[params.dataIndex] >= 0 ? '#f5222d' : '#52c41a')
        }
      }
    ]
  })
}

watch(() => [props.stockDaily, props.adjustType], () => {
  renderChart()
})

onMounted(() => {
  renderChart()
  window.addEventListener('resize', () => chartInstance?.resize())
})

onBeforeUnmount(() => {
  chartInstance?.dispose()
})
</script>
