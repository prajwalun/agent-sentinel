"use client"

import type React from "react"
import { useRouter } from "next/navigation"
import { useEffect } from "react"
import { Shield, Home, Users, FileText, Settings, LogOut } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/contexts/AuthContext"

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const { user, logout, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    // Only redirect after the auth context has finished reading from localStorage.
    // Without this check, the layout redirects on every page reload before the
    // stored token has been restored, logging the user out unexpectedly.
    if (!loading && !user) {
      router.push("/auth/login")
    }
  }, [user, loading, router])

  if (loading || !user) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="flex items-center gap-3 text-gray-400">
          <div className="w-5 h-5 border-2 border-red-600 border-t-transparent rounded-full animate-spin" />
          Loading...
        </div>
      </div>
    )
  }

  const handleLogout = () => {
    logout()
    router.push("/auth/login")
  }

  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <header className="bg-black border-b border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Shield className="h-8 w-8 text-red-600" />
            <h1 className="text-xl font-bold text-white">Agent Sentinel</h1>
          </div>

          <nav className="hidden md:flex items-center space-x-6">
            <Link href="/dashboard" className="text-gray-300 hover:text-white flex items-center space-x-2">
              <Home className="h-4 w-4" />
              <span>Dashboard</span>
            </Link>
            <Link href="/agents" className="text-gray-300 hover:text-white flex items-center space-x-2">
              <Users className="h-4 w-4" />
              <span>Agents</span>
            </Link>
            <Link href="/reports" className="text-gray-300 hover:text-white flex items-center space-x-2">
              <FileText className="h-4 w-4" />
              <span>Reports</span>
            </Link>
            <Link href="/settings" className="text-gray-300 hover:text-white flex items-center space-x-2">
              <Settings className="h-4 w-4" />
              <span>Settings</span>
            </Link>
          </nav>

          <div className="flex items-center space-x-4">
            <span className="text-gray-300">Welcome, {user.name}</span>
            <Button onClick={handleLogout} variant="ghost" size="sm" className="text-red-400 hover:text-red-300">
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-6">{children}</main>
    </div>
  )
}
