"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect, useCallback } from "react"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"

interface User {
  id: string
  email: string
  name: string
  created_at: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, name: string) => Promise<{ apiKey: string }>
  logout: () => void
  loading: boolean
  error: string | null
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const storedToken = localStorage.getItem("sentinel_token")
    const storedUser = localStorage.getItem("sentinel_user")
    if (storedToken && storedUser) {
      setToken(storedToken)
      setUser(JSON.parse(storedUser))
    }
    setLoading(false)
  }, [])

  const persistSession = useCallback((jwt: string, userData: User) => {
    setToken(jwt)
    setUser(userData)
    localStorage.setItem("sentinel_token", jwt)
    localStorage.setItem("sentinel_user", JSON.stringify(userData))
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true)
    setError(null)

    try {
      const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      })

      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail || `Login failed (${res.status})`)
      }

      const data = await res.json()
      persistSession(data.token, data.user)
    } catch (err) {
      const message = err instanceof Error ? err.message : "Login failed"
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [persistSession])

  const signup = useCallback(async (email: string, password: string, name: string) => {
    setLoading(true)
    setError(null)

    try {
      const res = await fetch(`${API_BASE_URL}/api/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, name }),
      })

      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail || `Signup failed (${res.status})`)
      }

      const data = await res.json()
      persistSession(data.token, data.user)
      return { apiKey: data.api_key }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Signup failed"
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [persistSession])

  const logout = useCallback(() => {
    setUser(null)
    setToken(null)
    localStorage.removeItem("sentinel_token")
    localStorage.removeItem("sentinel_user")
  }, [])

  return (
    <AuthContext.Provider value={{ user, token, login, signup, logout, loading, error }}>
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
