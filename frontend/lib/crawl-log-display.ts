/** Hiển thị crawl log thân thiện — parse message kiểu inserted=… từ backend. */

export type IngestStats = {
  inserted: number;
  updated: number;
  skipped?: number;
};

const INGEST_STATS_RE =
  /^inserted=(\d+),\s*updated=(\d+)(?:,\s*skipped=(\d+))?$/;

export function parseIngestStatsMessage(message: string | null | undefined): {
  stats: IngestStats | null;
  /** Nội dung khác (lỗi, thông báo tùy chỉnh) khi không khớp mẫu ingest. */
  freeText: string | null;
} {
  const raw = message?.trim();
  if (!raw) return { stats: null, freeText: null };
  const m = raw.match(INGEST_STATS_RE);
  if (!m) return { stats: null, freeText: raw };
  const stats: IngestStats = {
    inserted: Number(m[1]),
    updated: Number(m[2]),
  };
  if (m[3] !== undefined) stats.skipped = Number(m[3]);
  return { stats, freeText: null };
}

const CRAWL_TYPE_LABELS: Record<string, string> = {
  vietstock_list_price: "VietStock — lùi giá theo ngày (ListPrice)",
  vietstock_eod: "VietStock — giá phiên / EOD",
  price_json: "Nạp giá từ JSON (thủ công)",
};

export function labelCrawlType(crawlType: string): string {
  if (CRAWL_TYPE_LABELS[crawlType]) return CRAWL_TYPE_LABELS[crawlType];
  return crawlType.replace(/_/g, " ");
}

export type CrawlStatusTone = "success" | "failed" | "running" | "neutral";

export function crawlStatusPresentation(status: string): {
  label: string;
  tone: CrawlStatusTone;
} {
  const s = status.toLowerCase();
  if (s === "success")
    return { label: "Thành công", tone: "success" };
  if (s === "failed")
    return { label: "Thất bại", tone: "failed" };
  if (s === "running")
    return { label: "Đang chạy", tone: "running" };
  return { label: status, tone: "neutral" };
}
