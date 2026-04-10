"use client";

import { ChevronRight } from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";
import { AppLogo } from "@/components/common/AppLogo";
import { UserAvatarMenu } from "@/components/common/UserAvatarMenu";
import { ROUTES } from "@/constants/routes";
import { useAuth } from "@/hooks/useAuth";

function IconChart({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M4 19V5M8 19V11M12 19V8M16 19V14M20 19V9"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}

function IconSpark({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M12 2v4M12 18v4M4 12h4M16 12h4M6.34 6.34l2.83 2.83M14.83 14.83l2.83 2.83M6.34 17.66l2.83-2.83M14.83 9.17l2.83-2.83"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <circle cx="12" cy="12" r="3" fill="currentColor" />
    </svg>
  );
}

function IconLayers({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M12 4L4 8l8 4 8-4-8-4zM4 12l8 4 8-4M4 16l8 4 8-4"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function IconShield({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M12 3l8 4v6c0 5-3.5 9-8 10-4.5-1-8-5-8-10V7l8-4z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
      />
    </svg>
  );
}

const features = [
  {
    icon: IconChart,
    title: "Engine chỉ báo kỹ thuật",
    description:
      "Điểm xu hướng, động lượng, thanh khoản và trạng thái thị trường được tính từ chuỗi giá — minh bạch cho từng mã.",
  },
  {
    icon: IconSpark,
    title: "Phân tích & lịch sử",
    description:
      "Chạy phân tích, lưu kết quả và xem lại tóm tắt AI (khi bật OpenAI) cùng snapshot chỉ số tại thời điểm chạy.",
  },
  {
    icon: IconLayers,
    title: "Dữ liệu & crawl linh hoạt",
    description:
      "Ingest JSON hoặc cấu hình crawl theo metadata từng mã — dễ đổi nguồn dữ liệu sau này.",
  },
  {
    icon: IconShield,
    title: "Tài khoản & phân quyền",
    description:
      "Đăng ký, đăng nhập JWT; quản lý mã chứng khoán dành cho tài khoản có quyền phù hợp.",
  },
];

export function HomeLanding() {
  const { user, loading, logout } = useAuth();

  return (
    <div className="relative min-h-screen overflow-x-hidden bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
      <div
        className="pointer-events-none absolute inset-0 bg-grid-light bg-grid dark:bg-grid-dark"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute -left-32 top-0 h-[420px] w-[420px] rounded-full bg-emerald-400/25 blur-[100px] dark:bg-emerald-500/15"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute -right-24 top-32 h-[360px] w-[360px] rounded-full bg-sky-400/20 blur-[90px] dark:bg-sky-500/12"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute bottom-0 left-1/2 h-[280px] w-[600px] -translate-x-1/2 rounded-full bg-teal-400/15 blur-[100px] dark:bg-teal-500/10"
        aria-hidden
      />

      <header className="relative z-20 border-b border-zinc-200/80 bg-white/70 backdrop-blur-md dark:border-zinc-800/80 dark:bg-zinc-950/70">
        <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-emerald-500/20 to-transparent dark:via-emerald-400/15" aria-hidden />
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4 py-4 sm:px-6">
          <AppLogo />
          <nav className="flex flex-wrap items-center gap-1 text-sm sm:gap-2">
            <Link
              href={ROUTES.stocks}
              className="rounded-lg px-3 py-2 text-zinc-600 transition hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-zinc-100"
            >
              Cổ phiếu
            </Link>
            {!loading && user && (
              <>
                <Link
                  href={ROUTES.home}
                  className="rounded-lg px-3 py-2 text-zinc-600 transition hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-zinc-100"
                >
                  Trang chủ
                </Link>
                <Link
                  href={ROUTES.history}
                  className="rounded-lg px-3 py-2 text-zinc-600 transition hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-zinc-100"
                >
                  Lịch sử
                </Link>
                {user.role === "admin" && (
                  <>
                    <Link
                      href={ROUTES.adminUsers}
                      className="rounded-lg px-3 py-2 text-zinc-600 transition hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-zinc-100"
                    >
                      Người dùng
                    </Link>
                    <Link
                      href={ROUTES.stockSymbolManagement}
                      className="rounded-lg px-3 py-2 text-zinc-600 transition hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-zinc-100"
                    >
                      Quản lý mã
                    </Link>
                  </>
                )}
              </>
            )}
            {!loading && !user && (
              <>
                <Link
                  href={ROUTES.login}
                  className="rounded-lg px-3 py-2 text-zinc-600 transition hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-zinc-100"
                >
                  Đăng nhập
                </Link>
                <Link
                  href={ROUTES.register}
                  className="rounded-lg bg-zinc-900 px-4 py-2 font-medium text-white shadow-sm transition hover:bg-zinc-800 dark:bg-white dark:text-zinc-900 dark:hover:bg-zinc-100"
                >
                  Đăng ký
                </Link>
              </>
            )}
            {!loading && user && (
              <UserAvatarMenu user={user} onLogout={logout} variant="default" />
            )}
          </nav>
        </div>
      </header>

      <main className="relative z-10">
        <section className="mx-auto max-w-6xl px-4 pb-20 pt-16 sm:px-6 sm:pt-20 lg:pt-28">
          <div className="mx-auto max-w-3xl text-center">
            <p className="inline-flex items-center gap-2 rounded-full border border-emerald-200/80 bg-emerald-50/90 px-3 py-1 text-xs font-medium text-emerald-800 shadow-sm dark:border-emerald-500/30 dark:bg-emerald-950/50 dark:text-emerald-200">
              <span className="relative flex h-1.5 w-1.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-emerald-500" />
              </span>
              Phân tích chứng khoán Việt Nam
            </p>
            <h1 className="mt-6 text-4xl font-semibold tracking-tight text-zinc-900 sm:text-5xl sm:leading-[1.1] lg:text-6xl dark:text-white">
              Nền tảng{" "}
              <span className="bg-gradient-to-r from-emerald-600 via-teal-600 to-sky-600 bg-clip-text text-transparent dark:from-emerald-400 dark:via-teal-400 dark:to-sky-400">
                VN Stock Analyzer
              </span>
            </h1>
            <p className="mx-auto mt-6 max-w-xl text-base leading-relaxed text-zinc-600 dark:text-zinc-400">
              Theo dõi mã, biểu đồ giá đa khung thời gian, chỉ báo kỹ thuật và phân tích có lưu lịch sử — giao diện hiện đại,
              API rõ ràng (Next.js + FastAPI + MySQL).
            </p>
            <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row sm:gap-4">
              <Link
                href={ROUTES.stocks}
                className="inline-flex w-full min-w-[200px] items-center justify-center rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 px-8 py-3.5 text-sm font-semibold text-white shadow-lg shadow-emerald-600/25 transition hover:from-emerald-500 hover:to-teal-500 hover:shadow-emerald-600/35 sm:w-auto dark:shadow-emerald-900/40"
              >
                Xem danh sách cổ phiếu
              </Link>
              {!loading && user ? (
                <Link
                  href={ROUTES.history}
                  className="inline-flex w-full min-w-[200px] items-center justify-center rounded-xl border border-zinc-300 bg-white/80 px-8 py-3.5 text-sm font-semibold text-zinc-800 backdrop-blur transition hover:border-zinc-400 hover:bg-white sm:w-auto dark:border-zinc-600 dark:bg-zinc-900/80 dark:text-zinc-100 dark:hover:bg-zinc-900"
                >
                  Lịch sử phân tích
                </Link>
              ) : (
                <Link
                  href={ROUTES.register}
                  className="inline-flex w-full min-w-[200px] items-center justify-center rounded-xl border border-zinc-300 bg-white/80 px-8 py-3.5 text-sm font-semibold text-zinc-800 backdrop-blur transition hover:border-zinc-400 hover:bg-white sm:w-auto dark:border-zinc-600 dark:bg-zinc-900/80 dark:text-zinc-100 dark:hover:bg-zinc-900"
                >
                  Tạo tài khoản miễn phí
                </Link>
              )}
            </div>
          </div>

          <div className="mx-auto mt-20 grid max-w-4xl grid-cols-1 gap-4 sm:grid-cols-3">
            {(
              [
                { k: "Chỉ báo", title: "Điểm & trạng thái", sub: "Engine nội bộ" },
                {
                  k: "Biểu đồ",
                  title: (
                    <span className="inline-flex items-center justify-center gap-0.5">
                      <span>1D</span>
                      <ChevronRight
                        className="h-5 w-5 shrink-0 text-zinc-400 dark:text-zinc-500"
                        strokeWidth={2}
                        aria-hidden
                      />
                      <span>ALL</span>
                    </span>
                  ),
                  sub: "EOD & khung tùy chọn",
                },
                { k: "Stack", title: "Next + FastAPI", sub: "API REST chuẩn" },
              ] as { k: string; title: ReactNode; sub: string }[]
            ).map((item) => (
              <div
                key={item.k}
                className="rounded-2xl border border-zinc-200/80 bg-white/60 p-5 text-center shadow-sm backdrop-blur-sm dark:border-zinc-800 dark:bg-zinc-900/40"
              >
                <p className="text-xs font-medium uppercase tracking-wider text-zinc-500 dark:text-zinc-500">
                  {item.k}
                </p>
                <p className="mt-2 text-lg font-semibold text-zinc-900 dark:text-white">{item.title}</p>
                <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">{item.sub}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="border-y border-zinc-200/80 bg-white/50 py-20 dark:border-zinc-800 dark:bg-zinc-900/30">
          <div className="mx-auto max-w-6xl px-4 sm:px-6">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-2xl font-semibold tracking-tight text-zinc-900 sm:text-3xl dark:text-white">
                Tính năng nổi bật
              </h2>
              <p className="mt-3 text-zinc-600 dark:text-zinc-400">
                Mọi thứ xoay quanh dữ liệu giá minh bạch và luồng phân tích có thể truy vết.
              </p>
            </div>
            <ul className="mx-auto mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {features.map(({ icon: Icon, title, description }) => (
                <li
                  key={title}
                  className="group rounded-2xl border border-zinc-200/90 bg-zinc-50/80 p-6 transition hover:border-emerald-300/60 hover:shadow-md dark:border-zinc-800 dark:bg-zinc-950/50 dark:hover:border-emerald-500/25"
                >
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700 transition group-hover:scale-105 dark:bg-emerald-950/80 dark:text-emerald-300">
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="mt-4 font-semibold text-zinc-900 dark:text-white">{title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
                    {description}
                  </p>
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
          <div className="overflow-hidden rounded-3xl border border-zinc-200/80 bg-gradient-to-br from-zinc-900 to-zinc-800 px-8 py-14 text-center shadow-xl dark:border-zinc-700 dark:from-zinc-900 dark:to-zinc-950">
            <h2 className="text-2xl font-semibold text-white sm:text-3xl">
              Sẵn sàng xem biểu đồ và chỉ báo?
            </h2>
            <p className="mx-auto mt-3 max-w-lg text-sm text-zinc-400">
              Chọn một mã trong danh sách — hệ thống sẽ tải giá và engine kỹ thuật khi đủ dữ liệu lịch sử.
            </p>
            <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Link
                href={ROUTES.stocks}
                className="inline-flex min-w-[200px] items-center justify-center rounded-xl bg-white px-8 py-3.5 text-sm font-semibold text-zinc-900 transition hover:bg-zinc-100"
              >
                Mở danh sách cổ phiếu
              </Link>
              {!loading && !user && (
                <Link
                  href={ROUTES.login}
                  className="inline-flex min-w-[200px] items-center justify-center rounded-xl border border-zinc-600 px-8 py-3.5 text-sm font-semibold text-white transition hover:border-zinc-500 hover:bg-white/5"
                >
                  Đã có tài khoản? Đăng nhập
                </Link>
              )}
            </div>
          </div>
        </section>

        <footer className="border-t border-zinc-200/80 py-10 dark:border-zinc-800">
          <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-4 text-center text-sm text-zinc-500 sm:flex-row sm:px-6 sm:text-left dark:text-zinc-500">
            <p>© {new Date().getFullYear()} VN Stock Analyzer · Dữ liệu chỉ mang tính tham khảo.</p>
            <div className="flex flex-wrap justify-center gap-4">
              <span className="rounded-md bg-zinc-200/80 px-2 py-0.5 text-xs font-medium text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">
                Next.js
              </span>
              <span className="rounded-md bg-zinc-200/80 px-2 py-0.5 text-xs font-medium text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">
                FastAPI
              </span>
              <span className="rounded-md bg-zinc-200/80 px-2 py-0.5 text-xs font-medium text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">
                MySQL
              </span>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
