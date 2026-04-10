export interface AnalysisHistoryItem {
  id: number;
  stockTicker: string;
  analysisDate: string;
  fundamentalScore: number | null;
  technicalScore: number | null;
  riskScore: number | null;
  aiRecommendation: string | null;
  createdAt: string;
}

export interface AnalysisDetail extends AnalysisHistoryItem {
  aiSummary: string | null;
  aiFundamentalAnalysis: string | null;
  aiTechnicalAnalysis: string | null;
  aiRisksJson: string[] | null;
  aiConclusion: string | null;
  engineOutputJson: Record<string, unknown> | null;
  rawAiResponseJson: Record<string, unknown> | null;
}

export interface RunAnalysisResult {
  resultId: number;
  engine: Record<string, unknown>;
  ai: Record<string, unknown>;
}
