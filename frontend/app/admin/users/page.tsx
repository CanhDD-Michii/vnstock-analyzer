"use client";

import { ChevronLeft } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { PageShell } from "@/components/common/PageShell";
import { SectionCard } from "@/components/ui/SectionCard";
import { ROUTES } from "@/constants/routes";
import { useAuth } from "@/hooks/useAuth";
import * as adminApi from "@/services/admin.service";

const PAGE_TITLE = "Quản lý người dùng";

const selectClass =
  "rounded-lg border border-zinc-200 bg-white px-2 py-1.5 text-sm dark:border-zinc-600 dark:bg-zinc-900";

const inputClass =
  "w-full min-w-[8rem] rounded-lg border border-zinc-200 bg-white px-2 py-1.5 text-sm dark:border-zinc-600 dark:bg-zinc-900";

function UserEditorRow({
  row,
  currentUserId,
  onUpdated,
}: {
  row: adminApi.UserAdminRow;
  currentUserId: number | null;
  onUpdated: (u: adminApi.UserAdminRow) => void;
}) {
  const [fullName, setFullName] = useState(row.fullName);
  const [role, setRole] = useState<"user" | "admin">(
    row.role === "admin" ? "admin" : "user",
  );
  const [status, setStatus] = useState<"active" | "inactive">(
    row.status === "inactive" ? "inactive" : "active",
  );
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const isSelf = currentUserId != null && row.id === currentUserId;
  const dirty =
    fullName !== row.fullName || role !== row.role || status !== row.status;

  useEffect(() => {
    setFullName(row.fullName);
    setRole(row.role === "admin" ? "admin" : "user");
    setStatus(row.status === "inactive" ? "inactive" : "active");
    setErr(null);
  }, [row]);

  async function save() {
    setErr(null);
    setSaving(true);
    try {
      const updated = await adminApi.adminPatchUser(row.id, {
        fullName,
        role,
        status,
      });
      onUpdated(updated);
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "Cập nhật thất bại");
    } finally {
      setSaving(false);
    }
  }

  return (
    <tr className="border-b border-zinc-100 align-top dark:border-zinc-800/90">
      <td className="px-3 py-3 tabular-nums text-zinc-500 dark:text-zinc-400">{row.id}</td>
      <td className="px-3 py-3 text-sm text-zinc-600 dark:text-zinc-400">{row.email}</td>
      <td className="px-3 py-3">
        <input
          type="text"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          className={inputClass}
          aria-label="Họ tên"
        />
      </td>
      <td className="px-3 py-3">
        <select
          value={role}
          onChange={(e) => setRole(e.target.value as "user" | "admin")}
          className={selectClass}
          aria-label="Vai trò"
        >
          <option value="user">user</option>
          <option value="admin">admin</option>
        </select>
      </td>
      <td className="px-3 py-3">
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value as "active" | "inactive")}
          disabled={isSelf}
          className={selectClass}
          title={isSelf ? "Không thể tự đổi trạng thái tài khoản của chính mình" : undefined}
          aria-label="Trạng thái"
        >
          <option value="active">active</option>
          <option value="inactive">inactive</option>
        </select>
        {isSelf ? (
          <p className="mt-1 text-[11px] text-zinc-400">Bạn — không tự khóa</p>
        ) : null}
      </td>
      <td className="px-3 py-3">
        <button
          type="button"
          disabled={!dirty || saving}
          onClick={() => void save()}
          className="rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 px-3 py-1.5 text-xs font-semibold text-white shadow-sm transition hover:from-emerald-500 hover:to-teal-500 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {saving ? "…" : "Lưu"}
        </button>
        {err ? <p className="mt-2 max-w-[200px] text-xs text-red-600 dark:text-red-400">{err}</p> : null}
      </td>
    </tr>
  );
}

