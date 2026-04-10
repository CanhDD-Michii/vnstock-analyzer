"use client";

import { useRouter } from "next/navigation";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { ROUTES } from "@/constants/routes";
import { setAccessToken, getAccessToken } from "@/lib/auth-storage";
import * as authApi from "@/services/auth.service";
import type { AuthUser } from "@/types/auth";

type AuthContextValue = {
  user: AuthUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (input: {
    fullName: string;
    email: string;
    password: string;
  }) => Promise<void>;
  logout: () => void;
  refreshMe: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshMe = useCallback(async () => {
    const t = getAccessToken();
    if (!t) {
      setUser(null);
      return;
    }
    try {
      const me = await authApi.fetchMe();
      setUser(me);
    } catch {
      setAccessToken(null);
      setUser(null);
    }
  }, []);

  useEffect(() => {
    void (async () => {
      setLoading(true);
      await refreshMe();
      setLoading(false);
    })();
  }, [refreshMe]);

  const login = useCallback(async (email: string, password: string) => {
    const tok = await authApi.loginUser(email, password);
    setAccessToken(tok.accessToken);
    await refreshMe();
  }, [refreshMe]);

  const register = useCallback(
    async (input: { fullName: string; email: string; password: string }) => {
      const tok = await authApi.registerUser(input);
      setAccessToken(tok.accessToken);
      await refreshMe();
    },
    [refreshMe],
  );

  const logout = useCallback(() => {
    setAccessToken(null);
    setUser(null);
    router.replace(ROUTES.home);
  }, [router]);

  const value = useMemo(
    () => ({
      user,
      loading,
      login,
      register,
      logout,
      refreshMe,
    }),
    [user, loading, login, register, logout, refreshMe],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
