import { requestWithAuth } from '@/utils/request'
import type {
    TradeCalendarRequest,
    ExchangeLastTradingDayRequest,
    TradeCalendarResponse,
    ExchangeLastTradingDayResponse
} from '@/types/tradeCalendar'

// 获取指定交易所的交易日历
export const getTradeCalendar = (data: TradeCalendarRequest): Promise<TradeCalendarResponse> => {
  return requestWithAuth<TradeCalendarResponse>({
    url: '/calendar/trading-days',
    method: 'POST',
    data
  })
}


// 获取指定交易所的最新交易日
export const getLatestTradingDay = (data: ExchangeLastTradingDayRequest): Promise<ExchangeLastTradingDayResponse> => {
  return requestWithAuth({
    url: '/calendar/latest-trading-day',
    method: 'POST',
    data
  })
}