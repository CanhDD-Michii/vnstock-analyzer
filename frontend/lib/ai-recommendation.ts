/** Chuẩn hóa mã khuyến nghị (rule-based / OpenAI) → nhãn tiếng Việt cho UI. */

const LABELS: Record<string, string> = {
  BUY: "Nên mua",
  SELL: "Nên bán",
  STRONG_BUY: "Mua mạnh",
  STRONG_SELL: "Bán mạnh",
  HOLD: "Nên giữ",
  WATCH: "Theo dõi",
  AVOID: "Tránh / không nên mua",
  NEUTRAL: "Trung lập",
};

export function formatAiRecommendationVi(raw: string | null | undefined): string {
  if (raw == null) return "—";
  const t = String(raw).trim();
  if (!t) return "—";
  const key = t.toUpperCase().replace(/\s+/g, "_");
  if (LABELS[key]) return LABELS[key];
  const firstToken = t.split(/[\s,|]+/)[0]?.toUpperCase() ?? "";
  if (firstToken && LABELS[firstToken]) return LABELS[firstToken];
  return t;
}
