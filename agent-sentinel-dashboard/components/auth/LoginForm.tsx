"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useAuth } from "@/contexts/AuthContext"
import { AuthLayout } from "./AuthLayout"

export function LoginForm() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const { user, login, clearError, loading, error } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && user) {
      router.replace("/dashboard")
    }
  }, [loading, user, router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await login(email, password)
      router.replace("/dashboard")
    } catch {
      // Error is surfaced via context
    }
  }

  return (
    <AuthLayout
      title="Sign In to Your Dashboard"
      subtitle="Enter your credentials to access your security monitoring dashboard"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-red-900/20 border border-red-600 text-red-400 px-4 py-3 rounded">
            {error}
          </div>
        )}

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
            placeholder="Enter your email address"
            required
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="password" className="text-white">
            Password
          </Label>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value)
              if (error) clearError()
            }}
            className="input-dark"
            placeholder="Enter your password"
            required
          />
        </div>

        <Button type="submit" className="w-full btn-primary" disabled={loading}>
          {loading ? "Signing In..." : "Sign In"}
        </Button>

        <div className="text-center text-sm text-gray-400">
          Don&apos;t have an account?{" "}
          <Link
            href="/auth/signup"
            className="text-red-400 hover:text-red-300 underline"
          >
            Sign Up
          </Link>
        </div>
      </form>
    </AuthLayout>
  )
}
