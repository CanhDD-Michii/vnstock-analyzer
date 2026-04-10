export const ROUTES = {
  home: "/",
  login: "/login",
  register: "/register",
  stocks: "/stocks",
  stockDetail: (ticker: string) => `/stocks/${encodeURIComponent(ticker)}`,
  history: "/history",
  historyDetail: (id: number) => `/history/${id}`,
  stockSymbolManagement: "/stock-symbol-management",
  adminUsers: "/admin/users",
} as const;
