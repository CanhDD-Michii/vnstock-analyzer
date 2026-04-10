import type { MarketIndexRow } from "@/types/market-index";

const COL_HELP: Record<string, string> = {
  price: "Giá đóng cửa phiên gần nhất (từ DB)",
  d: "Thay đổi % trong phiên gần nhất (Day)",
  w: "Thay đổi % so với ~7 ngày lịch (Week)",
  m: "Thay đổi % so với ~30 ngày lịch (Month)",
  q: "Thay đổi % so với ~92 ngày lịch (Quarter)",
  ytd: "Thay đổi % từ phiên đầu năm dương lịch trong dữ liệu (YTD)",
  y: "Thay đổi % so với ~365 ngày lịch (Year)",
};

function formatPrice(n: number | null): string {
  if (n === null || Number.isNaN(n)) return "—";
  return new Intl.NumberFormat("vi-VN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(n);
}

function formatPct(n: number | null): string {
  if (n === null || Number.isNaN(n)) return "—";
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toFixed(2)}%`;
}

function pctClass(n: number | null): string {
  if (n === null || Number.isNaN(n)) return "text-zinc-400 dark:text-zinc-500";
  if (n > 0) return "text-emerald-600 dark:text-emerald-400";
  if (n < 0) return "text-red-600 dark:text-red-400";
  return "text-zinc-500 dark:text-zinc-500";
}

type Props = {
  rows: MarketIndexRow[];
  updatedAtLabel?: string;
  /** Ghi chú dưới tiêu đề (VD: nguồn dữ liệu) */
  footnote?: string | null;
  /** Tiêu đề bảng */
  title?: string;
};

export function MarketIndicesTable({
  rows,
  updatedAtLabel,
  footnote,
  title = "Bảng hiệu suất giá các mã",
}: Props) {
  return (
    <div className="overflow-hidden rounded-2xl border border-zinc-200/90 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-950/80">
      <div className="flex flex-col gap-1 border-b border-zinc-100 px-4 py-3 sm:flex-row sm:items-center sm:justify-between dark:border-zinc-800">
        <div>
          <h2 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">{title}</h2>
          {footnote ? (
            <p className="mt-0.5 text-xs text-zinc-500 dark:text-zinc-400">{footnote}</p>
          ) : null}
        </div>
        {updatedAtLabel ? (
          <p className="text-xs text-zinc-400 dark:text-zinc-500">{updatedAtLabel}</p>
        ) : null}
      </div>

      <div className="overflow-x-auto">
        {rows.length === 0 ? (
          <p className="px-4 py-8 text-center text-sm text-zinc-500 dark:text-zinc-400">
            Chưa có mã hoặc chưa có lịch sử giá — hãy crawl / ingest dữ liệu trước.
          </p>
        ) : (
          <table className="w-full min-w-[720px] border-collapse text-sm">
            <thead>
              <tr className="border-b border-zinc-200 bg-zinc-50/90 dark:border-zinc-800 dark:bg-zinc-900/60">
                <th
                  scope="col"
                  className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-zinc-600 dark:text-zinc-400"
                >
                  Mã
                </th>
                <th
                  scope="col"
                  title={COL_HELP.price}
                  className="px-3 py-3 text-right text-xs font-semibold uppercase tracking-wide text-zinc-600 dark:text-zinc-400"
                >
                  Giá
                </th>
                {(
                  [
                    ["d", "D"],
                    ["w", "W"],
                    ["m", "M"],
                    ["q", "Q"],
                    ["ytd", "YTD"],
                    ["y", "Y"],
                  ] as const
                ).map(([key, label]) => (
                  <th
                    key={key}
                    scope="col"
                    title={COL_HELP[key]}
                    className="px-2 py-3 text-right text-xs font-semibold uppercase tracking-wide text-zinc-600 dark:text-zinc-400"
                  >
                    <span className="cursor-help border-b border-dotted border-zinc-400 dark:border-zinc-500">
                      {label}
                    </span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr
                  key={row.code}
                  className={`border-b border-zinc-100 transition dark:border-zinc-800/80 ${
                    row.highlight
                      ? "bg-[#FFF2E0]/90 dark:bg-amber-950/25"
                      : "hover:bg-zinc-50/80 dark:hover:bg-zinc-900/40"
                  }`}
                >
                  <th
                    scope="row"
                    className="max-w-[14rem] px-4 py-2.5 text-left font-semibold text-zinc-900 dark:text-zinc-100"
                  >
                    <span className="whitespace-nowrap">{row.code}</span>
                    {row.name ? (
                      <span className="mt-0.5 block truncate text-xs font-normal text-zinc-500 dark:text-zinc-400">
                        {row.name}
                      </span>
                    ) : null}
                  </th>
                  <td className="whitespace-nowrap px-3 py-2.5 text-right tabular-nums font-medium text-zinc-900 dark:text-zinc-100">
                    {formatPrice(row.price)}
                  </td>
                  <td
                    className={`whitespace-nowrap px-2 py-2.5 text-right tabular-nums font-medium ${pctClass(row.d)}`}
                  >
                    {formatPct(row.d)}
                  </td>
                  <td
                    className={`whitespace-nowrap px-2 py-2.5 text-right tabular-nums font-medium ${pctClass(row.w)}`}
                  >
                    {formatPct(row.w)}
                  </td>
                  <td
                    className={`whitespace-nowrap px-2 py-2.5 text-right tabular-nums font-medium ${pctClass(row.m)}`}
                  >
                    {formatPct(row.m)}
                  </td>
                  <td
                    className={`whitespace-nowrap px-2 py-2.5 text-right tabular-nums font-medium ${pctClass(row.q)}`}
                  >
                    {formatPct(row.q)}
                  </td>
                  <td
                    className={`whitespace-nowrap px-2 py-2.5 text-right tabular-nums font-medium ${pctClass(row.ytd)}`}
                  >
                    {formatPct(row.ytd)}
                  </td>
                  <td
                    className={`whitespace-nowrap px-2 py-2.5 text-right tabular-nums font-medium ${pctClass(row.y)}`}
                  >
                    {formatPct(row.y)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
