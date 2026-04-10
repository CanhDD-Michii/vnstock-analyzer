import { fetchJson } from "@/services/api-client";
import type { AuthUser, TokenPayload } from "@/types/auth";

export async function registerUser(input: {
  fullName: string;
  email: string;
  password: string;
}): Promise<TokenPayload> {
  const res = await fetchJson<TokenPayload>(
    "/api/v1/auth/register",
    {
      method: "POST",
      body: JSON.stringify({
        fullName: input.fullName,
        email: input.email,
        password: input.password,
      }),
    },
    { auth: false },
  );
  return res.data;
}

export async function loginUser(
  email: string,
  password: string,
): Promise<TokenPayload> {
  const res = await fetchJson<TokenPayload>(
    "/api/v1/auth/login",
    {
      method: "POST",
      body: JSON.stringify({ email, password }),
    },
    { auth: false },
  );
  return res.data;
}

export async function fetchMe(): Promise<AuthUser> {
  const res = await fetchJson<AuthUser>("/api/v1/auth/me");
  return res.data;
}
