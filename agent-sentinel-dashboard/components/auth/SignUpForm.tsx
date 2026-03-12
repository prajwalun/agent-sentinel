"use client"

import type React from "react"
import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useAuth } from "@/contexts/AuthContext"
import { AuthLayout } from "./AuthLayout"

export function SignUpForm() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  })
  const [apiKey, setApiKey] = useState<string | null>(null)
  const { signup, clearError, loading, error } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (formData.password !== formData.confirmPassword) {
      return
    }

    try {
      const result = await signup(formData.email, formData.password, formData.name)
      setApiKey(result.apiKey)
    } catch {
      // Error is surfaced via context
    }
  }

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (error) clearError()
  }

  const passwordMismatch =
    formData.confirmPassword.length > 0 &&
    formData.password !== formData.confirmPassword

  if (apiKey) {
    return (
      <AuthLayout
        title="Account Created"
        subtitle="Save your API key — you will need it to connect the SDK"
      >
        <div className="space-y-4">
          <div className="bg-green-900/20 border border-green-600 text-green-400 px-4 py-3 rounded">
            Your account has been created successfully.
          </div>

          <div className="space-y-2">
            <Label className="text-white">Your API Key</Label>
            <div className="bg-gray-900 border border-gray-700 rounded p-3 font-mono text-sm text-green-400 break-all select-all">
              {apiKey}
            </div>
            <p className="text-xs text-gray-500">
              Copy this key now. It will not be shown again. Use it to configure the Agent
              Sentinel SDK.
            </p>
          </div>

          <div className="space-y-2">
            <Label className="text-white">Quick Start</Label>
            <p className="text-xs text-gray-500">In a new terminal, run:</p>
            <pre className="bg-gray-900 border border-gray-700 rounded p-3 text-xs text-gray-300 overflow-x-auto">
{`pip install agent-sentinel
export SENTINEL_API_URL="http://localhost:8001"
export SENTINEL_API_KEY="${apiKey}"`}
            </pre>
          </div>

          <Button
            onClick={() => router.push("/dashboard")}
            className="w-full btn-primary"
          >
            Go to Dashboard
          </Button>
        </div>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout
      title="Create Your Account"
      subtitle="Join Agent Sentinel to monitor your AI agents securely"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-red-900/20 border border-red-600 text-red-400 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="space-y-2">
          <Label htmlFor="name" className="text-white">
            Full Name
          </Label>
          <Input
            id="name"
            type="text"
            value={formData.name}
            onChange={(e) => handleChange("name", e.target.value)}
            className="input-dark"
            placeholder="Enter your full name"
            required
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="email" className="text-white">
            Email Address
          </Label>
          <Input
            id="email"
            type="email"
            value={formData.email}
            onChange={(e) => handleChange("email", e.target.value)}
            className="input-dark"
            placeholder="Enter your email"
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
            value={formData.password}
            onChange={(e) => handleChange("password", e.target.value)}
            className="input-dark"
            placeholder="Create a strong password (min 8 chars)"
            minLength={8}
            required
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="confirmPassword" className="text-white">
            Confirm Password
          </Label>
          <Input
            id="confirmPassword"
            type="password"
            value={formData.confirmPassword}
            onChange={(e) => handleChange("confirmPassword", e.target.value)}
            className="input-dark"
            placeholder="Confirm your password"
            required
          />
          {passwordMismatch && (
            <p className="text-red-400 text-xs">Passwords do not match</p>
          )}
        </div>

        <Button
          type="submit"
          className="w-full btn-primary"
          disabled={loading || passwordMismatch}
        >
          {loading ? "Creating Account..." : "Create Account"}
        </Button>

        <div className="text-center text-sm text-gray-400">
          Already have an account?{" "}
          <Link
            href="/auth/login"
            className="text-red-400 hover:text-red-300 underline"
          >
            Sign In
          </Link>
        </div>
      </form>
    </AuthLayout>
  )
}
