/** Một dòng trong bảng hiệu suất giá (mã thật trong DB). */
export type MarketIndexRow = {
  code: string;
  /** Tên công ty (hiển thị phụ) */
  name?: string;
  /** Giá đóng cửa phiên gần nhất */
  price: number | null;
  /** % thay đổi: ngày, tuần, tháng, quý, YTD, 1 năm — null nếu thiếu dữ liệu */
  d: number | null;
  w: number | null;
  m: number | null;
  q: number | null;
  ytd: number | null;
  y: number | null;
  highlight?: boolean;
};
