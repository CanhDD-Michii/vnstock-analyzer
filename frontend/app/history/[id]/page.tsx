"use client";

import { ChevronLeft } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { PageShell } from "@/components/common/PageShell";
import { SectionCard } from "@/components/ui/SectionCard";
import { ROUTES } from "@/constants/routes";
import { ApiClientError } from "@/services/api-client";
import * as analysisApi from "@/services/analysis.service";
import type { AnalysisDetail } from "@/types/analysis";

const backLinkClass =
  "mb-6 inline-flex items-center gap-2 rounded-xl border border-zinc-200/90 bg-white/80 px-4 py-2.5 text-sm font-medium text-zinc-700 shadow-sm transition hover:border-emerald-300/60 hover:bg-emerald-50/50 hover:text-emerald-800 dark:border-zinc-700 dark:bg-zinc-900/60 dark:text-zinc-200 dark:hover:border-emerald-500/35 dark:hover:bg-emerald-950/30 dark:hover:text-emerald-100";

export default function HistoryDetailPage() {
  const params = useParams();
  const id = Number(params.id);
  const [row, setRow] = useState<AnalysisDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [needsLogin, setNeedsLogin] = useState(false);

  useEffect(() => {
    if (!Number.isFinite(id)) return;
    void (async () => {
      try {
        const d = await analysisApi.getAnalysisDetail(id);
        setRow(d);
        setNeedsLogin(false);
        setError(null);
      } catch (e: unknown) {
        if (e instanceof ApiClientError && e.status === 401) {
          setNeedsLogin(true);
          setError(null);
          setRow(null);
        } else {
          setNeedsLogin(false);
          setError(e instanceof Error ? e.message : "Không tải được chi tiết");
        }
      }
    })();
  }, [id]);

  return (
    <PageShell
      title="Chi tiết phân tích"
      description={row ? `${row.stockTicker} · ${row.analysisDate}` : undefined}
    >
      <Link href={ROUTES.history} className={backLinkClass}>
        <ChevronLeft className="h-4 w-4 shrink-0" strokeWidth={2} aria-hidden />
        Quay lại lịch sử
      </Link>
      {needsLogin && (
        <p className="mb-4 rounded-xl border border-amber-200/90 bg-amber-50/90 px-4 py-3 text-sm text-amber-900 dark:border-amber-900/40 dark:bg-amber-950/40 dark:text-amber-100">
          Vui lòng{" "}
          <Link
            href={ROUTES.login}
            className="font-semibold text-amber-800 underline decoration-amber-600/40 underline-offset-2 dark:text-amber-200"
          >
            đăng nhập
          </Link>{" "}
          để xem chi tiết phân tích.
        </p>
      )}
      {error && (
        <p className="mb-4 rounded-xl border border-red-200 bg-red-50/90 px-4 py-3 text-sm text-red-800 dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-200">
          {error}
        </p>
      )}
      {row && (
        <div className="space-y-5">
          <SectionCard title="Tóm tắt">
            <p className="whitespace-pre-wrap text-sm leading-relaxed">{row.aiSummary ?? "—"}</p>
          </SectionCard>
          <SectionCard title="Cơ bản / Kỹ thuật">
            <p className="whitespace-pre-wrap text-sm leading-relaxed">{row.aiFundamentalAnalysis ?? "—"}</p>
            <p className="mt-4 whitespace-pre-wrap text-sm leading-relaxed border-t border-zinc-100 pt-4 dark:border-zinc-800">
              {row.aiTechnicalAnalysis ?? "—"}
            </p>
          </SectionCard>
          <SectionCard title="Rủi ro">
            <ul className="list-inside list-disc space-y-1 text-sm leading-relaxed">
              {(row.aiRisksJson ?? []).map((r, i) => (
                <li key={i}>{String(r)}</li>
              ))}
            </ul>
          </SectionCard>
          <SectionCard title="Kết luận">
            <p className="text-sm leading-relaxed">{row.aiConclusion ?? "—"}</p>
            <p className="mt-4 rounded-lg border border-emerald-200/80 bg-emerald-50/50 px-4 py-3 text-sm dark:border-emerald-900/40 dark:bg-emerald-950/30">
              <span className="font-semibold text-emerald-900 dark:text-emerald-100">Khuyến nghị:</span>{" "}
              <span className="text-zinc-800 dark:text-zinc-200">{row.aiRecommendation ?? "—"}</span>
            </p>
          </SectionCard>
        </div>
      )}
    </PageShell>
  );
}
