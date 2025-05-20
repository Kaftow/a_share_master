import { createRouter, createWebHistory } from 'vue-router'
import type{ RouteRecordRaw } from 'vue-router'
import Home from '@/views/Home.vue'
// 引入用户相关的路由
import userRoutes from '@/router/userRoutes'
// 引入股票相关的路由
import stockRoutes from '@/router/stockRoutes'


// 这里定义主路由
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: '首页', icon: 'House' }
  },
  ...userRoutes, 
  ...stockRoutes, // 引入股票相关的路由
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
