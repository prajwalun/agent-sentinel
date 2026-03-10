import { type NextRequest, NextResponse } from "next/server"

/**
 * Route-level middleware.
 *
 * Auth is enforced client-side (AuthContext + DashboardLayout) because the
 * JWT lives in localStorage — it is not available as an httpOnly cookie, so
 * we cannot inspect it server-side.  This middleware only handles ancillary
 * concerns like security headers.
 */

export function middleware(_req: NextRequest) {
  const response = NextResponse.next()

  response.headers.set("X-Content-Type-Options", "nosniff")
  response.headers.set("X-Frame-Options", "DENY")
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin")

  return response
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/agents/:path*",
    "/reports/:path*",
    "/settings/:path*",
    "/auth/:path*",
  ],
}
