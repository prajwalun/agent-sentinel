"use client"

import type React from "react"
import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { AuthLayout } from "./AuthLayout"

export function SignUpForm() {
  const [formData, setFormData] = useState({
    fullName: "",
    company: "",
    email: "",
    password: "",
    confirmPassword: "",
    termsAccepted: false,
    marketingAccepted: false,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match")
      setLoading(false)
      return
    }

    // Simulate signup process
    setTimeout(() => {
      setLoading(false)
      router.push("/auth/verify-email")
    }, 1000)
  }

  const handleChange = (field: string, value: string | boolean) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  return (
    <AuthLayout title="Create Your Account" subtitle="Join Agent Sentinel to monitor your AI agents securely">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <div className="bg-red-900/20 border border-red-600 text-red-400 px-4 py-3 rounded">{error}</div>}

        <div className="space-y-2">
          <Label htmlFor="fullName" className="text-white">
            Full Name
          </Label>
          <Input
            id="fullName"
            type="text"
            value={formData.fullName}
            onChange={(e) => handleChange("fullName", e.target.value)}
            className="input-dark"
            placeholder="Enter your full name"
            required
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="company" className="text-white">
            Company/Organization
          </Label>
          <Input
            id="company"
            type="text"
            value={formData.company}
            onChange={(e) => handleChange("company", e.target.value)}
            className="input-dark"
            placeholder="Enter your company name"
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
            placeholder="Create a strong password"
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
        </div>

        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="terms"
              checked={formData.termsAccepted}
              onCheckedChange={(checked) => handleChange("termsAccepted", checked as boolean)}
              required
            />
            <Label htmlFor="terms" className="text-gray-300 text-sm">
              I agree to the{" "}
              <Link href="/terms" className="text-red-400 hover:text-red-300 underline">
                Terms of Service
              </Link>
            </Label>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="marketing"
              checked={formData.marketingAccepted}
              onCheckedChange={(checked) => handleChange("marketingAccepted", checked as boolean)}
            />
            <Label htmlFor="marketing" className="text-gray-300 text-sm">
              I want to receive security updates and newsletters
            </Label>
          </div>
        </div>

        <Button type="submit" className="w-full btn-primary" disabled={loading || !formData.termsAccepted}>
          {loading ? "Creating Account..." : "Create Account"}
        </Button>

        <div className="text-center text-sm text-gray-400">
          Already have an account?{" "}
          <Link href="/auth/login" className="text-red-400 hover:text-red-300 underline">
            Sign In
          </Link>
        </div>
      </form>
    </AuthLayout>
  )
}
