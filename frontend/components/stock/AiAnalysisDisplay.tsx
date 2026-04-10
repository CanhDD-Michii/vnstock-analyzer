"use client";

import type { ReactNode } from "react";
import { formatAiRecommendationVi } from "@/lib/ai-recommendation";

function coerceAnalysisText(val: unknown): string {
  if (val == null) return "";
  if (typeof val === "string") return val;
  if (typeof val === "number" || typeof val === "boolean") return String(val);
  if (Array.isArray(val)) {
    return val
      .map((x) => coerceAnalysisText(x).trim())
      .filter(Boolean)
      .join("\n");
  }
  if (typeof val === "object") {
    const parts: string[] = [];
    for (const [k, v] of Object.entries(val as Record<string, unknown>)) {
      const body = coerceAnalysisText(v).trim();
      if (body) parts.push(`${k}\n${body}`);
    }
    return parts.join("\n\n");
  }
  try {
    return JSON.stringify(val);
  } catch {
    return String(val);
  }
}

function textField(obj: Record<string, unknown>, key: string): string {
  return coerceAnalysisText(obj[key]);
}

function stringList(obj: Record<string, unknown>, key: string): string[] {
  const v = obj[key];
  if (!Array.isArray(v)) return [];
  return v
    .map((item) => coerceAnalysisText(item).trim())
    .filter((s) => s.length > 0);
}

function normalizeRecCode(raw: string): string {
  return raw.toUpperCase().replace(/\s+/g, "_");
}

function recommendationVisual(raw: string): {
  border: string;
  gradient: string;
  title: string;
  chip: string;
} {
  const u = normalizeRecCode(raw);
  if (u.includes("STRONG_BUY") || u === "BUY") {
    return {
      border: "border-emerald-400/55 dark:border-emerald-500/35",
      gradient:
        "bg-gradient-to-br from-emerald-50/95 via-white to-teal-50/40 dark:from-emerald-950/45 dark:via-zinc-950 dark:to-teal-950/25",
      title: "text-emerald-900 dark:text-emerald-100",
      chip: "bg-emerald-600 text-white shadow-sm dark:bg-emerald-500",
    };
  }
  if (u.includes("STRONG_SELL") || u === "SELL") {
    return {
      border: "border-rose-400/55 dark:border-rose-500/35",
      gradient:
        "bg-gradient-to-br from-rose-50/95 via-white to-orange-50/35 dark:from-rose-950/40 dark:via-zinc-950 dark:to-orange-950/20",
      title: "text-rose-900 dark:text-rose-100",
      chip: "bg-rose-600 text-white shadow-sm dark:bg-rose-500",
    };
  }
  if (u === "HOLD") {
    return {
      border: "border-sky-400/50 dark:border-sky-500/35",
      gradient:
        "bg-gradient-to-br from-sky-50/90 via-white to-zinc-50/40 dark:from-sky-950/35 dark:via-zinc-950 dark:to-zinc-900/40",
      title: "text-sky-900 dark:text-sky-100",
      chip: "bg-sky-600 text-white shadow-sm dark:bg-sky-500",
    };
  }
  if (u === "WATCH" || u === "NEUTRAL") {
    return {
      border: "border-amber-400/50 dark:border-amber-500/30",
      gradient:
        "bg-gradient-to-br from-amber-50/90 via-white to-zinc-50/40 dark:from-amber-950/30 dark:via-zinc-950 dark:to-zinc-900/40",
      title: "text-amber-950 dark:text-amber-100",
      chip: "bg-amber-600 text-white shadow-sm dark:bg-amber-600",
    };
  }
  if (u === "AVOID") {
    return {
      border: "border-zinc-400/60 dark:border-zinc-500/40",
      gradient:
        "bg-gradient-to-br from-zinc-100/90 via-white to-zinc-50/50 dark:from-zinc-900/50 dark:via-zinc-950 dark:to-zinc-900/40",
      title: "text-zinc-900 dark:text-zinc-100",
      chip: "bg-zinc-700 text-white shadow-sm dark:bg-zinc-600",
    };
  }
  return {
    border: "border-zinc-200 dark:border-zinc-600",
    gradient: "bg-zinc-50/80 dark:bg-zinc-900/50",
    title: "text-zinc-900 dark:text-zinc-100",
    chip: "bg-zinc-600 text-white dark:bg-zinc-500",
  };
}

