import { fetchJson } from "@/services/api-client";

export interface UserAdminRow {
  id: number;
  fullName: string;
  email: string;
  role: string;
  status: string;
}

export interface StockAdminRow {
  id: number;
  ticker: string;
  companyName: string;
  exchange: string;
  sector: string;
  isActive: boolean;
  crawlMetadata?: Record<string, unknown> | null;
}

export interface CrawlLogRow {
  id: number;
  stockId: number | null;
  crawlType: string;
  status: string;
  message: string | null;
  startedAt: string | null;
  finishedAt: string | null;
}

export async function adminListUsers(): Promise<UserAdminRow[]> {
  const res = await fetchJson<UserAdminRow[]>("/api/v1/admin/users");
  return res.data;
}

export async function adminPatchUser(
  userId: number,
  body: {
    fullName?: string;
    role?: "user" | "admin";
    status?: "active" | "inactive";
  },
): Promise<UserAdminRow> {
  const res = await fetchJson<UserAdminRow>(`/api/v1/admin/users/${userId}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
  return res.data;
}

export async function adminListStocks(): Promise<StockAdminRow[]> {
  const res = await fetchJson<StockAdminRow[]>("/api/v1/admin/stocks");
  return res.data;
}

export async function adminCreateStock(body: {
  ticker: string;
  companyName: string;
  exchange?: string;
  sector?: string;
  description?: string | null;
  crawlMetadata?: Record<string, unknown> | null;
}): Promise<StockAdminRow> {
  const res = await fetchJson<StockAdminRow>("/api/v1/admin/stocks", {
    method: "POST",
    body: JSON.stringify(body),
  });
  return res.data;
}

export async function adminPatchStock(
  ticker: string,
  body: {
    companyName?: string;
    crawlMetadata?: Record<string, unknown> | null;
  },
): Promise<StockAdminRow> {
  const res = await fetchJson<StockAdminRow>(
    `/api/v1/admin/stocks/${encodeURIComponent(ticker)}`,
    {
      method: "PATCH",
      body: JSON.stringify(body),
    },
  );
  return res.data;
}

export async function adminIngestPrices(
  ticker: string,
  data: unknown[],
): Promise<{
  inserted: number;
  updated: number;
  skipped: number;
  message?: string | null;
}> {
  const res = await fetchJson<{
    inserted: number;
    updated: number;
    skipped: number;
    message?: string | null;
  }>(`/api/v1/admin/crawl/${encodeURIComponent(ticker)}`, {
    method: "POST",
    body: JSON.stringify({ data }),
  });
  return res.data;
}

export async function adminCrawlVietstock(
  ticker: string,
  body: {
    cookie?: string | null;
    requestVerificationToken?: string | null;
    extraForm?: Record<string, string>;
  } = {},
): Promise<{
  inserted: number;
  updated: number;
  skipped: number;
  message?: string | null;
}> {
  const res = await fetchJson<{
    inserted: number;
    updated: number;
    skipped: number;
    message?: string | null;
  }>(`/api/v1/admin/crawl/vietstock/${encodeURIComponent(ticker)}`, {
    method: "POST",
    body: JSON.stringify({
      cookie: body.cookie ?? undefined,
      requestVerificationToken: body.requestVerificationToken ?? undefined,
      extraForm: body.extraForm,
    }),
  });
  return res.data;
}

export async function adminCrawlLogs(): Promise<CrawlLogRow[]> {
  const res = await fetchJson<CrawlLogRow[]>("/api/v1/admin/crawl/logs");
  return res.data;
}

export interface CrawlScheduleRow {
  id: number;
  stockId: number;
  ticker: string;
  companyName: string;
  isEnabled: boolean;
  intervalMinutes: number;
  nextRunAt: string | null;
  lastRunAt: string | null;
  lastRunStatus: string | null;
  lastRunMessage: string | null;
  hasVietstockCookie: boolean;
  hasRequestVerificationToken: boolean;
}

export async function adminListCrawlSchedules(): Promise<CrawlScheduleRow[]> {
  const res = await fetchJson<CrawlScheduleRow[]>("/api/v1/admin/crawl/schedules");
  return res.data;
}

export async function adminUpsertCrawlSchedule(
  ticker: string,
  body: {
    isEnabled?: boolean;
    intervalMinutes?: number;
    vietstockCookie?: string | null;
    requestVerificationToken?: string | null;
  },
): Promise<CrawlScheduleRow> {
  const res = await fetchJson<CrawlScheduleRow>(
    `/api/v1/admin/crawl/schedules/${encodeURIComponent(ticker)}`,
    {
      method: "PUT",
      body: JSON.stringify(body),
    },
  );
  return res.data;
}

export async function adminDeleteCrawlSchedule(ticker: string): Promise<void> {
  await fetchJson<{ ok: boolean }>(
    `/api/v1/admin/crawl/schedules/${encodeURIComponent(ticker)}`,
    { method: "DELETE" },
  );
}
