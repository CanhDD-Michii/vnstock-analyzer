"use client";

import { ChevronRight, Loader2 } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { PageShell } from "@/components/common/PageShell";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { SectionCard } from "@/components/ui/SectionCard";
import { ROUTES } from "@/constants/routes";
import { ADMIN_DEFAULT_STOCK_TICKER, createDefaultVietstockCrawlMetadata } from "@/constants/vietstock-defaults";
import { useAuth } from "@/hooks/useAuth";
import {
  crawlStatusPresentation,
  labelCrawlType,
  parseIngestStatsMessage,
} from "@/lib/crawl-log-display";
import * as adminApi from "@/services/admin.service";

const PAGE_TITLE = "Quản lý mã chứng khoán";

/** localStorage — chỉ máy này; cookie/token nhạy cảm, tránh XSS. */
const VIETSTOCK_LS_COOKIE_KEY = "vnstock-analyzer.vietstock-manual-crawl.cookie";
const VIETSTOCK_LS_TOKEN_KEY = "vnstock-analyzer.vietstock-manual-crawl.token";

const VIETSTOCK_CRAWL_PROGRESS_HINTS = [
  "Đang crawl — server đang gọi VietStock (ListPrice) và có thể lùi nhiều ngày theo metadata.",
  "Vẫn đang chạy — với lịch sử dài, một lần crawl có thể mất vài phút; vui lòng không đóng trang.",
  "Nếu quá lâu: kiểm tra cookie và __RequestVerificationToken còn khớp phiên trình duyệt trên VietStock.",
] as const;

/** Mẫu đúng POST /api/v1/admin/crawl/{ticker} — body `{ data: [...] }`, từng phần tử qua `normalize_price_row` (backend). */
const INGEST_PRICE_JSON_EXAMPLE = `{
  "data": [
    {
      "TradingDate": "2024-12-23",
      "OpenPrice": 52.3,
      "HighestPrice": 53.1,
      "LowestPrice": 52.0,
      "ClosePrice": 52.8,
      "TotalVol": 15420000,
      "Change": 0.5,
      "PerChange": 0.96
    },
    {
      "TradingDate": "/Date(1734998400000)/",
      "OpenPrice": 52.8,
      "HighestPrice": 53.4,
      "LowestPrice": 51.9,
      "ClosePrice": 52.15,
      "TotalVol": 12035000,
      "Change": -0.65,
      "PerChange": -1.23
    },
    {
      "trading_date": "2024-12-25",
      "open_price": 52.0,
      "high_price": 52.6,
      "low_price": 51.4,
      "close_price": 52.35,
      "volume": 9850000
    }
  ]
}`;

function isRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === "object" && v !== null && !Array.isArray(v);
}

