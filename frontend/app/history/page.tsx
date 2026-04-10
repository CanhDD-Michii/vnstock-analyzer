"use client";

import { ChevronRight } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { PageShell } from "@/components/common/PageShell";
import { SectionCard } from "@/components/ui/SectionCard";
import { ROUTES } from "@/constants/routes";
import { ApiClientError } from "@/services/api-client";
import * as analysisApi from "@/services/analysis.service";
import type { AnalysisHistoryItem } from "@/types/analysis";

function SkeletonRow() {
  return (
    <div className="animate-pulse rounded-2xl border border-zinc-200/80 bg-zinc-50/80 p-5 dark:border-zinc-800 dark:bg-zinc-900/40">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-2">
          <div className="h-6 w-24 rounded-md bg-zinc-200 dark:bg-zinc-700" />
          <div className="h-4 w-36 rounded-md bg-zinc-100 dark:bg-zinc-800" />
        </div>
        <div className="flex flex-wrap gap-2">
          <div className="h-7 w-16 rounded-lg bg-zinc-200 dark:bg-zinc-700" />
          <div className="h-7 w-16 rounded-lg bg-zinc-200 dark:bg-zinc-700" />
          <div className="h-7 w-20 rounded-lg bg-zinc-200 dark:bg-zinc-700" />
        </div>
      </div>
    </div>
  );
}

function ScoreChip({ label, value }: { label: string; value: string | number }) {
  return (
    <span className="inline-flex items-baseline gap-1 rounded-lg border border-zinc-200/90 bg-white/90 px-2.5 py-1 text-xs dark:border-zinc-700 dark:bg-zinc-900/60">
      <span className="font-medium text-zinc-500 dark:text-zinc-400">{label}</span>
      <span className="tabular-nums font-semibold text-zinc-900 dark:text-zinc-100">{value}</span>
    </span>
  );
}

