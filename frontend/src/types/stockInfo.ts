import type { ISODateString, ISODateTimeString } from '@/types/common';

export interface Industry {
  ind_code: string;
  ind_name: string;
}

export interface StockInfoRequest {
  stock_code: string;
}

export interface StockInfoResponseItem {
  exchange_code: string;
  exchange_name: string;
  org_id?: string;
  org_name_cn?: string;
  org_short_name_cn?: string;
  org_name_en?: string;
  org_short_name_en?: string;
  main_operation_business?: string;
  operating_scope?: string;
  district_encode?: string;
  org_cn_introduction?: string;
  legal_representative?: string;
  general_manager?: string;
  secretary?: string;
  established_date?: ISODateString;
  reg_asset?: number;
  staff_num?: number;
  telephone?: string;
  postcode?: string;
  fax?: string;
  email?: string;
  org_website?: string;
  reg_address_cn?: string;
  office_address_cn?: string;
  currency_encode?: string;
  currency?: string;
  listed_date?: ISODateString;
  provincial_name?: string;
  actual_controller?: string;
  classi_name?: string;
  pre_name_cn?: string;
  chairman?: string;
  executives_nums?: number;
  actual_issue_vol?: number;
  issue_price?: number;
  actual_rc_net_amt?: number;
  pe_after_issuing?: number;
  online_success_rate_of_issue?: number;
  affiliate_industry?: Industry | null;
}

export interface StockInfoResponse {
  stock_code: string;
  updated_at: ISODateTimeString;
  info: StockInfoResponseItem;
}
