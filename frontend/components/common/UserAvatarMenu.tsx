"use client";

import { useEffect, useRef, useState } from "react";
import type { AuthUser } from "@/types/auth";

function initialsFromUser(user: AuthUser): string {
  const name = user.fullName?.trim();
  if (name) {
    const parts = name.split(/\s+/).filter(Boolean);
    if (parts.length >= 2) {
      return (
        parts[0]!.charAt(0) + parts[parts.length - 1]!.charAt(0)
      ).toUpperCase();
    }
    if (parts[0]!.length >= 2) {
      return parts[0]!.slice(0, 2).toUpperCase();
    }
    return (parts[0]!.charAt(0) + (parts[0]!.charAt(1) || "")).toUpperCase();
  }
  const e = user.email || "?";
  const local = e.split("@")[0] || e;
  return local.slice(0, 2).toUpperCase();
}

type UserAvatarMenuProps = {
  user: AuthUser;
  onLogout: () => void;
  /** Avatar nhỏ hơn cho header PageShell */
  variant?: "default" | "compact";
};

export function UserAvatarMenu({
  user,
  onLogout,
  variant = "default",
}: UserAvatarMenuProps) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function onDocMouseDown(e: MouseEvent) {
      if (!rootRef.current?.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", onDocMouseDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onDocMouseDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, []);

  const initials = initialsFromUser(user);
  const avatarSize =
    variant === "compact"
      ? "h-9 w-9 min-h-9 min-w-9 text-xs"
      : "h-10 w-10 min-h-10 min-w-10 text-sm";

  return (
    <div className="relative" ref={rootRef}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className={`flex ${avatarSize} items-center justify-center rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 font-semibold text-white shadow-md ring-2 ring-white/30 transition hover:from-emerald-400 hover:to-teal-500 hover:ring-white/50 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-2 dark:ring-zinc-900/50 dark:focus-visible:ring-offset-zinc-950`}
        aria-expanded={open}
        aria-haspopup="menu"
        aria-label="Menu tài khoản"
      >
        {initials}
      </button>

      {open ? (
        <div
          role="menu"
          aria-orientation="vertical"
          className="absolute right-0 top-full z-[100] mt-2 min-w-[240px] overflow-hidden rounded-xl border border-zinc-200 bg-white py-1 shadow-xl dark:border-zinc-700 dark:bg-zinc-900"
        >
          <div className="border-b border-zinc-100 px-4 py-3 dark:border-zinc-800">
            <p className="truncate text-sm font-medium text-zinc-900 dark:text-zinc-100">
              {user.fullName || "Người dùng"}
            </p>
            <p className="truncate text-xs text-zinc-500 dark:text-zinc-400">
              {user.email}
            </p>
            {user.role ? (
              <p className="mt-1 text-[11px] uppercase tracking-wide text-zinc-400 dark:text-zinc-500">
                {user.role}
              </p>
            ) : null}
          </div>
          <button
            type="button"
            role="menuitem"
            onClick={() => {
              setOpen(false);
              onLogout();
            }}
            className="flex w-full items-center gap-2 px-4 py-2.5 text-left text-sm text-red-600 transition hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/40"
          >
            <svg
              className="h-4 w-4 shrink-0 opacity-80"
              viewBox="0 0 24 24"
              fill="none"
              aria-hidden
            >
              <path
                d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4M10 17l5-5-5-5M15 12H3"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            Đăng xuất
          </button>
        </div>
      ) : null}
    </div>
  );
}
