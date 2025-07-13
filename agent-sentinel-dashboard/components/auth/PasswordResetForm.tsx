"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ArrowLeft } from "lucide-react"
import { useAuth } from "@/contexts/AuthContext"
import { AuthLayout } from "./AuthLayout"

export function PasswordResetForm() {
  const [email, setEmail] = useState("")
  const [success, setSuccess] = useState(false)
  const { forgotPassword, loading, error } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await forgotPassword(email)
      setSuccess(true)
    } catch (err) {
      // Error handled by context
    }
  }

  if (success) {
    return (
      <AuthLayout title="Check Your Email" subtitle="We've sent a password reset link to your email address">
        <div className="text-center space-y-4">
          <div className="bg-green-900/20 border border-green-600 text-green-400 px-4 py-3 rounded">
            Password reset link sent to {email}
          </div>
          <p className="text-gray-300">Please check your email and click the link to reset your password.</p>
          <Link href="/auth/login" className="inline-flex items-center text-red-400 hover:text-red-300 underline">
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back to Sign In
          </Link>
        </div>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout
      title="Reset Your Password"
      subtitle="Enter your email address and we'll send you a link to reset your password"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <div className="bg-red-900/20 border border-red-600 text-red-400 px-4 py-3 rounded">{error}</div>}

        <div className="space-y-2">
          <Label htmlFor="email" className="text-white">
            Email Address
          </Label>
          <Input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input-dark"
            placeholder="Enter your email"
            required
          />
        </div>

        <Button type="submit" className="w-full btn-primary" disabled={loading}>
          {loading ? "Sending..." : "Send Reset Link"}
        </Button>

        <div className="text-center">
          <Link
            href="/auth/login"
            className="inline-flex items-center text-red-400 hover:text-red-300 underline text-sm"
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back to Sign In
          </Link>
        </div>
      </form>
    </AuthLayout>
  )
}
