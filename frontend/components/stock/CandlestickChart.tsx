"use client";

import type { MouseEvent } from "react";
import { useCallback, useLayoutEffect, useMemo, useRef, useState } from "react";
import type { PriceBar } from "@/types/stock";
import {
  type ChartRange,
  filterBarsByRange,
} from "@/components/stock/PriceChart";
import { ChartFullscreenIconButton } from "@/components/stock/ChartFullscreenIconButton";
import { useChartFullscreen } from "@/components/stock/useChartFullscreen";

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

function formatPrice(n: number): string {
  return new Intl.NumberFormat("vi-VN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(n);
}

function formatAxisDate(iso: string, range: ChartRange): string {
  const d = new Date(`${iso.slice(0, 10)}T12:00:00`);
  if (range === "1D" || range === "5D" || range === "1M") {
    return `${d.getDate().toString().padStart(2, "0")}/${(d.getMonth() + 1).toString().padStart(2, "0")}`;
  }
  return `${d.getMonth() + 1}/${d.getFullYear().toString().slice(-2)}`;
}

const MARGIN = { top: 12, right: 12, bottom: 28, left: 56 };

export function CandlestickChart({
  bars,
  title,
}: {
  bars: PriceBar[];
  title?: string;
}) {
  const [range, setRange] = useState<ChartRange>("3M");
  const rootRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const { isFullscreen, toggleFullscreen } = useChartFullscreen(rootRef);
  const [size, setSize] = useState({ w: 640, h: 320 });
  const [hover, setHover] = useState<{
    bar: PriceBar;
    px: number;
    py: number;
  } | null>(null);

  useLayoutEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(() => {
      setSize({ w: Math.max(200, el.clientWidth), h: Math.max(200, el.clientHeight) });
    });
    ro.observe(el);
    setSize({ w: Math.max(200, el.clientWidth), h: Math.max(200, el.clientHeight) });
    return () => ro.disconnect();
  }, []);

  const displayed = useMemo(() => filterBarsByRange(bars, range), [bars, range]);

  const layout = useMemo(() => {
    const w = size.w;
    const h = size.h;
    const innerW = w - MARGIN.left - MARGIN.right;
    const innerH = h - MARGIN.top - MARGIN.bottom;
    if (displayed.length === 0 || innerW <= 0 || innerH <= 0) {
      return {
        w,
        h,
        innerW,
        innerH,
        yScale: () => MARGIN.top,
        slotW: 1,
        bodyW: 0,
        gap: 0,
        lo: 0,
        hi: 1,
        span: 1,
        candles: [] as PriceBar[],
      };
    }
    let minP = Infinity;
    let maxP = -Infinity;
    for (const b of displayed) {
      minP = Math.min(minP, b.lowPrice);
      maxP = Math.max(maxP, b.highPrice);
    }
    const pad = Math.max((maxP - minP) * 0.06, maxP * 0.002, 0.01);
    const lo = minP - pad;
    const hi = maxP + pad;
    const span = Math.max(hi - lo, 1e-9);
    const yScale = (p: number) => MARGIN.top + ((hi - p) / span) * innerH;
    const gap = Math.max(1, Math.min(4, innerW / displayed.length / 12));
    const slotW = innerW / displayed.length;
    const bodyW = Math.max(2, Math.min(slotW - gap, slotW * 0.72));

    return { w, h, innerW, innerH, yScale, slotW, bodyW, gap, lo, hi, span, candles: displayed };
  }, [displayed, size]);

  const onSvgMove = useCallback(
    (e: MouseEvent<SVGSVGElement>) => {
      const svgEl = e.currentTarget;
      const cRect = containerRef.current?.getBoundingClientRect() ?? svgEl.getBoundingClientRect();
      const ctm = svgEl.getScreenCTM();
      if (!ctm) {
        setHover(null);
        return;
      }
      const pt = svgEl.createSVGPoint();
      pt.x = e.clientX;
      pt.y = e.clientY;
      const p = pt.matrixTransform(ctm.inverse());
      const x = p.x;
      if (x < MARGIN.left || x > layout.w - MARGIN.right || displayed.length === 0) {
        setHover(null);
        return;
      }
      const rel = x - MARGIN.left;
      const idx = Math.min(
        displayed.length - 1,
        Math.max(0, Math.floor(rel / layout.slotW)),
      );
      const bar = displayed[idx]!;
      setHover({
        bar,
        px: e.clientX - cRect.left,
        py: e.clientY - cRect.top,
      });
    },
    [layout.w, layout.slotW, displayed],
  );

  if (bars.length === 0) {
    return (
      <p className="rounded-lg border border-dashed border-zinc-300 py-12 text-center text-sm text-zinc-500 dark:border-zinc-600">
        Chưa có dữ liệu giá.
      </p>
    );
  }

  const bull = "#16a34a";
  const bear = "#dc2626";

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
          <p className="mt-0.5 text-[11px] text-zinc-500 dark:text-zinc-400">
            Mở · cao · thấp · đóng (OHLC) — mỗi cột là một phiên
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
                    ? "border-amber-500 bg-amber-50 text-amber-900 dark:border-amber-400 dark:bg-amber-950/50 dark:text-amber-200"
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
        ref={containerRef}
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
        <svg
          width="100%"
          height="100%"
          viewBox={`0 0 ${layout.w} ${layout.h}`}
          preserveAspectRatio="xMidYMid meet"
          role="img"
          aria-label={`Biểu đồ nến ${title ?? ""}`}
          onMouseLeave={() => setHover(null)}
          onMouseMove={onSvgMove}
        >
          {/* Grid ngang nhẹ */}
          {layout.candles.length > 0
            ? [0, 0.25, 0.5, 0.75, 1].map((t) => {
                const y = MARGIN.top + t * layout.innerH;
                const price = layout.hi - t * (layout.hi - layout.lo);
                return (
                  <g key={t}>
                    <line
                      x1={MARGIN.left}
                      x2={layout.w - MARGIN.right}
                      y1={y}
                      y2={y}
                      stroke="currentColor"
                      strokeOpacity={0.12}
                      className="text-zinc-400"
                      strokeDasharray="4 4"
                    />
                    <text
                      x={MARGIN.left - 8}
                      y={y + 4}
                      textAnchor="end"
                      className="fill-zinc-500"
                      style={{ fontSize: 10 }}
                    >
                      {formatPrice(price)}
                    </text>
                  </g>
                );
              })
            : null}

          {layout.candles.map((b, i) => {
            const cx = MARGIN.left + i * layout.slotW + layout.slotW / 2;
            const yH = layout.yScale(b.highPrice);
            const yL = layout.yScale(b.lowPrice);
            const yO = layout.yScale(b.openPrice);
            const yC = layout.yScale(b.closePrice);
            const top = Math.min(yO, yC);
            const bot = Math.max(yO, yC);
            const up = b.closePrice >= b.openPrice;
            const color = up ? bull : bear;
            const bodyH = Math.max(bot - top, 1);

            return (
              <g key={`${b.tradingDate}-${i}`}>
                <line
                  x1={cx}
                  x2={cx}
                  y1={yH}
                  y2={yL}
                  stroke={color}
                  strokeWidth={1.25}
                />
                <rect
                  x={cx - layout.bodyW / 2}
                  y={top}
                  width={layout.bodyW}
                  height={bodyH}
                  fill={color}
                  fillOpacity={up ? 0.85 : 0.95}
                  stroke={color}
                  strokeWidth={1}
                />
              </g>
            );
          })}

          {/* Trục X — nhãn thưa */}
          {layout.candles.map((b, i) => {
            const n = layout.candles.length;
            const step = Math.max(1, Math.ceil(n / 9));
            const show = i === 0 || i === n - 1 || i % step === 0;
            if (!show) return null;
            const cx = MARGIN.left + i * layout.slotW + layout.slotW / 2;
            return (
              <text
                key={`lbl-${b.tradingDate}-${i}`}
                x={cx}
                y={layout.h - 8}
                textAnchor="middle"
                className="fill-zinc-500"
                style={{ fontSize: 9 }}
              >
                {formatAxisDate(b.tradingDate, range)}
              </text>
            );
          })}
        </svg>

        {hover ? (
          <div
            className="pointer-events-none absolute z-10 max-w-[220px] rounded-lg border border-zinc-200 bg-white/95 px-3 py-2 text-xs shadow-lg dark:border-zinc-600 dark:bg-zinc-900/95"
            style={{
              left: Math.min(
                Math.max(hover.px + 12, 8),
                (containerRef.current?.clientWidth ?? 240) - 228,
              ),
              top: Math.max(hover.py - 8, 8),
            }}
          >
            <p className="font-medium text-zinc-900 dark:text-zinc-100">
              {hover.bar.tradingDate.slice(0, 10)}
            </p>
            <ul className="mt-1 space-y-0.5 tabular-nums text-zinc-600 dark:text-zinc-300">
              <li>Mở: {formatPrice(hover.bar.openPrice)}</li>
              <li>Cao: {formatPrice(hover.bar.highPrice)}</li>
              <li>Thấp: {formatPrice(hover.bar.lowPrice)}</li>
              <li>Đóng: {formatPrice(hover.bar.closePrice)}</li>
            </ul>
          </div>
        ) : null}
      </div>
    </div>
  );
}
