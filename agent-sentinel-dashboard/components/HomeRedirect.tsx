"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/contexts/AuthContext"

export function HomeRedirect() {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (loading) return
    if (user) {
      router.replace("/dashboard")
    } else {
      router.replace("/auth/login")
    }
  }, [loading, user, router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950">
      <div className="text-gray-400">Loading...</div>
    </div>
  )
}
