"use client";

import { ChevronLeft, Loader2 } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { SectionCard } from "@/components/ui/SectionCard";
import { CandlestickChart } from "@/components/stock/CandlestickChart";
import { PriceChart } from "@/components/stock/PriceChart";
import { ROUTES } from "@/constants/routes";
import { ApiClientError } from "@/services/api-client";
import * as analysisApi from "@/services/analysis.service";
import * as stockApi from "@/services/stock.service";
import { AiAnalysisDisplay } from "@/components/stock/AiAnalysisDisplay";
import {
  normalizeMarketState,
  orderedScoreEntries,
} from "@/lib/technical-engine-copy";
import type { PriceBar, StockDetail } from "@/types/stock";
import type { RunAnalysisResult } from "@/types/analysis";

export function StockDetailClient({
  ticker,
  initialDetail,
  initialPrices,
}: {
  ticker: string;
  initialDetail: StockDetail;
  initialPrices: PriceBar[];
}) {
  const [prices] = useState(initialPrices);
  const [technicals, setTechnicals] = useState<Record<string, unknown> | null>(null);
  const [techErr, setTechErr] = useState<string | null>(null);
  const [techLoading, setTechLoading] = useState(true);
  const [analysis, setAnalysis] = useState<RunAnalysisResult | null>(null);
  const [runErr, setRunErr] = useState<string | null>(null);
  const [runNeedsLogin, setRunNeedsLogin] = useState(false);
  const [running, setRunning] = useState(false);

  const loadTechnicals = useCallback(async () => {
    setTechLoading(true);
    setTechErr(null);
    try {
      const t = await stockApi.getStockTechnicals(ticker);
      setTechnicals(t);
    } catch (e: unknown) {
      setTechErr(e instanceof Error ? e.message : "Không tải được chỉ báo");
    } finally {
      setTechLoading(false);
    }
  }, [ticker]);

  useEffect(() => {
    void loadTechnicals();
  }, [loadTechnicals]);

  async function onAnalyze() {
    setRunErr(null);
    setRunNeedsLogin(false);
    setRunning(true);
    try {
      const res = await analysisApi.runAnalysis(ticker);
      setAnalysis(res);
    } catch (e: unknown) {
      if (e instanceof ApiClientError && e.status === 401) {
        setRunNeedsLogin(true);
        setRunErr(null);
      } else {
        setRunErr(e instanceof Error ? e.message : "Phân tích thất bại");
      }
    } finally {
      setRunning(false);
    }
  }

  const scoresRaw = technicals?.scores as Record<string, number> | undefined;
  const technicalScoreRaw =
    technicals?.technical_score ?? technicals?.technicalScore;
  const technicalScore =
    typeof technicalScoreRaw === "number" && Number.isFinite(technicalScoreRaw)
      ? technicalScoreRaw
      : undefined;
  const scoreRows =
    scoresRaw != null
      ? orderedScoreEntries(
          scoresRaw,
          technicalScore !== undefined
            ? { technical_score: technicalScore }
            : undefined,
        )
      : [];
  const marketState = normalizeMarketState(technicals?.state);
  const analysisDateRaw =
    technicals?.analysis_date ?? technicals?.analysisDate;
  const analysisDate =
    typeof analysisDateRaw === "string" ? analysisDateRaw : null;

  return (
    <div className="flex flex-col gap-8">
      <Link
        href={ROUTES.stocks}
        className="inline-flex w-fit items-center gap-2 rounded-xl border border-zinc-200/90 bg-white/80 px-4 py-2.5 text-sm font-medium text-zinc-700 shadow-sm transition hover:border-emerald-300/60 hover:bg-emerald-50/50 hover:text-emerald-800 dark:border-zinc-700 dark:bg-zinc-900/60 dark:text-zinc-200 dark:hover:border-emerald-500/35 dark:hover:bg-emerald-950/30 dark:hover:text-emerald-100"
      >
        <ChevronLeft className="h-4 w-4 shrink-0" strokeWidth={2} aria-hidden />
        Danh sách cổ phiếu
      </Link>
      <SectionCard title="Thông tin mã">
        <p className="text-sm leading-relaxed">
          <span className="font-medium text-zinc-900 dark:text-zinc-100">{initialDetail.companyName}</span>
          <span className="text-zinc-400 dark:text-zinc-500"> · </span>
          <span className="rounded-md bg-zinc-100 px-2 py-0.5 text-xs font-semibold text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">
            {initialDetail.exchange}
          </span>
          <span className="text-zinc-400 dark:text-zinc-500"> · </span>
          {initialDetail.sector || "—"}
        </p>
      </SectionCard>
      <SectionCard title="Biểu đồ nến (OHLC)">
        {prices.length === 0 ? (
          <p className="text-sm text-zinc-500">Chưa có dữ liệu giá.</p>
        ) : (
          <CandlestickChart bars={prices} title={ticker} />
        )}
      </SectionCard>
      <SectionCard title="Biểu đồ giá đóng cửa">
        {prices.length === 0 ? (
          <p className="text-sm text-zinc-500">Chưa có dữ liệu giá.</p>
        ) : (
          <PriceChart bars={prices} title={ticker} />
        )}
      </SectionCard>
      <SectionCard title="Chỉ báo & engine">
        {analysisDate && (
          <p className="mb-3 text-xs text-zinc-500 dark:text-zinc-400">
            Ngày dữ liệu tính toán:{" "}
            <span className="font-medium text-zinc-700 dark:text-zinc-300">
              {analysisDate}
            </span>
          </p>
        )}
        {techErr && (
          <p className="mb-2 text-sm text-amber-700 dark:text-amber-300">{techErr}</p>
        )}
        {scoreRows.length > 0 && (
          <ul className="grid gap-3 text-sm md:grid-cols-2">
            {scoreRows.map(({ key, value, meta }) => (
              <li
                key={key}
                className="rounded-lg border border-zinc-200/80 bg-zinc-50/50 p-3 dark:border-zinc-700 dark:bg-zinc-900/40"
              >
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <span className="font-medium text-zinc-900 dark:text-zinc-100">
                    {meta.label}
                  </span>
                  <span className="tabular-nums text-lg font-semibold tracking-tight text-zinc-800 dark:text-zinc-100">
                    {value}
                  </span>
                </div>
                <p className="mt-2 text-xs leading-relaxed text-zinc-600 dark:text-zinc-400">
                  {meta.help}
                </p>
              </li>
            ))}
          </ul>
        )}
        {marketState && (
          <div className="mt-4 rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-700 dark:bg-zinc-950/50">
            <p className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
              Trạng thái thị trường: {marketState.titleVi}
            </p>
            {marketState.titleEn &&
              marketState.titleVi !== marketState.titleEn && (
                <p className="mt-0.5 text-xs text-zinc-400">
                  ({marketState.titleEn})
                </p>
              )}
            {marketState.description ? (
              <p className="mt-2 text-sm leading-relaxed text-zinc-700 dark:text-zinc-300">
                {marketState.description}
              </p>
            ) : null}
          </div>
        )}
        <button
          type="button"
          disabled={techLoading}
          aria-busy={techLoading}
          onClick={() => void loadTechnicals()}
          className="mt-4 inline-flex items-center justify-center gap-2 rounded-xl border border-zinc-200 bg-zinc-50/80 px-4 py-2 text-xs font-medium text-zinc-700 transition hover:border-emerald-300/50 hover:bg-emerald-50/40 hover:text-emerald-900 disabled:pointer-events-none disabled:opacity-60 dark:border-zinc-600 dark:bg-zinc-900/50 dark:text-zinc-200 dark:hover:border-emerald-500/30 dark:hover:bg-emerald-950/25"
        >
          {techLoading ? (
            <>
              <Loader2 className="h-3.5 w-3.5 shrink-0 animate-spin" strokeWidth={2} aria-hidden />
              <span>Đang tải…</span>
            </>
          ) : (
            "Làm mới chỉ báo"
          )}
        </button>
      </SectionCard>
      <SectionCard title="Phân tích (AI + lưu lịch sử)">
        <button
          type="button"
          disabled={running}
          aria-busy={running}
          onClick={() => void onAnalyze()}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 px-5 py-2.5 text-sm font-semibold text-white shadow-md shadow-emerald-600/25 transition hover:from-emerald-500 hover:to-teal-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {running ? (
            <>
              <Loader2 className="h-4 w-4 shrink-0 animate-spin" strokeWidth={2} aria-hidden />
              <span>Đang chạy…</span>
            </>
          ) : (
            "Chạy phân tích"
          )}
        </button>
        {runNeedsLogin && (
          <p className="mt-2 text-sm text-amber-800 dark:text-amber-200">
            Cần{" "}
            <Link href={ROUTES.login} className="font-medium underline">
              đăng nhập
            </Link>{" "}
            để chạy phân tích và lưu lịch sử.
          </p>
        )}
        {runErr && (
          <p className="mt-2 text-sm text-red-600 dark:text-red-400">{runErr}</p>
        )}
        {analysis?.ai != null && typeof analysis.ai === "object" && (
          <AiAnalysisDisplay ai={analysis.ai as Record<string, unknown>} />
        )}
      </SectionCard>
    </div>
  );
}
