export interface StockListItem {
  id: number;
  ticker: string;
  companyName: string;
  exchange: string;
  sector: string;
  isActive: boolean;
}

export interface StockDetail {
  id: number;
  ticker: string;
  companyName: string;
  exchange: string;
  sector: string;
  description: string | null;
  isActive: boolean;
}

export interface PriceBar {
  tradingDate: string;
  openPrice: number;
  highPrice: number;
  lowPrice: number;
  closePrice: number;
  totalVolume: number;
}

export interface KeyMetrics {
  metricDate: string | null;
  pe: number | null;
  pb: number | null;
  roe: number | null;
  roa: number | null;
  grossMargin: number | null;
  netMargin: number | null;
  debtToEquity: number | null;
  revenueGrowthYoy: number | null;
  profitGrowthYoy: number | null;
}

/** Từ GET /stocks/performance-board — tính từ lịch sử giá trong DB. */
export interface StockPerformanceRow {
  ticker: string;
  companyName: string;
  asOfDate: string | null;
  closePrice: number | null;
  pctDay: number | null;
  pctWeek: number | null;
  pctMonth: number | null;
  pctQuarter: number | null;
  pctYtd: number | null;
  pctYear: number | null;
}
