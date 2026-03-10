"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { AuthLayout } from "./AuthLayout"

export function EmailVerification() {
  return (
    <AuthLayout
      title="Account Created"
      subtitle="Your account is ready to use"
    >
      <div className="text-center space-y-4">
        <div className="bg-green-900/20 border border-green-600 text-green-400 px-4 py-3 rounded">
          Your account has been created successfully.
        </div>

        <p className="text-gray-300">
          You can now sign in and start monitoring your AI agents.
        </p>

        <Link href="/auth/login">
          <Button className="w-full btn-primary">Go to Sign In</Button>
        </Link>
      </div>
    </AuthLayout>
  )
}
