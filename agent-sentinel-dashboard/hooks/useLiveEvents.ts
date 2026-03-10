"use client"

import { useEffect, useRef, useState, useCallback } from "react"
import type { SecurityEvent } from "@/lib/api"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"

/**
 * SSE hook that subscribes to /api/events/stream.
 * Pushes new SecurityEvent objects into state as they arrive.
 * Automatically reconnects on disconnection.
 */
export function useLiveEvents(maxBuffer = 50) {
  const [events, setEvents] = useState<SecurityEvent[]>([])
  const [connected, setConnected] = useState(false)
  const sourceRef = useRef<EventSource | null>(null)

  const connect = useCallback(() => {
    if (sourceRef.current) {
      sourceRef.current.close()
    }

    const token = typeof window !== "undefined"
      ? localStorage.getItem("sentinel_token")
      : null
    if (!token) return

    const es = new EventSource(
      `${API_BASE_URL}/api/events/stream?token=${encodeURIComponent(token)}`
    )
    sourceRef.current = es

    es.onopen = () => setConnected(true)

    es.onmessage = (msg) => {
      try {
        const event: SecurityEvent = JSON.parse(msg.data)
        setEvents((prev) => [event, ...prev].slice(0, maxBuffer))
      } catch {
        // Heartbeat or malformed — ignore
      }
    }

    es.onerror = () => {
      setConnected(false)
      es.close()
      setTimeout(connect, 5000)
    }
  }, [maxBuffer])

  useEffect(() => {
    connect()
    return () => {
      sourceRef.current?.close()
    }
  }, [connect])

  return { events, connected }
}
