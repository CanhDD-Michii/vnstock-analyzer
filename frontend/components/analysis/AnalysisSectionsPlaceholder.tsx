import { SectionCard } from "@/components/ui/SectionCard";

/** Placeholder các section output AI (summary, fundamental, technical, risks…). */
export function AnalysisSectionsPlaceholder() {
  return (
    <div className="grid gap-4">
      <SectionCard title="Tóm tắt">—</SectionCard>
      <SectionCard title="Phân tích cơ bản">—</SectionCard>
      <SectionCard title="Phân tích kỹ thuật">—</SectionCard>
      <SectionCard title="Rủi ro">—</SectionCard>
      <SectionCard title="Kết luận & khuyến nghị">—</SectionCard>
    </div>
  );
}
