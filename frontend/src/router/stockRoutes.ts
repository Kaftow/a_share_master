import type { RouteRecordRaw } from 'vue-router'
import StockInfo from '@/views/stock/info/StockInfo.vue'
import StockDaily from '@/views/stock/daily/StockDaily.vue'

const stockRoutes: RouteRecordRaw[] = [
  {
    path: '/stock/info',
    name: 'StockInfo',
    component: StockInfo,
    meta: { title: '股票基本信息', icon: 'DataLine' }
  },
  {
    path: '/stock/daily',
    name: 'StockDaily',
    component: StockDaily,
    meta: { title: '股票日线数据', icon: 'Stock' }
  },
]

export default stockRoutes
