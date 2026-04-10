import { fetchJson } from "@/services/api-client";
import type {
  AnalysisDetail,
  AnalysisHistoryItem,
  RunAnalysisResult,
} from "@/types/analysis";

export async function runAnalysis(ticker: string): Promise<RunAnalysisResult> {
  const res = await fetchJson<RunAnalysisResult>(
    `/api/v1/analysis/${encodeURIComponent(ticker)}`,
    { method: "POST" },
  );
  return res.data;
}

export async function listAnalysisHistory(): Promise<AnalysisHistoryItem[]> {
  const res = await fetchJson<AnalysisHistoryItem[]>("/api/v1/analysis/history");
  return res.data;
}

export async function getAnalysisDetail(id: number): Promise<AnalysisDetail> {
  const res = await fetchJson<AnalysisDetail>(
    `/api/v1/analysis/history/${id}`,
  );
  return res.data;
}