export default function HistoryPage() {
  const [items, setItems] = useState<AnalysisHistoryItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [needsLogin, setNeedsLogin] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void (async () => {
      setLoading(true);
      try {
        const data = await analysisApi.listAnalysisHistory();
        setItems(data);
        setNeedsLogin(false);
        setError(null);
      } catch (e: unknown) {
        if (e instanceof ApiClientError && e.status === 401) {
          setNeedsLogin(true);
          setError(null);
          setItems([]);
        } else {
          setNeedsLogin(false);
          setError(e instanceof Error ? e.message : "Không tải được lịch sử");
        }
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const showList = !loading && !needsLogin && !error;
  const hasItems = items.length > 0;

  return (
    <PageShell
      title="Lịch sử phân tích"
      description="Các lần chạy phân tích đã lưu — mở từng mục để xem tóm tắt AI và khuyến nghị."
    >
      <div className="space-y-6">
        {needsLogin && (
          <div className="rounded-2xl border border-amber-200/90 bg-gradient-to-br from-amber-50/95 to-orange-50/40 px-5 py-4 text-sm text-amber-950 shadow-sm dark:border-amber-900/45 dark:from-amber-950/50 dark:to-orange-950/20 dark:text-amber-100">
            <p className="font-medium">Cần đăng nhập</p>
            <p className="mt-1 text-amber-900/90 dark:text-amber-200/90">
              Vui lòng{" "}
              <Link
                href={ROUTES.login}
                className="font-semibold text-amber-800 underline decoration-amber-600/50 underline-offset-2 hover:text-amber-950 dark:text-amber-100"
              >
                đăng nhập
              </Link>{" "}
              để xem lịch sử phân tích của bạn.
            </p>
          </div>
        )}

        {error && (
          <div
            role="alert"
            className="rounded-2xl border border-red-200/90 bg-red-50/95 px-5 py-4 text-sm text-red-900 shadow-sm dark:border-red-900/50 dark:bg-red-950/45 dark:text-red-100"
          >
            {error}
          </div>
        )}

        {loading && (
          <div className="space-y-3">
            <p className="text-sm text-zinc-500 dark:text-zinc-400">Đang tải lịch sử…</p>
            <SkeletonRow />
            <SkeletonRow />
            <SkeletonRow />
          </div>
        )}

        {showList && (
          <SectionCard title="Các lần phân tích đã lưu">
            {hasItems ? (
              <>
                <div className="-mt-1 mb-5 flex flex-wrap items-center justify-between gap-2 border-b border-zinc-100 pb-4 dark:border-zinc-800">
                  <p className="text-sm text-zinc-600 dark:text-zinc-400">
                    <span className="font-semibold tabular-nums text-zinc-900 dark:text-zinc-100">
                      {items.length}
                    </span>{" "}
                    bản ghi
                  </p>
                  <Link
                    href={ROUTES.stocks}
                    className="inline-flex items-center gap-1 text-xs font-medium text-emerald-700 transition hover:text-emerald-800 dark:text-emerald-400 dark:hover:text-emerald-300"
                  >
                    Chạy phân tích mới
                    <ChevronRight className="h-3.5 w-3.5 shrink-0" strokeWidth={2} aria-hidden />
                  </Link>
                </div>
                <ul className="space-y-3">
                  {items.map((row) => (
                    <li key={row.id}>
                      <Link
                        href={ROUTES.historyDetail(row.id)}
                        className="group relative block overflow-hidden rounded-2xl border border-zinc-200/90 bg-gradient-to-br from-white via-white to-zinc-50/80 p-4 shadow-sm shadow-zinc-900/[0.03] transition hover:border-emerald-300/60 hover:shadow-md hover:shadow-emerald-900/[0.06] dark:border-zinc-800 dark:from-zinc-950 dark:via-zinc-950 dark:to-zinc-900/60 dark:shadow-black/20 dark:hover:border-emerald-500/35"
                      >
                        <span
                          className="pointer-events-none absolute inset-y-0 right-0 w-1 bg-gradient-to-b from-emerald-500/0 via-emerald-500/40 to-teal-500/0 opacity-0 transition group-hover:opacity-100"
                          aria-hidden
                        />
                        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                          <div className="min-w-0 flex-1">
                            <div className="flex flex-wrap items-center gap-2">
                              <span className="text-lg font-bold tracking-tight text-zinc-900 dark:text-white">
                                {row.stockTicker}
                              </span>
                              <span className="rounded-md bg-zinc-100 px-2 py-0.5 text-xs font-medium text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
                                {row.analysisDate}
                              </span>
                            </div>
                            {row.aiRecommendation ? (
                              <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
                                <span className="font-medium text-zinc-700 dark:text-zinc-300">
                                  Khuyến nghị:
                                </span>{" "}
                                {row.aiRecommendation}
                              </p>
                            ) : (
                              <p className="mt-2 text-sm italic text-zinc-400 dark:text-zinc-500">
                                Chưa có khuyến nghị ghi trong lịch sử.
                              </p>
                            )}
                          </div>
                          <div className="flex shrink-0 flex-wrap items-center gap-2 sm:flex-col sm:items-end">
                            <div className="flex flex-wrap gap-2">
                              <ScoreChip label="Tech" value={row.technicalScore ?? "—"} />
                              <ScoreChip label="Risk" value={row.riskScore ?? "—"} />
                              <ScoreChip label="Cơ bản" value={row.fundamentalScore ?? "—"} />
                            </div>
                            <span className="inline-flex items-center gap-1 text-xs font-medium text-emerald-600 opacity-80 transition group-hover:opacity-100 dark:text-emerald-400">
                              Chi tiết
                              <ChevronRight
                                className="h-3.5 w-3.5 shrink-0 transition group-hover:translate-x-0.5"
                                strokeWidth={2}
                                aria-hidden
                              />
                            </span>
                          </div>
                        </div>
                      </Link>
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <div className="flex flex-col items-center rounded-2xl border border-dashed border-zinc-200 bg-zinc-50/50 px-6 py-14 text-center dark:border-zinc-700 dark:bg-zinc-900/30">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-100/90 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300">
                  <svg className="h-7 w-7" viewBox="0 0 24 24" fill="none" aria-hidden>
                    <path
                      d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
                      stroke="currentColor"
                      strokeWidth="1.75"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </div>
                <p className="mt-4 text-base font-semibold text-zinc-900 dark:text-white">
                  Chưa có phân tích nào được lưu
                </p>
                <p className="mt-2 max-w-sm text-sm leading-relaxed text-zinc-500 dark:text-zinc-400">
                  Chọn một mã cổ phiếu và chạy phân tích (khi đã đăng nhập) — kết quả sẽ xuất hiện tại đây.
                </p>
                <Link
                  href={ROUTES.stocks}
                  className="mt-6 inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 px-5 py-2.5 text-sm font-semibold text-white shadow-md shadow-emerald-600/25 transition hover:from-emerald-500 hover:to-teal-500"
                >
                  Xem danh sách cổ phiếu
                </Link>
              </div>
            )}
          </SectionCard>
        )}
      </div>
    </PageShell>
  );
}
