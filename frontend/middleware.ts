import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

/** Khung middleware — bảo vệ route admin/auth khi triển khai. */
export function middleware(_request: NextRequest) {
  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/admin/:path*",
    "/stocks/:path*",
    "/history/:path*",
    "/stock-symbol-management/:path*",
  ],
};
