import { SectionCard } from "@/components/ui/SectionCard";

export function AdminPanelPlaceholder() {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <SectionCard title="Users">Chưa triển khai</SectionCard>
      <SectionCard title="Mã CK">Chưa triển khai</SectionCard>
      <SectionCard title="Crawl">Chưa triển khai</SectionCard>
      <SectionCard title="Prompt AI">Chưa triển khai</SectionCard>
    </div>
  );
}
