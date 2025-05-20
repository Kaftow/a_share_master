<template>
  <div ref="chartRef" style="width: 100%; height: 400px;"></div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import type { StockDailyResponse } from '@/types/stockDaily'

const props = defineProps<{
  stockDaily: StockDailyResponse | null
  adjustType: 'none' | 'qfq' | 'hfq'
}>()

const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null

function formatKlineData(daily: StockDailyResponse['daily'], adjust: typeof props.adjustType) {
  if (!daily) return []
  return daily.map(item => {
    let factor = 1
    if (adjust === 'qfq') factor = item.qfq_factor
    else if (adjust === 'hfq') factor = item.hfq_factor

    const open = +(item.open * factor).toFixed(2)
    const close = +(item.close * factor).toFixed(2)
    const low = +(item.low * factor).toFixed(2)
    const high = +(item.high * factor).toFixed(2)

    return [item.date, [open, close, low, high]]
  })
}

function renderChart() {
  if (!chartRef.value) return
  if (!chartInstance) chartInstance = echarts.init(chartRef.value)
  if (!props.stockDaily) {
    chartInstance.clear()
    return
  }

  const klineData = formatKlineData(props.stockDaily.daily, props.adjustType)
  const dates = klineData.map(item => item[0])
  const values = klineData.map(item => item[1])

  chartInstance.setOption({
    title: { text: `${props.stockDaily.stock_code} 日线图` },
    xAxis: { type: 'category', data: dates, scale: true, boundaryGap: false },
    yAxis: { scale: true },
    dataZoom: [{ type: 'inside' }, { type: 'slider' }],
    series: [{
      type: 'candlestick',
      data: values,
      itemStyle: {
        color: '#ec0000',
        color0: '#00da3c',
        borderColor: '#8A0000',
        borderColor0: '#008F28',
      }
    }]
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
