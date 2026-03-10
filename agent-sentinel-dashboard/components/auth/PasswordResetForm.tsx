"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import { AuthLayout } from "./AuthLayout"

export function PasswordResetForm() {
  return (
    <AuthLayout
      title="Password Reset"
      subtitle="Contact your administrator to reset your password"
    >
      <div className="text-center space-y-4">
        <p className="text-gray-300">
          Password reset is managed by your organization administrator.
          Please contact them if you need to reset your credentials.
        </p>

        <Link href="/auth/login">
          <Button variant="ghost" className="text-red-400 hover:text-red-300">
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back to Sign In
          </Button>
        </Link>
      </div>
    </AuthLayout>
  )
}
