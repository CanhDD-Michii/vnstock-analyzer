import { SectionCard } from "@/components/ui/SectionCard";

/** Khung section trang mã — thay bằng header / chart / chỉ số khi triển khai. */
export function StockPagePlaceholder({ ticker }: { ticker: string }) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <SectionCard title="Thông tin mã">{ticker}</SectionCard>
      <SectionCard title="Biểu đồ giá">Chưa triển khai</SectionCard>
      <SectionCard title="Chỉ báo kỹ thuật">Chưa triển khai</SectionCard>
      <SectionCard title="Phân tích AI">Chưa triển khai</SectionCard>
    </div>
  );
}
