import { PageShell } from "@/components/common/PageShell";
import { MarketIndicesTable } from "@/components/stock/MarketIndicesTable";
import { StocksListTable } from "@/components/stock/StocksListTable";
import { ApiClientError } from "@/services/api-client";
import { listPerformanceBoard, listStocks } from "@/services/stock.service";
import type { MarketIndexRow } from "@/types/market-index";
import type { StockPerformanceRow } from "@/types/stock";

export const dynamic = "force-dynamic";

function performanceToMarketRows(rows: StockPerformanceRow[]): MarketIndexRow[] {
  return rows.map((r) => ({
    code: r.ticker,
    name: r.companyName,
    price: r.closePrice,
    d: r.pctDay,
    w: r.pctWeek,
    m: r.pctMonth,
    q: r.pctQuarter,
    ytd: r.pctYtd,
    y: r.pctYear,
  }));
}

function boardAsOfLabel(rows: StockPerformanceRow[]): string | undefined {
  const ds = rows.map((r) => r.asOfDate).filter((x): x is string => Boolean(x));
  if (ds.length === 0) return undefined;
  const uniq = [...new Set(ds)].sort();
  if (uniq.length === 1) return `Phiên gần nhất trong dữ liệu: ${uniq[0]}`;
  return `Nhiều phiên — mới nhất: ${uniq[uniq.length - 1]}`;
}

export default async function StocksPage() {
  let items: Awaited<ReturnType<typeof listStocks>> = [];
  let boardRows: MarketIndexRow[] = [];
  let boardRaw: StockPerformanceRow[] = [];
  let err: string | null = null;
  let boardErr: string | null = null;

  try {
    items = await listStocks();
  } catch (e: unknown) {
    if (e instanceof ApiClientError) {
      err = e.message;
    } else if (e instanceof Error) {
      err = e.message;
    } else {
      err = "Không tải được danh sách mã — kiểm tra API / NEXT_PUBLIC_API_URL (và API_URL khi SSR Docker).";
    }
  }

  try {
    boardRaw = await listPerformanceBoard(100, 800);
    boardRows = performanceToMarketRows(boardRaw);
  } catch (e: unknown) {
    if (e instanceof ApiClientError) {
      boardErr = e.message;
    } else if (e instanceof Error) {
      boardErr = e.message;
    } else {
      boardErr = "Không tải được bảng hiệu suất — kiểm tra backend.";
    }
  }

  const boardLabel = boardErr ? undefined : boardAsOfLabel(boardRaw);

  return (
    <PageShell
      title="Cổ phiếu & chỉ số"
      description="Hiệu suất giá tính từ lịch sử trong cơ sở dữ liệu và danh sách mã đang hoạt động."
    >
      <div className="space-y-10">
        <div className="-mt-2 flex flex-col gap-3 rounded-2xl border border-zinc-200/80 bg-gradient-to-br from-emerald-50/40 via-white to-zinc-50/90 px-5 py-4 dark:border-zinc-800 dark:from-emerald-950/20 dark:via-zinc-950 dark:to-zinc-900/80 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <p className="max-w-2xl text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
            Cột <span className="font-medium text-zinc-800 dark:text-zinc-200">Giá</span> và{" "}
            <span className="font-medium text-zinc-800 dark:text-zinc-200">D·W·M·Q·YTD·Y</span> được{" "}
            <span className="font-medium text-zinc-800 dark:text-zinc-200">tính trên server</span> từ{" "}
            <code className="rounded bg-zinc-100 px-1 font-mono text-xs dark:bg-zinc-800">stock_price_histories</code>{" "}
            của từng mã (đóng cửa, kỳ lịch như mô tả khi rê chuột lên tiêu đề cột).
          </p>
          <span className="shrink-0 rounded-full bg-emerald-100/90 px-3 py-1 text-center text-xs font-medium text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-200">
            Dữ liệu thật trong DB
          </span>
        </div>

        {boardErr ? (
          <div
            role="alert"
            className="rounded-2xl border border-amber-200/90 bg-amber-50/90 px-5 py-4 text-sm text-amber-900 dark:border-amber-900/40 dark:bg-amber-950/40 dark:text-amber-100"
          >
            Không tải bảng hiệu suất: {boardErr}
          </div>
        ) : (
          <MarketIndicesTable
            rows={boardRows}
            updatedAtLabel={boardLabel}
            footnote="Mỗi hàng là một mã đang hoạt động; ô trống (—) khi chưa đủ lịch sử giá cho kỳ đó."
          />
        )}

        {err ? (
          <div
            role="alert"
            className="rounded-2xl border border-red-200/90 bg-red-50/90 px-5 py-4 text-sm leading-relaxed text-red-800 shadow-sm dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-200"
          >
            {err}
          </div>
        ) : (
          <StocksListTable items={items} />
        )}
      </div>
    </PageShell>
  );
}