export default function AdminUsersPage() {
  const { user, loading } = useAuth();
  const [items, setItems] = useState<adminApi.UserAdminRow[]>([]);
  const [loadErr, setLoadErr] = useState<string | null>(null);
  const [loadingList, setLoadingList] = useState(true);

  const refresh = useCallback(async () => {
    setLoadingList(true);
    setLoadErr(null);
    try {
      const data = await adminApi.adminListUsers();
      setItems(data);
    } catch (e: unknown) {
      setLoadErr(e instanceof Error ? e.message : "Không tải được danh sách");
    } finally {
      setLoadingList(false);
    }
  }, []);

  useEffect(() => {
    if (loading || user?.role !== "admin") return;
    void refresh();
  }, [user, loading, refresh]);

  function mergeUpdated(u: adminApi.UserAdminRow) {
    setItems((prev) => prev.map((x) => (x.id === u.id ? u : x)));
  }

  if (loading) {
    return (
      <PageShell title={PAGE_TITLE} description="Đang xác thực…">
        <p className="text-sm text-zinc-500">Đang tải…</p>
      </PageShell>
    );
  }

  if (user?.role !== "admin") {
    return (
      <PageShell title={PAGE_TITLE} description="Chỉ admin mới truy cập được.">
        <p className="rounded-xl border border-zinc-200 bg-zinc-50/90 px-4 py-3 text-sm text-zinc-700 dark:border-zinc-700 dark:bg-zinc-900/50 dark:text-zinc-300">
          Bạn không có quyền truy cập trang này.
        </p>
      </PageShell>
    );
  }

  return (
    <PageShell
      title={PAGE_TITLE}
      description="Xem và chỉnh họ tên, vai trò (user / admin), trạng thái (active / inactive). Phải luôn còn ít nhất một admin đang hoạt động."
    >
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <Link
          href={ROUTES.stockSymbolManagement}
          className="inline-flex items-center gap-1 text-sm font-medium text-emerald-700 hover:text-emerald-800 dark:text-emerald-400"
        >
          <ChevronLeft className="h-4 w-4 shrink-0" strokeWidth={2} aria-hidden />
          Quản lý mã chứng khoán
        </Link>
        <button
          type="button"
          onClick={() => void refresh()}
          disabled={loadingList}
          className="rounded-lg border border-zinc-200 px-3 py-1.5 text-xs font-medium text-zinc-700 transition hover:bg-zinc-50 dark:border-zinc-600 dark:text-zinc-200 dark:hover:bg-zinc-800"
        >
          {loadingList ? "Đang tải…" : "Làm mới danh sách"}
        </button>
      </div>

      <SectionCard title="Danh sách tài khoản">
        {loadErr ? (
          <p className="mb-4 rounded-xl border border-red-200 bg-red-50/90 px-4 py-3 text-sm text-red-800 dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-200">
            {loadErr}
          </p>
        ) : null}
        {loadingList && items.length === 0 ? (
          <p className="text-sm text-zinc-500">Đang tải danh sách…</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] border-collapse text-sm">
              <thead>
                <tr className="border-b border-zinc-200 bg-zinc-50/90 text-left text-xs font-semibold uppercase tracking-wide text-zinc-600 dark:border-zinc-800 dark:bg-zinc-900/50 dark:text-zinc-400">
                  <th scope="col" className="px-3 py-2">
                    ID
                  </th>
                  <th scope="col" className="px-3 py-2">
                    Email
                  </th>
                  <th scope="col" className="px-3 py-2">
                    Họ tên
                  </th>
                  <th scope="col" className="px-3 py-2">
                    Vai trò
                  </th>
                  <th scope="col" className="px-3 py-2">
                    Trạng thái
                  </th>
                  <th scope="col" className="px-3 py-2">
                    Thao tác
                  </th>
                </tr>
              </thead>
              <tbody>
                {items.map((row) => (
                  <UserEditorRow
                    key={row.id}
                    row={row}
                    currentUserId={user?.id ?? null}
                    onUpdated={mergeUpdated}
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}
        {!loadingList && items.length === 0 && !loadErr ? (
          <p className="text-sm text-zinc-500">Chưa có người dùng.</p>
        ) : null}
      </SectionCard>
    </PageShell>
  );
}
