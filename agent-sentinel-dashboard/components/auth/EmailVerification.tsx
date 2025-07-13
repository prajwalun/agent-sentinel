"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/contexts/AuthContext"
import { AuthLayout } from "./AuthLayout"

export function EmailVerification() {
  const [resent, setResent] = useState(false)
  const { user, verifyEmail, loading } = useAuth()

  const handleResend = async () => {
    // Simulate resending email
    setResent(true)
    setTimeout(() => setResent(false), 3000)
  }

  return (
    <AuthLayout title="Verify Your Email" subtitle="We've sent a verification link to your email address">
      <div className="text-center space-y-4">
        <div className="bg-blue-900/20 border border-blue-600 text-blue-400 px-4 py-3 rounded">
          Verification email sent to: {user?.email}
        </div>

        <p className="text-gray-300">
          Please check your email and click the verification link to activate your account.
        </p>

        {resent && (
          <div className="bg-green-900/20 border border-green-600 text-green-400 px-4 py-3 rounded">
            Verification email resent successfully!
          </div>
        )}

        <div className="space-y-2">
          <Button
            onClick={handleResend}
            variant="outline"
            className="w-full bg-transparent"
            disabled={loading || resent}
          >
            {resent ? "Email Sent!" : "Resend Email"}
          </Button>

          <Link href="/auth/login">
            <Button variant="ghost" className="w-full text-red-400 hover:text-red-300">
              Change Email Address
            </Button>
          </Link>
        </div>
      </div>
    </AuthLayout>
  )
}
