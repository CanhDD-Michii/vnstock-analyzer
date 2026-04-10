"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { AppLogo } from "@/components/common/AppLogo";
import { UserAvatarMenu } from "@/components/common/UserAvatarMenu";
import { ROUTES } from "@/constants/routes";
import { useAuth } from "@/hooks/useAuth";
import { isNavActive } from "@/lib/nav-active";

const navLinkBase =
  "rounded-lg px-3 py-2 text-sm font-medium transition focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500/50 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-50 dark:focus-visible:ring-offset-zinc-950";

export function PageShell({
  title,
  description,
  children,
}: {
  title: string;
  /** Mô tả ngắn dưới tiêu đề trang (tùy chọn) */
  description?: string;
  children: React.ReactNode;
}) {
  const { user, logout, loading } = useAuth();
  const pathname = usePathname() || "";

  const mainNav = [
    { href: ROUTES.stocks, label: "Cổ phiếu" },
    { href: ROUTES.history, label: "Lịch sử phân tích" },
    ...(user?.role === "admin"
      ? [
          { href: ROUTES.adminUsers, label: "Người dùng" },
          { href: ROUTES.stockSymbolManagement, label: "Quản lý mã" },
        ]
      : []),
  ];

  return (
    <div className="relative min-h-screen overflow-x-hidden bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
      <div
        className="pointer-events-none absolute inset-0 bg-grid-light bg-grid opacity-[0.35] dark:bg-grid-dark dark:opacity-[0.22]"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute -left-24 top-0 h-72 w-72 rounded-full bg-emerald-400/20 blur-[88px] dark:bg-emerald-500/12"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute -right-16 top-40 h-64 w-64 rounded-full bg-sky-400/15 blur-[80px] dark:bg-sky-500/10"
        aria-hidden
      />

      <header className="relative z-20 border-b border-zinc-200/90 bg-white/75 backdrop-blur-xl dark:border-zinc-800/90 dark:bg-zinc-950/75">
        <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-emerald-500/25 to-transparent dark:via-emerald-400/20" aria-hidden />
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4 py-3.5 sm:px-6">
          <AppLogo />
          <div className="flex flex-wrap items-center gap-2 sm:gap-3">
            <nav className="flex flex-wrap items-center gap-0.5 sm:gap-1" aria-label="Điều hướng chính">
              {mainNav.map((item) => {
                const active = isNavActive(item.href, pathname);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`${navLinkBase} ${
                      active
                        ? "bg-emerald-100/90 text-emerald-900 shadow-sm dark:bg-emerald-950/55 dark:text-emerald-100"
                        : "text-zinc-600 hover:bg-zinc-100/90 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800/80 dark:hover:text-zinc-100"
                    }`}
                    aria-current={active ? "page" : undefined}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
            {!loading && !user && (
              <div className="ml-1 flex items-center gap-2 border-l border-zinc-200 pl-3 dark:border-zinc-700">
                <Link
                  href={ROUTES.login}
                  className={`${navLinkBase} text-zinc-600 hover:bg-zinc-100/90 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800/80 dark:hover:text-zinc-100`}
                >
                  Đăng nhập
                </Link>
                <Link
                  href={ROUTES.register}
                  className="rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 px-4 py-2 text-sm font-semibold text-white shadow-md shadow-emerald-600/20 transition hover:from-emerald-500 hover:to-teal-500 hover:shadow-emerald-600/30 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-50 dark:focus-visible:ring-offset-zinc-950"
                >
                  Đăng ký
                </Link>
              </div>
            )}
            {!loading && user && (
              <UserAvatarMenu user={user} onLogout={logout} variant="compact" />
            )}
          </div>
        </div>
      </header>

      <main className="relative z-10 mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-12">
        <header className="mb-10">
          <h1 className="text-3xl font-semibold tracking-tight text-zinc-900 dark:text-white sm:text-[1.75rem]">
            {title}
          </h1>
          {description ? (
            <p className="mt-2 max-w-2xl text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
              {description}
            </p>
          ) : null}
          <div
            className="mt-5 h-1 w-14 rounded-full bg-gradient-to-r from-emerald-500 via-teal-500 to-sky-500 opacity-90"
            aria-hidden
          />
        </header>
        {children}
      </main>
    </div>
  );
}
