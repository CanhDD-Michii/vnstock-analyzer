"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { PageShell } from "@/components/common/PageShell";
import { useAuth } from "@/hooks/useAuth";
import { ROUTES } from "@/constants/routes";

const inputClass =
  "mt-1.5 w-full rounded-xl border border-zinc-200 bg-white px-4 py-2.5 text-sm text-zinc-900 shadow-inner shadow-zinc-900/[0.02] transition placeholder:text-zinc-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 dark:placeholder:text-zinc-500 dark:focus:border-emerald-500";

export default function LoginPage() {
  const { login, user, loading } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    if (!loading && user) {
      router.replace(ROUTES.stocks);
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <PageShell title="Đăng nhập" description="Xác thực tài khoản để lưu phân tích và xem lịch sử.">
        <p className="text-sm text-zinc-500">Đang tải…</p>
      </PageShell>
    );
  }

  if (user) {
    return (
      <PageShell title="Đăng nhập">
        <p className="text-sm text-zinc-500">Đang chuyển đến danh sách cổ phiếu…</p>
      </PageShell>
    );
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setPending(true);
    try {
      await login(email, password);
      router.push(ROUTES.stocks);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Đăng nhập thất bại");
    } finally {
      setPending(false);
    }
  }

  return (
    <PageShell title="Đăng nhập" description="Đăng nhập bằng email và mật khẩu đã đăng ký.">
      <div className="mx-auto max-w-md rounded-2xl border border-zinc-200/90 bg-white/90 p-6 shadow-lg shadow-zinc-900/[0.04] backdrop-blur-sm dark:border-zinc-800 dark:bg-zinc-950/80 dark:shadow-black/30 sm:p-8">
        <form onSubmit={onSubmit} className="space-y-5">
          {error && (
            <p
              role="alert"
              className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800 dark:border-red-900/50 dark:bg-red-950/50 dark:text-red-200"
            >
              {error}
            </p>
          )}
          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300" htmlFor="login-email">
              Email
            </label>
            <input
              id="login-email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={inputClass}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300" htmlFor="login-password">
              Mật khẩu
            </label>
            <input
              id="login-password"
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={inputClass}
            />
          </div>
          <button
            type="submit"
            disabled={pending}
            className="w-full rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 px-4 py-3 text-sm font-semibold text-white shadow-md shadow-emerald-600/25 transition hover:from-emerald-500 hover:to-teal-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {pending ? "Đang đăng nhập…" : "Đăng nhập"}
          </button>
          <p className="text-center text-sm text-zinc-600 dark:text-zinc-400">
            Chưa có tài khoản?{" "}
            <Link
              href={ROUTES.register}
              className="font-semibold text-emerald-700 underline decoration-emerald-500/40 underline-offset-2 hover:text-emerald-800 dark:text-emerald-400"
            >
              Đăng ký
            </Link>
          </p>
        </form>
      </div>
    </PageShell>
  );
}
