"use client"

import type React from "react"
import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { useAuth } from "@/contexts/AuthContext"
import { AuthLayout } from "./AuthLayout"

export function LoginForm() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [rememberMe, setRememberMe] = useState(false)
  const { login, loading, error } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await login(email, password, rememberMe)
      router.push("/dashboard")
    } catch (err) {
      // Error handled by context
    }
  }

  return (
    <AuthLayout
      title="Sign In to Your Dashboard"
      subtitle="Enter your credentials to access your security monitoring dashboard"
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
            onChange={(e) => setPassword(e.target.value)}
            className="input-dark"
            placeholder="Enter your password"
            required
          />
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="remember"
              checked={rememberMe}
              onCheckedChange={(checked) => setRememberMe(checked as boolean)}
            />
            <Label htmlFor="remember" className="text-gray-300 text-sm">
              Remember me
            </Label>
          </div>
          <Link href="/auth/forgot-password" className="text-red-400 hover:text-red-300 text-sm underline">
            Forgot password?
          </Link>
        </div>

        <Button type="submit" className="w-full btn-primary" disabled={loading}>
          {loading ? "Signing In..." : "Sign In"}
        </Button>

        <div className="text-center text-sm text-gray-400">
          Don't have an account?{" "}
          <Link href="/auth/signup" className="text-red-400 hover:text-red-300 underline">
            Sign Up
          </Link>
        </div>
      </form>
    </AuthLayout>
  )
}
