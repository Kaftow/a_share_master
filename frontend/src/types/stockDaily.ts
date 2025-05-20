import type{ ISODateString } from '@/types/common';

export interface StockDailyRequest {
  stock_code: string;
  start_date?: ISODateString;
  end_date?: ISODateString;
}

export interface StockDailyResponseItem {
  date: ISODateString;
  open: number;
  high: number;
  low: number;
  close: number;
  change: number;
  pct_chg: number;
  vol: number;
  amount: number;
  qfq_factor: number;
  hfq_factor: number;
}

export interface StockDailyResponse {
  stock_code: string;
  data_count: number;
  start_date: ISODateString;
  end_date: ISODateString;
  daily: StockDailyResponseItem[];
}

