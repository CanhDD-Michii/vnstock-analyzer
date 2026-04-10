export function SectionCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-2xl border border-zinc-200/90 bg-white/90 p-5 shadow-sm shadow-zinc-900/[0.03] backdrop-blur-sm dark:border-zinc-800 dark:bg-zinc-950/70 dark:shadow-black/20">
      <h2 className="mb-4 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
        <span
          className="h-1.5 w-1.5 shrink-0 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500"
          aria-hidden
        />
        {title}
      </h2>
      <div className="text-sm text-zinc-800 dark:text-zinc-200">{children}</div>
    </section>
  );
}
