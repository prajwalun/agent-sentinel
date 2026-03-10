import { Suspense } from "react"
import { AuthError } from "@/components/auth/AuthError"

export default function AuthErrorPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-black" />}>
      <AuthError />
    </Suspense>
  )
}
