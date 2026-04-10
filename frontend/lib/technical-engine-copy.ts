/**
 * Nhãn & mô tả tiếng Việt cho output engine kỹ thuật (khớp backend indicators pipeline).
 * Khóa API thường là snake_case (object JSON thô từ BE).
 */

export const MARKET_STATE_TITLE_VI: Record<string, string> = {
  "Strong Uptrend": "Xu hướng tăng mạnh",
  Downtrend: "Xu hướng giảm",
  "Oversold Rebound Candidate": "Ứng viên hồi sau vùng quá bán",
  "Weak Uptrend": "Xu hướng tăng yếu",
  "Breakout Setup": "Thiết lập breakout",
  "Sideway Accumulation": "Tích lũy đi ngang",
  "Distribution / Weakening": "Phân phối / suy yếu",
  "Neutral / Mixed": "Trung tính / tín hiệu hỗn hợp",
};

export type ScoreMeta = { label: string; help: string };

/** Thứ tự hiển thị ưu tiên */
export const SCORE_DISPLAY_ORDER: string[] = [
  "technical_score",
  "trend_score",
  "momentum_score",
  "volume_score",
  "breakout_score",
  "volatility_score",
  "risk_score",
];

export const SCORE_HELP_VI: Record<string, ScoreMeta> = {
  technical_score: {
    label: "Điểm kỹ thuật tổng hợp",
    help: "Trung bình bốn mảng: xu hướng, động lượng, thanh khoản và breakout (thang 0–100, cao hơn thường thuận chiều tích cực hơn).",
  },
  trend_score: {
    label: "Điểm xu hướng",
    help: "Đánh giá hướng giá qua vị trí so với các đường MA, độ dốc xu hướng và vùng gần đỉnh gần nhất.",
  },
  momentum_score: {
    label: "Điểm động lượng",
    help: "Sức mạnh nhịp giá gần đây (RSI, MACD, ROC, Stochastic, vị trí đóng cửa trong biên độ phiên).",
  },
  volume_score: {
    label: "Điểm thanh khoản / dòng tiền",
    help: "Mức khớp lệnh so với trung bình, xác nhận tăng/giảm có kèm volume và tín hiệu breakout có hỗ trợ volume.",
  },
  breakout_score: {
    label: "Điểm breakout",
    help: "Mức độ giá áp sát vùng hỗ trợ/kháng cự và khả năng vượt biên (theo engine nội bộ).",
  },
  volatility_score: {
    label: "Điểm biến động (phù hợp)",
    help: "Biến động “vừa phải” (ATR, Bollinger) được ưu tiên; quá trầm hoặc quá hỗn loạn bị điều chỉnh điểm.",
  },
  risk_score: {
    label: "Điểm rủi ro",
    help: "Lưu ý: điểm càng cao thì rủi ro càng lớn (drawdown, biến động bất thuận…), không phải “điểm an toàn”.",
  },
};

export function normalizeMarketState(raw: unknown): {
  titleVi: string;
  titleEn: string;
  description: string;
} | null {
  if (!raw || typeof raw !== "object") return null;
  const o = raw as Record<string, unknown>;
  const en = String(o.primary_state ?? o.primaryState ?? "");
  const description = String(o.description ?? "");
  if (!en && !description) return null;
  return {
    titleEn: en,
    titleVi: (en && MARKET_STATE_TITLE_VI[en]) || en || "Trạng thái thị trường",
    description,
  };
}

export function orderedScoreEntries(
  scores: Record<string, number>,
  extraTop?: Record<string, number>,
): { key: string; value: number; meta: ScoreMeta }[] {
  const merged: Record<string, number> = { ...scores };
  if (extraTop) {
    for (const [k, v] of Object.entries(extraTop)) {
      if (v !== undefined && Number.isFinite(v)) merged[k] = v;
    }
  }
  const seen = new Set<string>();
  const out: { key: string; value: number; meta: ScoreMeta }[] = [];

  const pushKey = (key: string) => {
    if (seen.has(key) || !(key in merged)) return;
    seen.add(key);
    const value = merged[key]!;
    const meta = SCORE_HELP_VI[key] ?? {
      label: key.replace(/_/g, " "),
      help: "Chỉ số từ engine (chưa có mô tả chi tiết).",
    };
    out.push({ key, value, meta });
  };

  for (const key of SCORE_DISPLAY_ORDER) pushKey(key);
  for (const key of Object.keys(merged).sort()) {
    if (!seen.has(key)) pushKey(key);
  }
  return out;
}
