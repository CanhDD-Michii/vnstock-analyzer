"use client";

import { useId, useMemo, useRef, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceDot,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { PriceBar } from "@/types/stock";
import { ChartFullscreenIconButton } from "@/components/stock/ChartFullscreenIconButton";
import { useChartFullscreen } from "@/components/stock/useChartFullscreen";

export type ChartRange = "1D" | "5D" | "1M" | "3M" | "6M" | "YTD" | "1Y" | "ALL";

const RANGES: { key: ChartRange; label: string }[] = [
  { key: "1D", label: "1D" },
  { key: "5D", label: "5D" },
  { key: "1M", label: "1M" },
  { key: "3M", label: "3M" },
  { key: "6M", label: "6M" },
  { key: "YTD", label: "YTD" },
  { key: "1Y", label: "1Y" },
  { key: "ALL", label: "ALL" },
];

function parseBarDate(s: string): Date {
  return new Date(`${s.slice(0, 10)}T12:00:00`);
}

function sortBarsAsc(bars: PriceBar[]): PriceBar[] {
  return [...bars].sort((a, b) => a.tradingDate.localeCompare(b.tradingDate));
}

/** Lọc theo khoảng; dữ liệu EOD — 1D dùng vài phiên cuối để đường có hình dạng. */
export function filterBarsByRange(bars: PriceBar[], range: ChartRange): PriceBar[] {
  if (bars.length === 0) return [];
  const sorted = sortBarsAsc(bars);
  const last = sorted[sorted.length - 1]!;
  const lastD = parseBarDate(last.tradingDate);

  const takeLast = (n: number) => sorted.slice(Math.max(0, sorted.length - Math.max(1, n)));

  switch (range) {
    case "1D":
      return takeLast(Math.min(5, sorted.length));
    case "5D":
      return takeLast(5);
    case "1M":
      return takeLast(22);
    case "3M":
      return takeLast(66);
    case "6M":
      return takeLast(132);
    case "YTD": {
      const y = lastD.getFullYear();
      const start = new Date(y, 0, 1);
      const ytd = sorted.filter((b) => {
        const d = parseBarDate(b.tradingDate);
        return d >= start && d <= lastD;
      });
      return ytd.length > 0 ? ytd : sorted;
    }
    case "1Y":
      return takeLast(252);
    case "ALL":
    default:
      return sorted;
  }
}

function formatPrice(n: number): string {
  return new Intl.NumberFormat("vi-VN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(n);
}

function formatAxisDate(iso: string, range: ChartRange): string {
  const d = parseBarDate(iso);
  if (range === "1D" || range === "5D" || range === "1M") {
    return `${d.getDate().toString().padStart(2, "0")}/${(d.getMonth() + 1).toString().padStart(2, "0")}`;
  }
  return `${d.getMonth() + 1}/${d.getFullYear().toString().slice(-2)}`;
}

type ChartRow = { date: string; close: number; label: string };

export function PriceChart({
  bars,
  title,
}: {
  bars: PriceBar[];
  title?: string;
}) {
  const [range, setRange] = useState<ChartRange>("3M");
  const gradId = useId().replace(/:/g, "");
  const rootRef = useRef<HTMLDivElement>(null);
  const { isFullscreen, toggleFullscreen } = useChartFullscreen(rootRef);

  const visibleBars = useMemo(() => filterBarsByRange(bars, range), [bars, range]);

  const { lastClose, change, changePct, up } = useMemo(() => {
    const rows: ChartRow[] = visibleBars.map((b) => ({
      date: b.tradingDate.slice(0, 10),
      close: b.closePrice,
      label: b.tradingDate,
    }));
    const last = rows[rows.length - 1]?.close ?? 0;
    const prevClose = rows.length >= 2 ? rows[rows.length - 2]!.close : rows[0]?.close ?? 0;
    const ch = last - prevClose;
    const pct = prevClose !== 0 ? (ch / prevClose) * 100 : 0;
    return { lastClose: last, change: ch, changePct: pct, up: ch >= 0 };
  }, [visibleBars]);

  const { chartData, baseline } = useMemo(() => {
    if (visibleBars.length === 0) {
      return { chartData: [] as ChartRow[], baseline: 0 };
    }
    const sorted = sortBarsAsc(bars);
    const rows: ChartRow[] = visibleBars.map((b) => ({
      date: b.tradingDate.slice(0, 10),
      close: b.closePrice,
      label: b.tradingDate,
    }));

    let baselineVal = rows[0]?.close ?? 0;
    const firstBar = visibleBars[0]!;
    const i = visibleBars.findIndex((b) => b.tradingDate === firstBar.tradingDate);
    if (i > 0) {
      baselineVal = visibleBars[i - 1]!.closePrice;
    } else {
      const fd = firstBar.tradingDate.slice(0, 10);
      const si = sorted.findIndex((b) => b.tradingDate.slice(0, 10) === fd);
      if (si > 0) baselineVal = sorted[si - 1]!.closePrice;
      else baselineVal = firstBar.openPrice;
    }

    return { chartData: rows, baseline: baselineVal };
  }, [bars, visibleBars]);

  const stroke = up ? "#16a34a" : "#dc2626";
  const fillId = `priceFill-${gradId}`;

  if (bars.length === 0) {
    return (
      <p className="rounded-lg border border-dashed border-zinc-300 py-12 text-center text-sm text-zinc-500 dark:border-zinc-600">
        Chưa có dữ liệu giá.
      </p>
    );
  }

  return (
    <div
      ref={rootRef}
      className={
        isFullscreen
          ? "flex h-screen max-h-[100dvh] w-screen flex-col overflow-hidden bg-white dark:bg-zinc-950"
          : "overflow-hidden rounded-xl border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-950"
      }
    >
      <div className="flex flex-col gap-3 border-b border-zinc-100 px-4 py-3 dark:border-zinc-800 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0 text-center sm:text-left">
          {title ? (
            <p className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">{title}</p>
          ) : null}
          <div className="mt-1 flex flex-wrap items-baseline justify-center gap-2 sm:justify-start">
            <span className="text-xl font-semibold tabular-nums tracking-tight text-zinc-900 dark:text-zinc-50">
              {formatPrice(lastClose)}
            </span>
            <span
              className={`text-sm font-medium tabular-nums ${up ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400"}`}
            >
              {up ? "+" : ""}
              {formatPrice(change)} ({up ? "+" : ""}
              {changePct.toFixed(2)}%)
            </span>
          </div>
          <p className="mt-0.5 text-[11px] text-zinc-500 dark:text-zinc-400">
            Đóng cửa · thay đổi so với phiên giao dịch liền trước
            {range === "1D" ? " · EOD: 1D ≈ 5 phiên gần nhất" : ""}
          </p>
        </div>
        <div className="flex flex-col items-stretch gap-2 sm:flex-row sm:items-center sm:justify-end">
          <div className="flex flex-wrap items-center justify-center gap-1.5 sm:justify-end">
            {RANGES.map(({ key, label }) => (
              <button
                key={key}
                type="button"
                onClick={() => setRange(key)}
                className={`rounded-full border px-2.5 py-1 text-xs font-medium transition-colors ${
                  range === key
                    ? "border-sky-500 bg-sky-50 text-sky-800 dark:border-sky-400 dark:bg-sky-950/50 dark:text-sky-200"
                    : "border-zinc-200 bg-zinc-50 text-zinc-600 hover:border-zinc-300 hover:bg-zinc-100 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-400 dark:hover:border-zinc-600"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div
        className={
          isFullscreen
            ? "relative min-h-0 w-full flex-1 px-2 pb-2 pt-1"
            : "relative h-80 w-full px-2 pb-2 pt-1"
        }
      >
        <div className="absolute right-2 top-2 z-20 sm:right-3">
          <ChartFullscreenIconButton
            isFullscreen={isFullscreen}
            onToggle={() => {
              void toggleFullscreen();
            }}
          />
        </div>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 12, right: 16, left: 4, bottom: 4 }}>
            <defs>
              <linearGradient id={fillId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={stroke} stopOpacity={0.28} />
                <stop offset="100%" stopColor={stroke} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
              className="stroke-zinc-200 dark:stroke-zinc-800"
            />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 10, fill: "currentColor" }}
              className="text-zinc-500"
              tickFormatter={(v) => formatAxisDate(String(v), range)}
              interval="preserveStartEnd"
              minTickGap={28}
            />
            <YAxis
              domain={["auto", "auto"]}
              tick={{ fontSize: 10, fill: "currentColor" }}
              className="text-zinc-500"
              width={56}
              tickFormatter={(v) => formatPrice(Number(v))}
            />
            <Tooltip
              contentStyle={{
                borderRadius: "8px",
                border: "1px solid rgb(228 228 231)",
                fontSize: "12px",
              }}
              labelFormatter={(label) => `Ngày: ${label}`}
              formatter={(value: number | string) => [formatPrice(Number(value)), "Đóng cửa"]}
            />
            {chartData.length > 0 && Number.isFinite(baseline) && baseline > 0 ? (
              <ReferenceLine
                y={baseline}
                stroke="#ca8a04"
                strokeDasharray="5 5"
                strokeWidth={1}
                strokeOpacity={0.85}
              />
            ) : null}
            <Area
              type="monotone"
              dataKey="close"
              stroke={stroke}
              strokeWidth={2}
              fill={`url(#${fillId})`}
              dot={false}
              activeDot={{ r: 6, stroke: stroke, strokeWidth: 2, fill: "#fff" }}
            />
            {chartData.length > 0 ? (
              <ReferenceDot
                x={chartData[chartData.length - 1]!.date}
                y={chartData[chartData.length - 1]!.close}
                r={5}
                fill={stroke}
                stroke="#fff"
                strokeWidth={2}
              />
            ) : null}
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
