import { getAccessToken } from "@/lib/auth-storage";
import { getApiBaseUrl } from "@/lib/env";
import type { ApiErrorBody, ApiSuccessResponse } from "@/types/common";

export class ApiClientError extends Error {
  readonly status: number;
  readonly body: ApiErrorBody | null;

  constructor(message: string, status: number, body: ApiErrorBody | null) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.body = body;
  }
}

function messageFromErrorJson(json: unknown, status: number): {
  message: string;
  body: ApiErrorBody | null;
} {
  if (json && typeof json === "object" && "errorCode" in json && "message" in json) {
    return { message: String((json as ApiErrorBody).message), body: json as ApiErrorBody };
  }
  const detail = json && typeof json === "object" ? (json as { detail?: unknown }).detail : undefined;
  if (Array.isArray(detail)) {
    const parts: string[] = [];
    for (const item of detail) {
      if (typeof item === "string") {
        parts.push(item);
      } else if (item && typeof item === "object" && "msg" in item) {
        parts.push(String((item as { msg: string }).msg));
      }
    }
    if (parts.length) {
      return { message: parts.join(" · "), body: null };
    }
  }
  if (typeof detail === "string") {
    return { message: detail, body: null };
  }
  return { message: `Request failed with status ${status}`, body: null };
}

export async function fetchJson<T>(
  path: string,
  init?: RequestInit,
  options?: { auth?: boolean },
): Promise<ApiSuccessResponse<T>> {
  const url = `${getApiBaseUrl()}${path.startsWith("/") ? path : `/${path}`}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init?.headers as Record<string, string> | undefined),
  };
  if (options?.auth !== false) {
    const t = getAccessToken();
    if (t) headers.Authorization = `Bearer ${t}`;
  }
  const response = await fetch(url, {
    ...init,
    headers,
  });

  const json: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    const { message, body } = messageFromErrorJson(json, response.status);
    throw new ApiClientError(message, response.status, body);
  }

  return json as ApiSuccessResponse<T>;
}
