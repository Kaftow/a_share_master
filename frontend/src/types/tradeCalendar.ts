import type { ISODateString } from '@/types/common';

export type ExchangeCode = 'SH' | 'SZ' | 'BJ';

export interface TradeCalendarRequest {
  exchange_code: ExchangeCode;
  start_date?: ISODateString;
  end_date?: ISODateString;
}

export interface ExchangeLastTradingDayRequest {
  exchange_code: ExchangeCode;
}

export interface TradeCalendarResponse {
  exchange_code: ExchangeCode;
  trade_dates: ISODateString[];
  total_count: number;
  first_trade_date: ISODateString;
  last_trade_date: ISODateString;
}

export interface ExchangeLastTradingDayResponse {
  exchange_code: ExchangeCode;
  last_trading_day: ISODateString;
}
