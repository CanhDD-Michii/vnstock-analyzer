import type { MarketIndexRow } from "@/types/market-index";

/**
 * Dữ liệu mẫu minh họa — thay bằng fetch API khi có nguồn chỉ số thời gian thực.
 * Cấu trúc khớp bảng tham chiếu (Giá, D, W, M, Q, YTD, Y).
 */
export const DEMO_MARKET_INDICES: MarketIndexRow[] = [
  {
    code: "VN-Index",
    price: 1736.68,
    d: -0.48,
    w: -1.13,
    m: 2.47,
    q: -3.2,
    ytd: 4.12,
    y: 8.35,
    highlight: true,
  },
  { code: "HNX", price: 234.12, d: 0.32, w: -0.85, m: 1.1, q: 2.4, ytd: -1.2, y: 5.6 },
  { code: "UPCOM", price: 91.45, d: -0.21, w: 0.44, m: -0.9, q: 1.8, ytd: 3.1, y: -2.3 },
  { code: "VN30", price: 1782.05, d: -0.52, w: -1.05, m: 2.1, q: -2.8, ytd: 3.9, y: 7.8 },
  { code: "HNX30", price: 412.88, d: 0.18, w: -0.62, m: 0.95, q: 1.5, ytd: -0.8, y: 4.2 },
  { code: "VNMidcap", price: 1623.4, d: -0.35, w: 0.12, m: 1.65, q: -1.1, ytd: 5.4, y: 6.1 },
  { code: "VN100", price: 1056.2, d: -0.41, w: -0.78, m: 1.88, q: -2.2, ytd: 4.0, y: 7.2 },
  { code: "VNSmallcap", price: 1489.33, d: 0.22, w: 1.05, m: -0.45, q: 2.9, ytd: 6.7, y: -1.4 },
  { code: "VNAllshare", price: 1688.9, d: -0.39, w: -0.95, m: 2.0, q: -2.5, ytd: 3.8, y: 7.9 },
  { code: "VS100", price: 892.15, d: -0.28, w: 0.33, m: 1.2, q: -0.9, ytd: 2.6, y: 4.9 },
  { code: "VN30F1M", price: 1785.0, d: -0.55, w: -1.02, m: 2.05, q: -2.7, ytd: 3.85, y: 7.75 },
  { code: "VS-LargeCap", price: 1120.4, d: -0.44, w: -0.88, m: 1.92, q: -2.1, ytd: 3.95, y: 7.5 },
  { code: "VS-MidCap", price: 1345.67, d: 0.08, w: 0.55, m: 0.72, q: 1.15, ytd: 4.8, y: 5.3 },
  { code: "VS-SmallCap", price: 1567.22, d: 0.31, w: 1.12, m: -0.38, q: 3.05, ytd: 7.1, y: -0.9 },
];

export const DEMO_INDICES_UPDATED_AT = "09/04/2026 — 15:03";
