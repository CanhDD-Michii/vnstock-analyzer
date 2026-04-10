import Link from "next/link";
import { ROUTES } from "@/constants/routes";

export function AppLogo({ className = "" }: { className?: string }) {
  return (
    <Link
      href={ROUTES.home}
      className={`group flex items-center gap-2.5 text-sm font-semibold tracking-tight text-zinc-900 transition hover:opacity-90 dark:text-white ${className}`}
    >
      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 text-xs font-bold text-white shadow-md shadow-emerald-600/25 ring-1 ring-white/25 transition group-hover:shadow-lg group-hover:shadow-emerald-600/30 dark:ring-white/10">
        VN
      </span>
      <span className="leading-tight">
        Stock{" "}
        <span className="font-normal text-zinc-500 dark:text-zinc-400">Analyzer</span>
      </span>
    </Link>
  );
}
