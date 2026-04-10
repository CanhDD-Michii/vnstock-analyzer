"use client";

import { ChevronRight } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { PageShell } from "@/components/common/PageShell";
import { SectionCard } from "@/components/ui/SectionCard";
import { ROUTES } from "@/constants/routes";
import { ADMIN_DEFAULT_STOCK_TICKER, createDefaultVietstockCrawlMetadata } from "@/constants/vietstock-defaults";
import { useAuth } from "@/hooks/useAuth";
import * as adminApi from "@/services/admin.service";

const PAGE_TITLE = "Quản lý mã chứng khoán";

function isRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === "object" && v !== null && !Array.isArray(v);
}

export default function StockSymbolManagementPage() {
  const { user, loading } = useAuth();
  const [stocks, setStocks] = useState<adminApi.StockAdminRow[]>([]);
  const [logs, setLogs] = useState<adminApi.CrawlLogRow[]>([]);
  const [jsonText, setJsonText] = useState('{"data":[]}');
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

  async function onClearScheduleSecrets() {
    setMsg(null);
    setErr(null);
    const t = schedTicker.trim().toUpperCase();
    if (!t) return;
    setSchedSaving(true);
    try {
      await adminApi.adminUpsertCrawlSchedule(t, {
        isEnabled: schedEnabled,
        intervalMinutes: schedInterval,
        vietstockCookie: null,
        requestVerificationToken: null,
      });
      setMsg(`Đã gỡ cookie/token lịch cho ${t}.`);
      await refreshData();
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "Thao tác thất bại");
    } finally {
      setSchedSaving(false);
    }
  }

  async function onDeleteSchedule(ticker: string) {
    if (!confirm(`Xóa lịch crawl cho ${ticker}?`)) return;
    setMsg(null);
    setErr(null);
    try {
      await adminApi.adminDeleteCrawlSchedule(ticker);
      setMsg(`Đã xóa lịch ${ticker}.`);
      await refreshData();
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "Xóa lịch thất bại");
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

  async function onCrawlVietstock() {
    setMsg(null);
    setErr(null);
    if (!stocks.some((s) => s.ticker === crawlTicker)) {
      setErr("Chưa có mã để crawl.");
      return;
    }
    try {
      const res = await adminApi.adminCrawlVietstock(crawlTicker, {
        cookie: vsCookie.trim() || undefined,
        requestVerificationToken: vsToken.trim() || undefined,
      });
      setMsg(
        `VietStock: inserted=${res.inserted}, updated=${res.updated}, skipped=${res.skipped}`,
      );
      setLogs(await adminApi.adminCrawlLogs());
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "Crawl VietStock thất bại");
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
        <ul className="max-h-48 overflow-auto text-xs">
          {logs.map((l) => (
            <li key={l.id}>
              {l.crawlType} · {l.status} · {l.message ?? ""}
            </li>
          ))}
        </ul>
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
                        onClick={() => void onDeleteSchedule(sc.ticker)}
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
              onClick={() => void onClearScheduleSecrets()}
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
        <p className="mt-2 text-xs text-zinc-500">
          Cookie / <code className="rounded bg-zinc-100 px-0.5 dark:bg-zinc-800">__RequestVerificationToken</code>{" "}
          thường hết hạn; nên dán khi crawl, hoặc lưu trong{" "}
          <code className="rounded bg-zinc-100 px-0.5 dark:bg-zinc-800">session</code> của JSON (cân nhắc bảo mật).
        </p>
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
          onClick={() => void onCrawlVietstock()}
          className="mt-2 rounded-md bg-emerald-800 px-3 py-1.5 text-sm text-white dark:bg-emerald-700"
        >
          Crawl giá (ListPrice) &amp; lưu DB
        </button>
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
        <p className="mb-2 text-xs text-zinc-500">
          Body: <code className="rounded bg-zinc-100 px-0.5 dark:bg-zinc-800">data[]</code> các object có{" "}
          <code className="rounded bg-zinc-100 px-0.5 dark:bg-zinc-800">TradingDate</code> (/Date(ms)/ hoặc ISO) và
          OHLCV (vd. <code className="rounded bg-zinc-100 px-0.5 dark:bg-zinc-800">OpenPrice</code>… hoặc OpenIndex…).
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
          rows={8}
          className="w-full rounded-md border border-zinc-300 bg-white p-2 font-mono text-xs dark:border-zinc-700 dark:bg-zinc-900"
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
    </PageShell>
  );
}
