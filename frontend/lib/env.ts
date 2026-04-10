import { DEFAULT_LOCAL_API_BASE } from "@/constants/api";

function trimTrailingSlash(s: string): string {
  return s.replace(/\/$/, "");
}

/**
 * Base URL FastAPI.
 * - Trình duyệt: NEXT_PUBLIC_API_URL (host + port đã publish, ví dụ http://localhost:8000).
 * - Server Components / SSR trong Docker: API_URL hoặc INTERNAL_API_URL trỏ hostname nội bộ
 *   (ví dụ http://backend:8000). Nếu không set, SSR dùng NEXT_PUBLIC — trong container
 *   localhost thường sai, nên compose nên khai báo API_URL.
 */
export function getApiBaseUrl(): string {
  if (typeof window === "undefined") {
    const internal =
      process.env.API_URL?.trim() ||
      process.env.INTERNAL_API_URL?.trim() ||
      process.env.NEXT_PUBLIC_API_URL?.trim();
    return internal ? trimTrailingSlash(internal) : DEFAULT_LOCAL_API_BASE;
  }
  const pub = process.env.NEXT_PUBLIC_API_URL?.trim();
  return pub ? trimTrailingSlash(pub) : DEFAULT_LOCAL_API_BASE;
}

/** @deprecated Dùng getApiBaseUrl — giữ tên cũ cho code đã import. */
export function getPublicApiBaseUrl(): string {
  return getApiBaseUrl();
}