export default function StockSymbolManagementPage() {
  const { user, loading } = useAuth();
  const [stocks, setStocks] = useState<adminApi.StockAdminRow[]>([]);
  const [logs, setLogs] = useState<adminApi.CrawlLogRow[]>([]);
  const [jsonText, setJsonText] = useState(INGEST_PRICE_JSON_EXAMPLE);
  const [ticker, setTicker] = useState(ADMIN_DEFAULT_STOCK_TICKER);
  const [crawlTicker, setCrawlTicker] = useState(ADMIN_DEFAULT_STOCK_TICKER);
  const [metaJson, setMetaJson] = useState(() =>
    JSON.stringify(createDefaultVietstockCrawlMetadata(), null, 2),
  );
  const [vsTimeFrame, setVsTimeFrame] = useState("C");
  const [vsListPageSize, setVsListPageSize] = useState("20");
  const [vsLanguageId, setVsLanguageId] = useState("1");
  const [vsListToDate, setVsListToDate] = useState("");
  const [vsCookie, setVsCookie] = useState("");
  const [vsToken, setVsToken] = useState("");
  const [persistedVietstockSecrets, setPersistedVietstockSecrets] = useState({
    cookie: "",
    token: "",
  });
  const [crawlLocalStoragePromptOpen, setCrawlLocalStoragePromptOpen] = useState(false);
  const [newTicker, setNewTicker] = useState("");
  const [newCompany, setNewCompany] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [schedules, setSchedules] = useState<adminApi.CrawlScheduleRow[]>([]);
  const [schedTicker, setSchedTicker] = useState("");
  const [schedInterval, setSchedInterval] = useState(1440);
  const [schedEnabled, setSchedEnabled] = useState(true);
  const [schedCookie, setSchedCookie] = useState("");
  const [schedToken, setSchedToken] = useState("");
  const [schedSaving, setSchedSaving] = useState(false);
  const [scheduleDeleteTicker, setScheduleDeleteTicker] = useState<string | null>(null);
  const [clearSecretsDialogOpen, setClearSecretsDialogOpen] = useState(false);
  const [confirmDialogBusy, setConfirmDialogBusy] = useState(false);
  const [vietstockCrawling, setVietstockCrawling] = useState(false);
  const [crawlProgressStep, setCrawlProgressStep] = useState(0);

  const refreshData = useCallback(async () => {
    const [s, l, sch] = await Promise.all([
      adminApi.adminListStocks(),
      adminApi.adminCrawlLogs(),
      adminApi.adminListCrawlSchedules(),
    ]);
    setStocks(s);
    setLogs(l);
    setSchedules(sch);
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const cookie = localStorage.getItem(VIETSTOCK_LS_COOKIE_KEY) ?? "";
      const token = localStorage.getItem(VIETSTOCK_LS_TOKEN_KEY) ?? "";
      setVsCookie(cookie);
      setVsToken(token);
      setPersistedVietstockSecrets({ cookie, token });
    } catch {
      /* private mode / chặn storage */
    }
  }, []);

  useEffect(() => {
    if (loading || user?.role !== "admin") return;
    void (async () => {
      try {
        await refreshData();
      } catch (e: unknown) {
        setErr(e instanceof Error ? e.message : "Không tải dữ liệu");
      }
    })();
  }, [user, loading, refreshData]);

  const applyMetaFromStock = useCallback(
    (t: string, list: adminApi.StockAdminRow[]) => {
      const row = list.find((x) => x.ticker === t);
      if (row?.crawlMetadata && isRecord(row.crawlMetadata)) {
        setMetaJson(JSON.stringify(row.crawlMetadata, null, 2));
      } else {
        setMetaJson(JSON.stringify(createDefaultVietstockCrawlMetadata(), null, 2));
      }
      const form = row?.crawlMetadata && isRecord(row.crawlMetadata) ? row.crawlMetadata.form : null;
      if (isRecord(form)) {
        if (typeof form.timeFrame === "string") setVsTimeFrame(form.timeFrame);
        if (typeof form.pageSize === "string" || typeof form.pageSize === "number")
          setVsListPageSize(String(form.pageSize));
        if (typeof form.languageID === "string" || typeof form.languageID === "number")
          setVsLanguageId(String(form.languageID));
        if (typeof form.toDate === "string") setVsListToDate(form.toDate);
        else setVsListToDate("");
      }
    },
    [],
  );

  useEffect(() => {
    if (stocks.length === 0) return;
    if (!stocks.some((s) => s.ticker === crawlTicker)) {
      setCrawlTicker(stocks[0]!.ticker);
      return;
    }
    applyMetaFromStock(crawlTicker, stocks);
  }, [crawlTicker, stocks, applyMetaFromStock]);

  useEffect(() => {
    if (stocks.length === 0) return;
    setSchedTicker((prev) => {
      if (prev && stocks.some((s) => s.ticker === prev)) return prev;
      return stocks[0]!.ticker;
    });
  }, [stocks]);

  function formatScheduleDt(iso: string | null): string {
    if (!iso) return "—";
    try {
      return new Date(iso).toLocaleString("vi-VN", { timeZone: "Asia/Ho_Chi_Minh" });
    } catch {
      return iso;
    }
  }

  const tickerByStockId = useMemo(() => {
    const m = new Map<number, string>();
    for (const s of stocks) m.set(s.id, s.ticker);
    return m;
  }, [stocks]);

  function statusBadgeClass(tone: ReturnType<typeof crawlStatusPresentation>["tone"]): string {
    switch (tone) {
      case "success":
        return "bg-emerald-500/15 text-emerald-800 ring-1 ring-emerald-500/25 dark:text-emerald-300 dark:ring-emerald-400/20";
      case "failed":
        return "bg-red-500/15 text-red-800 ring-1 ring-red-500/25 dark:text-red-300 dark:ring-red-400/20";
      case "running":
        return "bg-amber-500/15 text-amber-900 ring-1 ring-amber-500/25 dark:text-amber-200 dark:ring-amber-400/20";
      default:
        return "bg-zinc-500/10 text-zinc-700 ring-1 ring-zinc-500/15 dark:text-zinc-300 dark:ring-zinc-500/20";
    }
  }

  async function onSaveSchedule() {
    setMsg(null);
    setErr(null);
    const t = schedTicker.trim().toUpperCase();
    if (!t || !stocks.some((s) => s.ticker === t)) {
      setErr("Chọn mã hợp lệ.");
      return;
    }
    setSchedSaving(true);
    try {
      const body: Parameters<typeof adminApi.adminUpsertCrawlSchedule>[1] = {
        isEnabled: schedEnabled,
        intervalMinutes: schedInterval,
      };
      if (schedCookie.trim()) body.vietstockCookie = schedCookie.trim();
      if (schedToken.trim()) body.requestVerificationToken = schedToken.trim();
      await adminApi.adminUpsertCrawlSchedule(t, body);
      setMsg(`Đã lưu lịch crawl cho ${t}.`);
      setSchedCookie("");
      setSchedToken("");
      await refreshData();
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "Lưu lịch thất bại");
    } finally {
      setSchedSaving(false);
    }
  }

  function openClearSecretsDialog() {
    setErr(null);
    const t = schedTicker.trim().toUpperCase();
    if (!t) {
      setErr("Chọn mã trước khi gỡ cookie/token.");
      return;
    }
    setClearSecretsDialogOpen(true);
  }

  async function confirmClearScheduleSecrets() {
    const t = schedTicker.trim().toUpperCase();
    if (!t) {
      setClearSecretsDialogOpen(false);
      return;
    }
    setMsg(null);
    setErr(null);
    setConfirmDialogBusy(true);
    try {
      await adminApi.adminUpsertCrawlSchedule(t, {
        isEnabled: schedEnabled,
        intervalMinutes: schedInterval,
        vietstockCookie: null,
        requestVerificationToken: null,
      });
      setMsg(`Đã gỡ cookie/token lịch cho ${t}.`);
      await refreshData();
      setClearSecretsDialogOpen(false);
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "Thao tác thất bại");
    } finally {
      setConfirmDialogBusy(false);
    }
  }

  async function confirmDeleteSchedule() {
    if (!scheduleDeleteTicker) return;
    setMsg(null);
    setErr(null);
    setConfirmDialogBusy(true);
    try {
      await adminApi.adminDeleteCrawlSchedule(scheduleDeleteTicker);
      setMsg(`Đã xóa lịch ${scheduleDeleteTicker}.`);
      await refreshData();
      setScheduleDeleteTicker(null);
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "Xóa lịch thất bại");
    } finally {
      setConfirmDialogBusy(false);
    }
  }

  function loadScheduleIntoForm(row: adminApi.CrawlScheduleRow) {
    setSchedTicker(row.ticker);
    setSchedInterval(row.intervalMinutes);
    setSchedEnabled(row.isEnabled);
    setSchedCookie("");
    setSchedToken("");
  }

  async function onIngest() {
    setMsg(null);
    setErr(null);
    try {
      const body = JSON.parse(jsonText) as { data?: unknown[] };
      const rows = Array.isArray(body.data) ? body.data : [];
      const res = await adminApi.adminIngestPrices(ticker, rows);
      setMsg(
        `OK: inserted=${res.inserted}, updated=${res.updated}, skipped=${res.skipped}`,
      );
      setLogs(await adminApi.adminCrawlLogs());
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "Ingest thất bại");
    }
  }

  async function onSaveMetadata() {
    setMsg(null);
    setErr(null);
    if (!stocks.some((s) => s.ticker === crawlTicker)) {
      setErr("Chưa có mã để lưu — tạo mã hoặc đợi tải danh sách.");
      return;
    }
    try {
      const meta = JSON.parse(metaJson) as Record<string, unknown>;
      if (!isRecord(meta)) throw new Error("Metadata phải là object JSON");
      await adminApi.adminPatchStock(crawlTicker, { crawlMetadata: meta });
      setMsg("Đã lưu crawlMetadata cho mã.");
      await refreshData();
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "Lưu metadata thất bại");
    }
  }

  function onMergeListPriceFormIntoJson() {
    setMsg(null);
    setErr(null);
    if (!crawlTicker.trim()) {
      setErr("Chọn mã trước khi gộp form.");
      return;
    }
    try {
      const cur = JSON.parse(metaJson) as Record<string, unknown>;
      if (!isRecord(cur)) throw new Error("JSON hiện tại phải là object");
      const n = parseInt(vsListPageSize, 10);
      const pageSize = Number.isFinite(n) ? Math.min(20, Math.max(1, n)) : 20;
      const nextForm: Record<string, string> = {
        stockCode: crawlTicker,
        timeFrame: (vsTimeFrame.trim() || "C").toUpperCase(),
        page: "1",
        pageSize: String(pageSize),
        languageID: (vsLanguageId.trim() || "1").trim(),
      };
      if (vsListToDate.trim()) nextForm.toDate = vsListToDate.trim();
      cur.form = nextForm;
      setMetaJson(JSON.stringify(cur, null, 2));
      setMsg(
        `Đã ghi đúng field POST: stockCode, timeFrame, page, pageSize, languageID` +
          (vsListToDate.trim() ? ", toDate" : "") +
          ` (token gửi kèm khi crawl, không lưu trong form).`,
      );
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "Không gộp được form crawl");
    }
  }

  function vietstockSecretsDifferFromPersisted(): boolean {
    return (
      vsCookie !== persistedVietstockSecrets.cookie ||
      vsToken !== persistedVietstockSecrets.token
    );
  }

  function onCrawlVietstockClick() {
    setMsg(null);
    setErr(null);
    if (!stocks.some((s) => s.ticker === crawlTicker)) {
      setErr("Chưa có mã để crawl.");
      return;
    }
    if (vietstockSecretsDifferFromPersisted()) {
      setCrawlLocalStoragePromptOpen(true);
      return;
    }
    void executeVietstockCrawl();
  }

  function onCrawlPersistSaveAndRun() {
    try {
      localStorage.setItem(VIETSTOCK_LS_COOKIE_KEY, vsCookie);
      localStorage.setItem(VIETSTOCK_LS_TOKEN_KEY, vsToken);
    } catch {
      setErr(
        "Không ghi được localStorage. Bạn có thể chọn «Chỉ crawl» hoặc kiểm tra chế độ riêng tư / dung lượng trình duyệt.",
      );
      return;
    }
    setErr(null);
    setPersistedVietstockSecrets({ cookie: vsCookie, token: vsToken });
    setCrawlLocalStoragePromptOpen(false);
    void executeVietstockCrawl();
  }

  function onCrawlPersistSkipAndRun() {
    setErr(null);
    setPersistedVietstockSecrets({ cookie: vsCookie, token: vsToken });
    setCrawlLocalStoragePromptOpen(false);
    void executeVietstockCrawl();
  }

  async function executeVietstockCrawl() {
    setVietstockCrawling(true);
    setCrawlProgressStep(0);
    const progressTimer = window.setInterval(() => {
      setCrawlProgressStep((s) =>
        Math.min(s + 1, VIETSTOCK_CRAWL_PROGRESS_HINTS.length - 1),
      );
    }, 12000);
    try {
      const res = await adminApi.adminCrawlVietstock(crawlTicker, {
        cookie: vsCookie.trim() || undefined,
        requestVerificationToken: vsToken.trim() || undefined,
      });
      setMsg(
        `VietStock hoàn tất (${crawlTicker}): thêm ${res.inserted}, cập nhật ${res.updated}, bỏ qua ${res.skipped}.`,
      );
      setLogs(await adminApi.adminCrawlLogs());
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "Crawl VietStock thất bại");
    } finally {
      window.clearInterval(progressTimer);
      setVietstockCrawling(false);
      setCrawlProgressStep(0);
    }
  }

  async function onCreateStock() {
    setMsg(null);
    setErr(null);
    const t = newTicker.trim().toUpperCase();
    const cn = newCompany.trim();
    if (!t || !cn) {
      setErr("Ticker và tên công ty là bắt buộc.");
      return;
    }
    try {
      let meta: Record<string, unknown> | undefined;
      try {
        const parsed = JSON.parse(metaJson) as unknown;
        if (isRecord(parsed)) meta = parsed;
      } catch {
        meta = undefined;
      }
      await adminApi.adminCreateStock({
        ticker: t,
        companyName: cn,
        exchange: "HOSE",
        sector: "",
        crawlMetadata: meta,
      });
      setNewTicker("");
      setNewCompany("");
      setMsg(`Đã tạo mã ${t}.`);
      await refreshData();
      setCrawlTicker(t);
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "Tạo mã thất bại");
    }
  }

  if (loading) {
    return (
      <PageShell title={PAGE_TITLE} description="Tải dữ liệu quản trị…">
        <p className="text-sm text-zinc-500">Đang tải…</p>
      </PageShell>
    );
  }

  if (user?.role !== "admin") {
    return (
      <PageShell title={PAGE_TITLE} description="Chỉ tài khoản admin mới truy cập được trang này.">
        <p className="rounded-xl border border-zinc-200 bg-zinc-50/90 px-4 py-3 text-sm text-zinc-700 dark:border-zinc-700 dark:bg-zinc-900/50 dark:text-zinc-300">
          Bạn không có quyền truy cập trang này.
        </p>
      </PageShell>
    );
  }

  return (
    <PageShell
      title={PAGE_TITLE}
      description="Crawl giá từng mã (VietStock ListPrice), metadata, ingest JSON — vận hành dữ liệu."
    >
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <Link
          href={ROUTES.adminUsers}
          className="inline-flex items-center gap-1 text-sm font-medium text-emerald-700 hover:text-emerald-800 dark:text-emerald-400"
        >
          Quản lý người dùng
          <ChevronRight className="h-4 w-4 shrink-0" strokeWidth={2} aria-hidden />
        </Link>
      </div>
      <SectionCard title="Crawl logs (gần nhất)">
        <p className="mb-3 text-xs leading-relaxed text-zinc-500 dark:text-zinc-400">
          <span className="font-medium text-zinc-600 dark:text-zinc-300">Thêm mới</span>: bản ghi ngày giao dịch mới.{" "}
          <span className="font-medium text-zinc-600 dark:text-zinc-300">Cập nhật</span>: đã có ngày đó, OHLCV thay đổi.{" "}
          <span className="font-medium text-zinc-600 dark:text-zinc-300">Bỏ qua</span>: trùng ngày, dữ liệu không đổi.
        </p>
        <div className="max-h-80 space-y-2 overflow-auto pr-0.5">
          {logs.length === 0 ? (
            <p className="text-xs text-zinc-500">Chưa có log.</p>
          ) : (
            logs.map((l) => {
              const { stats, freeText } = parseIngestStatsMessage(l.message);
              const st = crawlStatusPresentation(l.status);
              const when = l.finishedAt ?? l.startedAt;
              const ticker =
                l.stockId != null ? (tickerByStockId.get(l.stockId) ?? `#${l.stockId}`) : "—";
              return (
                <div
                  key={l.id}
                  className="rounded-xl border border-zinc-200/90 bg-zinc-50/80 px-3 py-2.5 dark:border-zinc-800 dark:bg-zinc-900/40"
                >
                  <div className="flex flex-wrap items-center gap-2 gap-y-1.5">
                    <time
                      className="text-[11px] font-medium tabular-nums text-zinc-500 dark:text-zinc-400"
                      dateTime={when ?? undefined}
                      title={when ?? undefined}
                    >
                      {formatScheduleDt(when)}
                    </time>
                    <span className="rounded-md bg-white px-1.5 py-0.5 font-mono text-[11px] font-semibold text-zinc-800 shadow-sm dark:bg-zinc-950 dark:text-zinc-200">
                      {ticker}
                    </span>
                    <span
                      className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${statusBadgeClass(st.tone)}`}
                    >
                      {st.label}
                    </span>
                  </div>
                  <p className="mt-1.5 text-xs font-medium leading-snug text-zinc-800 dark:text-zinc-200">
                    {labelCrawlType(l.crawlType)}
                  </p>
                  {stats ? (
                    <ul className="mt-2 flex flex-wrap gap-1.5">
                      <li>
                        <span className="inline-flex items-center gap-1 rounded-lg bg-emerald-500/10 px-2 py-1 text-[11px] text-emerald-900 dark:text-emerald-200">
                          <span className="text-zinc-600 dark:text-zinc-400">Thêm mới</span>
                          <span className="font-semibold tabular-nums">{stats.inserted}</span>
                        </span>
                      </li>
                      <li>
                        <span className="inline-flex items-center gap-1 rounded-lg bg-sky-500/10 px-2 py-1 text-[11px] text-sky-900 dark:text-sky-200">
                          <span className="text-zinc-600 dark:text-zinc-400">Cập nhật</span>
                          <span className="font-semibold tabular-nums">{stats.updated}</span>
                        </span>
                      </li>
                      {stats.skipped !== undefined ? (
                        <li>
                          <span className="inline-flex items-center gap-1 rounded-lg bg-zinc-500/10 px-2 py-1 text-[11px] text-zinc-800 dark:text-zinc-200">
                            <span className="text-zinc-600 dark:text-zinc-400">Bỏ qua</span>
                            <span className="font-semibold tabular-nums">{stats.skipped}</span>
                          </span>
                        </li>
                      ) : null}
                    </ul>
                  ) : freeText ? (
                    <p
                      className={
                        st.tone === "failed"
                          ? "mt-2 whitespace-pre-wrap break-words font-mono text-[11px] leading-relaxed text-red-700 dark:text-red-300"
                          : "mt-2 whitespace-pre-wrap break-words font-mono text-[11px] leading-relaxed text-zinc-600 dark:text-zinc-400"
                      }
                    >
                      {freeText}
                    </p>
                  ) : null}
                </div>
              );
            })
          )}
        </div>
      </SectionCard>

      <SectionCard title="Lịch crawl tự động (VietStock)">
        <p className="mb-3 text-xs leading-relaxed text-zinc-600 dark:text-zinc-400">
          Lịch lưu trong bảng <code className="rounded bg-zinc-100 px-1 dark:bg-zinc-800">crawl_schedules</code>. Tiến trình
          nền kiểm tra mỗi ~30 giây; tới <span className="font-medium">nextRunAt</span> sẽ gọi cùng luồng VietStock như nút
          crawl thủ công. <span className="font-medium">crawlMetadata</span> trên mã là tuỳ chọn (thiếu thì backend dùng URL/strategy
          mặc định); cookie/token có thể lưu
          riêng cho lịch (không trả về API, chỉ báo đã cấu hình). Dữ liệu giá: ngày đã có chỉ{" "}
          <span className="font-medium">cập nhật khi OHLCV đổi</span>, không thêm dòng trùng ngày; log ghi{" "}
          <code className="rounded bg-zinc-100 px-0.5 dark:bg-zinc-800">skipped</code> khi không đổi.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px] border-collapse text-xs">
            <thead>
              <tr className="border-b border-zinc-200 text-left font-semibold text-zinc-600 dark:border-zinc-700 dark:text-zinc-400">
                <th className="py-2 pr-2">Mã</th>
                <th className="py-2 pr-2">Phút</th>
                <th className="py-2 pr-2">Bật</th>
                <th className="py-2 pr-2">Chạy tiếp (HCM)</th>
                <th className="py-2 pr-2">Lần cuối / Trạng thái</th>
                <th className="py-2 pr-2">Bí mật</th>
                <th className="py-2"> </th>
              </tr>
            </thead>
            <tbody>
              {schedules.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-4 text-zinc-500">
                    Chưa có lịch — tạo bên dưới.
                  </td>
                </tr>
              ) : (
                schedules.map((sc) => (
                  <tr key={sc.id} className="border-b border-zinc-100 dark:border-zinc-800/80">
                    <td className="py-2 pr-2 font-semibold">{sc.ticker}</td>
                    <td className="py-2 pr-2 tabular-nums">{sc.intervalMinutes}</td>
                    <td className="py-2 pr-2">{sc.isEnabled ? "Có" : "Không"}</td>
                    <td className="py-2 pr-2">{formatScheduleDt(sc.nextRunAt)}</td>
                    <td className="py-2 pr-2">
                      <span className={sc.lastRunStatus === "failed" ? "text-red-600 dark:text-red-400" : ""}>
                        {formatScheduleDt(sc.lastRunAt)} {sc.lastRunStatus ? `· ${sc.lastRunStatus}` : ""}
                      </span>
                      {sc.lastRunMessage ? (
                        <span className="mt-0.5 block truncate text-zinc-500" title={sc.lastRunMessage}>
                          {sc.lastRunMessage}
                        </span>
                      ) : null}
                    </td>
                    <td className="py-2 pr-2">
                      {sc.hasVietstockCookie ? "Cookie " : ""}
                      {sc.hasRequestVerificationToken ? "Token" : ""}
                      {!sc.hasVietstockCookie && !sc.hasRequestVerificationToken ? "—" : ""}
                    </td>
                    <td className="py-2">
                      <button
                        type="button"
                        onClick={() => loadScheduleIntoForm(sc)}
                        className="mr-2 text-emerald-700 hover:underline dark:text-emerald-400"
                      >
                        Sửa
                      </button>
                      <button
                        type="button"
                        onClick={() => setScheduleDeleteTicker(sc.ticker)}
                        className="text-red-600 hover:underline dark:text-red-400"
                      >
                        Xóa
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        <div className="mt-4 space-y-3 border-t border-zinc-200 pt-4 dark:border-zinc-700">
          <p className="text-xs font-medium text-zinc-700 dark:text-zinc-300">Tạo / cập nhật lịch</p>
          <div className="flex flex-wrap items-end gap-2">
            <div>
              <label className="block text-xs text-zinc-500">Mã</label>
              <select
                value={schedTicker}
                onChange={(e) => setSchedTicker(e.target.value.toUpperCase())}
                disabled={stocks.length === 0}
                className="rounded border border-zinc-300 px-2 py-1 text-sm dark:border-zinc-600 dark:bg-zinc-900"
              >
                {stocks.map((s) => (
                  <option key={s.id} value={s.ticker}>
                    {s.ticker}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-zinc-500">Chu kỳ</label>
              <select
                value={schedInterval}
                onChange={(e) => setSchedInterval(Number(e.target.value))}
                className="rounded border border-zinc-300 px-2 py-1 text-sm dark:border-zinc-600 dark:bg-zinc-900"
              >
                <option value={15}>15 phút</option>
                <option value={30}>30 phút</option>
                <option value={60}>1 giờ</option>
                <option value={360}>6 giờ</option>
                <option value={720}>12 giờ</option>
                <option value={1440}>24 giờ (mỗi ngày)</option>
                <option value={10080}>7 ngày</option>
              </select>
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={schedEnabled}
                onChange={(e) => setSchedEnabled(e.target.checked)}
              />
              Bật lịch
            </label>
          </div>
          <p className="text-xs text-zinc-500">
            Cookie / token (tùy chọn): chỉ gửi khi điền — dùng cho crawl định kỳ. Để giữ bí mật đã lưu, để trống hai ô dưới.
          </p>
          <textarea
            value={schedCookie}
            onChange={(e) => setSchedCookie(e.target.value)}
            placeholder="Cookie VietStock (chỉ khi cần lưu mới)"
            rows={2}
            className="w-full rounded-md border border-zinc-300 bg-white p-2 font-mono text-xs dark:border-zinc-700 dark:bg-zinc-900"
          />
          <input
            value={schedToken}
            onChange={(e) => setSchedToken(e.target.value)}
            placeholder="__RequestVerificationToken"
            className="w-full rounded border border-zinc-300 px-2 py-1 font-mono text-xs dark:border-zinc-600 dark:bg-zinc-900"
          />
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              disabled={schedSaving || stocks.length === 0}
              onClick={() => void onSaveSchedule()}
              className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 dark:bg-emerald-600"
            >
              {schedSaving ? "Đang lưu…" : "Lưu lịch crawl"}
            </button>
            <button
              type="button"
              disabled={schedSaving || stocks.length === 0}
              onClick={openClearSecretsDialog}
              className="rounded-lg border border-zinc-300 px-4 py-2 text-sm dark:border-zinc-600"
            >
              Gỡ cookie/token đã lưu
            </button>
          </div>
        </div>
      </SectionCard>

      <SectionCard title="Mã chứng khoán & crawlMetadata (JSON)">
        <p className="mb-2 text-xs leading-relaxed text-zinc-500 dark:text-zinc-400">
          Crawl chỉ dùng{" "}
          <code className="rounded bg-zinc-100 px-0.5 font-mono dark:bg-zinc-800">
            POST /data/GetStockDeal_ListPriceByTimeFrame
          </code>{" "}
          (x-www-form-urlencoded). Body khớp curl:{" "}
          <code className="rounded bg-zinc-100 px-0.5 dark:bg-zinc-800">stockCode</code>,{" "}
          <code className="rounded bg-zinc-100 px-0.5 dark:bg-zinc-800">timeFrame</code>,{" "}
          <code className="rounded bg-zinc-100 px-0.5 dark:bg-zinc-800">toDate</code>,{" "}
          <code className="rounded bg-zinc-100 px-0.5 dark:bg-zinc-800">page</code>,{" "}
          <code className="rounded bg-zinc-100 px-0.5 dark:bg-zinc-800">pageSize</code> (≤20),{" "}
          <code className="rounded bg-zinc-100 px-0.5 dark:bg-zinc-800">languageID</code>,{" "}
          <code className="rounded bg-zinc-100 px-0.5 dark:bg-zinc-800">
            __RequestVerificationToken
          </code>
          . Backend chỉ gửi các field này;{" "}
          <code className="rounded bg-zinc-100 px-0.5 dark:bg-zinc-800">stockCode</code> luôn = ticker
          mã; <code className="rounded bg-zinc-100 px-0.5 dark:bg-zinc-800">Referer</code> mặc định{" "}
          <code className="rounded bg-zinc-100 px-0.5 font-mono text-[10px] dark:bg-zinc-800">
            …/{"{ticker}"}/thong-ke-giao-dich.htm
          </code>{" "}
          (ghi đè bằng <code className="rounded bg-zinc-100 px-0.5 dark:bg-zinc-800">headers</code> nếu cần).
          Header client gần với trình duyệt (Sec-Fetch-*, sec-ch-ua…); tùy chỉnh thêm qua{" "}
          <code className="rounded bg-zinc-100 px-0.5 dark:bg-zinc-800">headers</code> trong JSON.
        </p>
        <div className="mb-2 flex flex-wrap items-center gap-2">
          <label className="text-xs text-zinc-600 dark:text-zinc-400">Chọn mã</label>
          <select
            value={crawlTicker}
            onChange={(e) => setCrawlTicker(e.target.value.toUpperCase())}
            disabled={stocks.length === 0}
            className="rounded border border-zinc-300 px-2 py-1 text-sm dark:border-zinc-600 dark:bg-zinc-900"
          >
            {stocks.length === 0 ? (
              <option value="">— Chưa có mã —</option>
            ) : (
              stocks.map((s) => (
                <option key={s.id} value={s.ticker}>
                  {s.ticker} — {s.companyName}
                </option>
              ))
            )}
          </select>
          <button
            type="button"
            onClick={() =>
              setMetaJson(JSON.stringify(createDefaultVietstockCrawlMetadata(), null, 2))
            }
            className="rounded-md border border-zinc-300 px-2 py-1 text-xs dark:border-zinc-600"
          >
            Mẫu crawlMetadata
          </button>
          <button
            type="button"
            onClick={() => void onSaveMetadata()}
            className="rounded-md bg-zinc-800 px-2 py-1 text-xs text-white dark:bg-zinc-200 dark:text-zinc-900"
          >
            Lưu metadata
          </button>
        </div>
        <textarea
          value={metaJson}
          onChange={(e) => setMetaJson(e.target.value)}
          rows={12}
          className="w-full rounded-md border border-zinc-300 bg-white p-2 font-mono text-xs dark:border-zinc-700 dark:bg-zinc-900"
        />
        <p className="mt-3 text-xs font-medium text-zinc-600 dark:text-zinc-400">
          Form nhanh → <code className="rounded bg-zinc-100 px-0.5 font-mono dark:bg-zinc-800">form</code>{" "}
          (token nhập ô dưới khi crawl, không ghi vào JSON)
        </p>
        <div className="mt-1 grid gap-2 md:grid-cols-6">
          <input
            value={vsTimeFrame}
            onChange={(e) => setVsTimeFrame(e.target.value)}
            placeholder="timeFrame (C)"
            className="rounded border border-zinc-300 px-2 py-1 text-sm dark:border-zinc-600 dark:bg-zinc-900"
          />
          <input
            value={vsListPageSize}
            onChange={(e) => setVsListPageSize(e.target.value)}
            placeholder="pageSize ≤20"
            className="rounded border border-zinc-300 px-2 py-1 text-sm dark:border-zinc-600 dark:bg-zinc-900"
          />
          <input
            value={vsLanguageId}
            onChange={(e) => setVsLanguageId(e.target.value)}
            placeholder="languageID"
            className="rounded border border-zinc-300 px-2 py-1 text-sm dark:border-zinc-600 dark:bg-zinc-900"
          />
          <input
            value={vsListToDate}
            onChange={(e) => setVsListToDate(e.target.value)}
            placeholder="toDate YYYY-MM-DD (tuỳ chọn)"
            className="rounded border border-zinc-300 px-2 py-1 text-sm md:col-span-2 dark:border-zinc-600 dark:bg-zinc-900"
          />
          <button
            type="button"
            onClick={onMergeListPriceFormIntoJson}
            className="rounded-md border border-zinc-300 px-2 py-1 text-sm dark:border-zinc-600"
          >
            Áp vào JSON
          </button>
        </div>
        <p className="mt-2 text-xs leading-relaxed text-zinc-500 dark:text-zinc-400">
          Cookie / <code className="rounded bg-zinc-100 px-0.5 dark:bg-zinc-800">__RequestVerificationToken</code>{" "}
          được tải từ <span className="font-medium text-zinc-600 dark:text-zinc-300">localStorage</span> trên trình duyệt
          này (nếu đã lưu). Khi nội dung khác bản đã lưu, nút crawl sẽ hỏi có muốn cập nhật localStorage hay chỉ crawl một
          lần. Dữ liệu nhạy cảm — tránh máy dùng chung; có thể kết hợp lưu trong{" "}
          <code className="rounded bg-zinc-100 px-0.5 dark:bg-zinc-800">session</code> của JSON (metadata).
        </p>
        {!vietstockSecretsDifferFromPersisted() &&
        (vsCookie.length > 0 || vsToken.length > 0) ? (
          <p className="mt-1 text-[11px] text-emerald-700 dark:text-emerald-400">
            Đang khớp bản đã lưu trên trình duyệt — crawl sẽ không hỏi lưu lại cho đến khi bạn sửa ô.
          </p>
        ) : null}
        <textarea
          value={vsCookie}
          onChange={(e) => setVsCookie(e.target.value)}
          placeholder="Cookie (tùy chọn, ưu tiên khi gửi crawl)"
          rows={2}
          className="mt-1 w-full rounded-md border border-zinc-300 bg-white p-2 font-mono text-xs dark:border-zinc-700 dark:bg-zinc-900"
        />
        <input
          value={vsToken}
          onChange={(e) => setVsToken(e.target.value)}
          placeholder="__RequestVerificationToken (bắt buộc nếu chưa có trong JSON.form hoặc session)"
          className="mt-1 w-full rounded border border-zinc-300 px-2 py-1 font-mono text-xs dark:border-zinc-600 dark:bg-zinc-900"
        />
        <button
          type="button"
          onClick={() => void onCrawlVietstockClick()}
          disabled={vietstockCrawling}
          aria-busy={vietstockCrawling}
          className="mt-2 inline-flex items-center justify-center gap-2 rounded-md bg-emerald-800 px-3 py-1.5 text-sm text-white disabled:pointer-events-none disabled:opacity-70 dark:bg-emerald-700"
        >
          {vietstockCrawling ? (
            <>
              <Loader2 className="h-4 w-4 shrink-0 animate-spin" strokeWidth={2} aria-hidden />
              <span>Đang crawl…</span>
            </>
          ) : (
            "Crawl giá (ListPrice) & lưu DB"
          )}
        </button>
        {vietstockCrawling ? (
          <div
            className="mt-2 flex gap-2 rounded-lg border border-emerald-500/25 bg-emerald-500/5 px-3 py-2 text-xs leading-relaxed text-zinc-700 dark:border-emerald-400/20 dark:bg-emerald-950/30 dark:text-zinc-300"
            role="status"
            aria-live="polite"
          >
            <Loader2
              className="mt-0.5 h-3.5 w-3.5 shrink-0 animate-spin text-emerald-700 dark:text-emerald-400"
              strokeWidth={2}
              aria-hidden
            />
            <span>{VIETSTOCK_CRAWL_PROGRESS_HINTS[crawlProgressStep]}</span>
          </div>
        ) : null}
        <p className="mt-2 text-xs text-amber-800 dark:text-amber-200">
          Chỉ crawl khi bạn có quyền sử dụng dữ liệu theo điều khoản VietStock / nguồn tương ứng. Công cụ chỉ hỗ trợ kỹ thuật, không thay thế giấy phép dữ liệu.
        </p>
        <div className="mt-4 border-t border-zinc-200 pt-3 dark:border-zinc-700">
          <p className="mb-1 text-xs font-medium text-zinc-600 dark:text-zinc-400">Tạo mã mới</p>
          <div className="flex flex-wrap gap-2">
            <input
              value={newTicker}
              onChange={(e) => setNewTicker(e.target.value.toUpperCase())}
              placeholder="Ticker"
              className="w-24 rounded border border-zinc-300 px-2 py-1 text-sm dark:border-zinc-600 dark:bg-zinc-900"
            />
            <input
              value={newCompany}
              onChange={(e) => setNewCompany(e.target.value)}
              placeholder="Tên công ty"
              className="min-w-[12rem] flex-1 rounded border border-zinc-300 px-2 py-1 text-sm dark:border-zinc-600 dark:bg-zinc-900"
            />
            <button
              type="button"
              onClick={() => void onCreateStock()}
              className="rounded-md border border-zinc-300 px-2 py-1 text-sm dark:border-zinc-600"
            >
              Tạo (kèm metadata ô trên)
            </button>
          </div>
        </div>
      </SectionCard>

      <SectionCard title="Ingest giá thủ công (JSON)">
        <p className="mb-2 text-xs leading-relaxed text-zinc-500 dark:text-zinc-400">
          Gửi <code className="rounded bg-zinc-100 px-0.5 font-mono dark:bg-zinc-800">POST …/admin/crawl/{"{ticker}"}</code> với
          body{" "}
          <code className="rounded bg-zinc-100 px-0.5 font-mono dark:bg-zinc-800">{"{ \"data\": [ … ] }"}</code>. Mỗi phần tử
          cần ngày (
          <code className="rounded bg-zinc-100 px-0.5 font-mono dark:bg-zinc-800">TradingDate</code> hoặc{" "}
          <code className="rounded bg-zinc-100 px-0.5 font-mono dark:bg-zinc-800">trading_date</code>, ISO{" "}
          <code className="font-mono">YYYY-MM-DD</code> hoặc chuỗi{" "}
          <code className="rounded bg-zinc-100 px-0.5 font-mono dark:bg-zinc-800">/Date(ms)/</code>) và đủ OHLC: kiểu
          VietStock{" "}
          <code className="rounded bg-zinc-100 px-0.5 font-mono dark:bg-zinc-800">OpenPrice</code>,{" "}
          <code className="rounded bg-zinc-100 px-0.5 font-mono dark:bg-zinc-800">HighestPrice</code>,{" "}
          <code className="rounded bg-zinc-100 px-0.5 font-mono dark:bg-zinc-800">LowestPrice</code>,{" "}
          <code className="rounded bg-zinc-100 px-0.5 font-mono dark:bg-zinc-800">ClosePrice</code> (hoặc{" "}
          <code className="rounded bg-zinc-100 px-0.5 font-mono dark:bg-zinc-800">open_price</code> …{" "}
          <code className="rounded bg-zinc-100 px-0.5 font-mono dark:bg-zinc-800">close_price</code>, hoặc{" "}
          <code className="rounded bg-zinc-100 px-0.5 font-mono dark:bg-zinc-800">OpenIndex</code>…). Khối lượng:{" "}
          <code className="rounded bg-zinc-100 px-0.5 font-mono dark:bg-zinc-800">TotalVol</code> /{" "}
          <code className="rounded bg-zinc-100 px-0.5 font-mono dark:bg-zinc-800">volume</code> (tuỳ chọn, mặc định 0).{" "}
          <code className="rounded bg-zinc-100 px-0.5 font-mono dark:bg-zinc-800">Change</code>,{" "}
          <code className="rounded bg-zinc-100 px-0.5 font-mono dark:bg-zinc-800">PerChange</code> tuỳ chọn.
        </p>
        <input
          value={ticker}
          onChange={(e) => setTicker(e.target.value.toUpperCase())}
          className="mb-2 w-32 rounded border border-zinc-300 px-2 py-1 text-sm dark:border-zinc-600 dark:bg-zinc-900"
          placeholder="Ticker"
        />
        <textarea
          value={jsonText}
          onChange={(e) => setJsonText(e.target.value)}
          rows={16}
          spellCheck={false}
          className="w-full rounded-md border border-zinc-300 bg-white p-2 font-mono text-xs leading-relaxed dark:border-zinc-700 dark:bg-zinc-900"
        />
        <button
          type="button"
          onClick={() => void onIngest()}
          className="mt-2 rounded-md bg-zinc-900 px-3 py-1 text-sm text-white dark:bg-zinc-100 dark:text-zinc-900"
        >
          Gửi ingest
        </button>
        {msg && (
          <p className="mt-3 rounded-xl border border-emerald-200/90 bg-emerald-50/90 px-4 py-2.5 text-sm text-emerald-900 dark:border-emerald-900/40 dark:bg-emerald-950/40 dark:text-emerald-100">
            {msg}
          </p>
        )}
        {err && (
          <p className="mt-3 rounded-xl border border-red-200 bg-red-50/90 px-4 py-2.5 text-sm text-red-800 dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-200">
            {err}
          </p>
        )}
      </SectionCard>

      <ConfirmDialog
        open={crawlLocalStoragePromptOpen}
        title="Lưu cookie / token vào trình duyệt?"
        description={
          <>
            Giá trị trong hai ô đã thay đổi so với bản lưu trong{" "}
            <span className="font-medium text-zinc-700 dark:text-zinc-300">localStorage</span> (hoặc bạn chưa từng lưu).
            Bạn có muốn <span className="font-medium">ghi lại</span> để lần sau tự điền không?
            <span className="mt-2 block text-zinc-500 dark:text-zinc-500">
              «Chỉ crawl» vẫn gửi request với nội dung hiện tại nhưng không ghi localStorage (và sẽ không hỏi lại cho đến
              khi bạn sửa ô).
            </span>
          </>
        }
        cancelLabel="Hủy"
        confirmLabel="Lưu và crawl"
        variant="default"
        pending={false}
        secondaryAction={{
          label: "Chỉ crawl, không lưu",
          onClick: () => {
            if (vietstockCrawling) return;
            onCrawlPersistSkipAndRun();
          },
        }}
        onCancel={() => {
          if (vietstockCrawling) return;
          setCrawlLocalStoragePromptOpen(false);
        }}
        onConfirm={() => {
          if (vietstockCrawling) return;
          onCrawlPersistSaveAndRun();
        }}
      />

      <ConfirmDialog
        open={scheduleDeleteTicker !== null}
        title="Xóa lịch crawl?"
        description={
          scheduleDeleteTicker ? (
            <>
              Xóa hoàn toàn lịch crawl tự động cho mã{" "}
              <span className="font-semibold text-zinc-900 dark:text-zinc-100">
                {scheduleDeleteTicker}
              </span>
              . Crawl định kỳ sẽ dừng cho mã này cho đến khi bạn tạo lịch mới. Thao tác không thể hoàn tác.
            </>
          ) : null
        }
        confirmLabel="Xóa lịch"
        cancelLabel="Hủy"
        variant="danger"
        pending={confirmDialogBusy}
        onCancel={() => {
          if (!confirmDialogBusy) setScheduleDeleteTicker(null);
        }}
        onConfirm={() => void confirmDeleteSchedule()}
      />

      <ConfirmDialog
        open={clearSecretsDialogOpen}
        title="Gỡ cookie và token đã lưu?"
        description={
          <>
            Xóa cookie VietStock và{" "}
            <code className="rounded bg-zinc-100 px-0.5 font-mono text-xs dark:bg-zinc-800">
              __RequestVerificationToken
            </code>{" "}
            đang lưu cho lịch mã{" "}
            <span className="font-semibold text-zinc-900 dark:text-zinc-100">
              {schedTicker.trim().toUpperCase() || "—"}
            </span>
            . Lịch vẫn giữ chu kỳ và trạng thái bật/tắt; crawl định kỳ có thể thất bại cho đến khi nhập bí mật mới.
          </>
        }
        confirmLabel="Gỡ bí mật"
        cancelLabel="Hủy"
        variant="danger"
        pending={confirmDialogBusy}
        onCancel={() => {
          if (!confirmDialogBusy) setClearSecretsDialogOpen(false);
        }}
        onConfirm={() => void confirmClearScheduleSecrets()}
      />
    </PageShell>
  );
}
