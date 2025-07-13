"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect } from "react"

interface User {
  id: string
  email: string
  fullName: string
  company: string
  isVerified: boolean
}

interface AuthContextType {
  user: User | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  loading: boolean
  error: string | null
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [mounted, setMounted] = useState(false)

  // Check for stored user on mount
  useEffect(() => {
    setMounted(true)
    const storedUser = localStorage.getItem("auth_user")
    if (storedUser) {
      setUser(JSON.parse(storedUser))
    }
  }, [])

  const login = async (email: string, password: string) => {
    setLoading(true)
    setError(null)

    try {
      // Simple validation - just check email format
      if (!email.includes("@")) {
        throw new Error("Please enter a valid email address")
      }

      if (!password) {
        throw new Error("Please enter a password")
      }

      // Create user from email - use email as ID to avoid hydration issues
      const userId = btoa(email).replace(/[^a-zA-Z0-9]/g, '').substring(0, 12)
      const newUser: User = {
        id: userId,
        email: email,
        fullName: email.split("@")[0],
        company: "Demo Company",
        isVerified: true,
      }

      setUser(newUser)
      if (mounted) {
        localStorage.setItem("auth_user", JSON.stringify(newUser))
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed")
      throw err
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    setUser(null)
    if (mounted) {
      localStorage.removeItem("auth_user")
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        loading,
        error,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
