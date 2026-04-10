import Link from "next/link";
import { ROUTES } from "@/constants/routes";
import type { StockListItem } from "@/types/stock";

export function StocksListTable({ items }: { items: StockListItem[] }) {
  if (items.length === 0) {
    return (
      <p className="rounded-xl border border-dashed border-zinc-300 py-12 text-center text-sm text-zinc-500 dark:border-zinc-600">
        Chưa có mã nào trong hệ thống.
      </p>
    );
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-zinc-200/90 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-950/80">
      <div className="border-b border-zinc-100 px-4 py-3 dark:border-zinc-800">
        <h2 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">
          Danh sách cổ phiếu
        </h2>
        <p className="mt-0.5 text-xs text-zinc-500 dark:text-zinc-400">
          Chọn mã để xem biểu đồ, chỉ báo và phân tích.
        </p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[480px] border-collapse text-sm">
          <thead>
            <tr className="border-b border-zinc-200 bg-zinc-50/90 text-left text-xs font-semibold uppercase tracking-wide text-zinc-600 dark:border-zinc-800 dark:bg-zinc-900/60 dark:text-zinc-400">
              <th scope="col" className="px-4 py-3">
                Mã
              </th>
              <th scope="col" className="px-4 py-3">
                Tên công ty
              </th>
              <th scope="col" className="px-4 py-3">
                Sàn
              </th>
              <th scope="col" className="px-4 py-3 text-right">
                Ngành
              </th>
            </tr>
          </thead>
          <tbody>
            {items.map((s) => (
              <tr
                key={s.id}
                className="border-b border-zinc-100 transition hover:bg-emerald-50/40 dark:border-zinc-800/80 dark:hover:bg-emerald-950/15"
              >
                <td className="px-4 py-3">
                  <Link
                    href={ROUTES.stockDetail(s.ticker)}
                    className="font-semibold text-emerald-700 hover:underline dark:text-emerald-400"
                  >
                    {s.ticker}
                  </Link>
                </td>
                <td className="max-w-[220px] truncate px-4 py-3 text-zinc-800 dark:text-zinc-200">
                  <Link
                    href={ROUTES.stockDetail(s.ticker)}
                    className="hover:text-emerald-700 hover:underline dark:hover:text-emerald-400"
                  >
                    {s.companyName}
                  </Link>
                </td>
                <td className="px-4 py-3">
                  <span className="inline-flex rounded-md bg-zinc-100 px-2 py-0.5 text-xs font-medium text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">
                    {s.exchange || "—"}
                  </span>
                </td>
                <td className="px-4 py-3 text-right text-zinc-600 dark:text-zinc-400">
                  {s.sector || "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
