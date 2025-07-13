import { type NextRequest, NextResponse } from "next/server"

// Define which paths require authentication.
const protectedPaths = ["/dashboard", "/agents", "/reports", "/settings"]

export async function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl
  const isAuthPage = pathname.startsWith("/auth")

  // If it's a protected path, let the client-side auth handle it
  // This middleware is now just for basic routing
  if (isAuthPage) {
    return NextResponse.next()
  }

  return NextResponse.next()
}

export const config = {
  matcher: ["/dashboard/:path*", "/agents/:path*", "/reports/:path*", "/settings/:path*", "/auth/:path*"],
}
