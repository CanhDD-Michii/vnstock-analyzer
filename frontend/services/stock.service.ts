import { fetchJson } from "@/services/api-client";
import type {
  KeyMetrics,
  PriceBar,
  StockDetail,
  StockListItem,
  StockPerformanceRow,
} from "@/types/stock";

export async function listStocks(): Promise<StockListItem[]> {
  const res = await fetchJson<StockListItem[]>("/api/v1/stocks/", undefined, {
    auth: false,
  });
  return res.data;
}

export async function listPerformanceBoard(
  limit = 100,
  priceLimit = 800,
): Promise<StockPerformanceRow[]> {
  const q = new URLSearchParams({
    limit: String(limit),
    price_limit: String(priceLimit),
  });
  const res = await fetchJson<StockPerformanceRow[]>(
    `/api/v1/stocks/performance-board?${q.toString()}`,
    undefined,
    { auth: false },
  );
  return res.data;
}

export async function getStockDetail(ticker: string): Promise<StockDetail> {
  const res = await fetchJson<StockDetail>(
    `/api/v1/stocks/${encodeURIComponent(ticker)}`,
    undefined,
    { auth: false },
  );
  return res.data;
}

export async function getStockPrices(
  ticker: string,
  limit = 500,
): Promise<PriceBar[]> {
  const res = await fetchJson<PriceBar[]>(
    `/api/v1/stocks/${encodeURIComponent(ticker)}/prices?limit=${limit}`,
    undefined,
    { auth: false },
  );
  return res.data;
}

export async function getStockMetrics(
  ticker: string,
): Promise<KeyMetrics | null> {
  const res = await fetchJson<KeyMetrics | null>(
    `/api/v1/stocks/${encodeURIComponent(ticker)}/metrics`,
    undefined,
    { auth: false },
  );
  return res.data;
}

export async function getStockTechnicals(
  ticker: string,
): Promise<Record<string, unknown>> {
  const res = await fetchJson<Record<string, unknown>>(
    `/api/v1/stocks/${encodeURIComponent(ticker)}/technicals`,
    undefined,
    { auth: false },
  );
  return res.data;
}