function Section({
  title,
  children,
  className = "",
}: {
  title: string;
  children: ReactNode;
  className?: string;
}) {
  if (children == null || children === false) return null;
  return (
    <section
      className={`rounded-xl border border-zinc-200/90 bg-white/90 p-4 shadow-sm dark:border-zinc-700/90 dark:bg-zinc-950/45 ${className}`}
    >
      <h3 className="mb-2.5 border-b border-zinc-100 pb-2 text-[11px] font-semibold uppercase tracking-wider text-emerald-700 dark:border-zinc-800 dark:text-emerald-400/95">
        {title}
      </h3>
      <div className="text-sm leading-relaxed text-zinc-800 dark:text-zinc-200">{children}</div>
    </section>
  );
}

function BulletList({ items }: { items: string[] }) {
  if (items.length === 0) return null;
  return (
    <ul className="list-none space-y-2.5 pl-0">
      {items.map((item, i) => (
        <li
          key={`${i}-${item.slice(0, 24)}`}
          className="relative pl-4 text-sm leading-relaxed text-zinc-800 before:absolute before:left-0 before:top-[0.55em] before:h-1.5 before:w-1.5 before:rounded-full before:bg-emerald-500/80 dark:text-zinc-200 dark:before:bg-emerald-400/70"
        >
          {item}
        </li>
      ))}
    </ul>
  );
}

export function AiAnalysisDisplay({ ai }: { ai: Record<string, unknown> }) {
  const summary = textField(ai, "summary").trim();
  const fundamental = textField(ai, "fundamental_analysis").trim();
  const technical = textField(ai, "technical_analysis").trim();
  const conclusion = textField(ai, "conclusion").trim();
  const recRaw = textField(ai, "recommendation").trim();
  const risks = stringList(ai, "risks");
  const gaps = stringList(ai, "fundamental_data_gaps");
  const wishlist = stringList(ai, "fundamental_wishlist");

  const vis = recommendationVisual(recRaw);
  const recLabel = formatAiRecommendationVi(recRaw);

  const hasAny =
    summary ||
    fundamental ||
    technical ||
    conclusion ||
    recRaw ||
    risks.length > 0 ||
    gaps.length > 0 ||
    wishlist.length > 0;

  if (!hasAny) {
    return <p className="mt-3 text-sm text-zinc-500">Chưa có nội dung phân tích AI.</p>;
  }

  return (
    <div className="mt-4 space-y-4">
      {recRaw ? (
        <div
          className={`rounded-xl border-2 p-4 ${vis.border} ${vis.gradient}`}
        >
          <p className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
            Khuyến nghị
          </p>
          <div className="mt-2 flex flex-wrap items-center gap-3">
            <span
              className={`inline-flex rounded-lg px-3 py-1.5 text-sm font-bold tracking-tight ${vis.chip}`}
            >
              {recRaw.toUpperCase()}
            </span>
            <span className={`text-base font-semibold ${vis.title}`}>{recLabel}</span>
          </div>
        </div>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-2">
        {summary ? (
          <Section title="Tóm tắt (4 trục)" className="lg:col-span-2">
            <p className="whitespace-pre-wrap">{summary}</p>
          </Section>
        ) : null}

        {fundamental ? (
          <Section title="Cơ bản">
            <p className="whitespace-pre-wrap">{fundamental}</p>
          </Section>
        ) : null}

        {technical ? (
          <Section title="Kỹ thuật" className={fundamental ? "" : "lg:col-span-2"}>
            <p className="whitespace-pre-wrap">{technical}</p>
          </Section>
        ) : null}
      </div>

      {risks.length > 0 ? (
        <Section title="Rủi ro">
          <BulletList items={risks} />
        </Section>
      ) : null}

      {conclusion ? (
        <Section title="Kết luận">
          <p className="whitespace-pre-wrap rounded-lg bg-zinc-50/80 px-3 py-2.5 dark:bg-zinc-900/60">
            {conclusion}
          </p>
        </Section>
      ) : null}

      {(gaps.length > 0 || wishlist.length > 0) && (
        <div className="grid gap-4 md:grid-cols-2">
          {gaps.length > 0 ? (
            <Section title="Khoảng trống dữ liệu">
              <BulletList items={gaps} />
            </Section>
          ) : null}
          {wishlist.length > 0 ? (
            <Section title="Gợi ý bổ sung dữ liệu">
              <BulletList items={wishlist} />
            </Section>
          ) : null}
        </div>
      )}
    </div>
  );
}
