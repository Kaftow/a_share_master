import { requestWithAuth } from '@/utils/request'
import type { StockDailyRequest, StockDailyResponse } from '@/types/stockDaily'
import type { StockInfoRequest, StockInfoResponse } from '@/types/stockInfo'

// 获取股票日线数据
export const getStockDaily = (data: StockDailyRequest): Promise<StockDailyResponse> => {
  return requestWithAuth<StockDailyResponse>({
    url: '/stock/daily',
    method: 'POST',
    data
  })
}

// 获取股票基本信息
export const getStockInfo = (data: StockInfoRequest): Promise<StockInfoResponse> => {
  return requestWithAuth<StockInfoResponse>({
    url: '/stock/info',
    method: 'POST',
    data
  })
}

