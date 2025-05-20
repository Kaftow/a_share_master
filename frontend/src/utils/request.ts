import axios from 'axios'
import type{ AxiosRequestConfig } from 'axios'

import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'


// 创建 axios 实例
const service = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})

service.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.status === 0) {
      return res.data
    } else {
      ElMessage.error(res.statusInfo.message || '请求失败')
      return Promise.reject(res)
    }
  },
  (error) => {
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

// 带 token 的请求封装
export function requestWithAuth<T = any>(config: AxiosRequestConfig): Promise<T> {
  const userStore = useUserStore()
  const token = userStore.token
  if (!token) {
    ElMessage.error('请先登录')
    return Promise.reject(new Error('缺少 token，拒绝请求'))
  }

  if (userStore.checkTokenExpired()) {
    ElMessage.error('登录状态已过期，请重新登录')
    return Promise.reject(new Error('Token expired'))
  }
  
  // 在请求头中添加 token
  config.headers = config.headers || {}
  config.headers['Authorization'] = `Bearer ${token}`

  return service(config)
}

// 不带 token 的请求
export function requestNoAuth<T = any>(config: AxiosRequestConfig): Promise<T> {
  return service(config)
}

