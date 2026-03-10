"use client"

import { AlertTriangle, CheckCircle, XCircle, Clock } from "lucide-react"
import { useEffect, useState } from "react"
import { apiService, type SecurityEvent } from "@/lib/api"

function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diffMs / 60_000)
  if (mins < 1) return "Just now"
  if (mins < 60) return `${mins} min ago`
  if (mins < 1440) return `${Math.floor(mins / 60)} hr ago`
  return `${Math.floor(mins / 1440)} days ago`
}

function SeverityIcon({ severity }: { severity: string }) {
  switch (severity) {
    case "CRITICAL":
      return <XCircle className="h-5 w-5 text-red-400" />
    case "HIGH":
      return <AlertTriangle className="h-5 w-5 text-orange-400" />
    case "MEDIUM":
      return <AlertTriangle className="h-5 w-5 text-yellow-400" />
    default:
      return <CheckCircle className="h-5 w-5 text-green-400" />
  }
}

export function RecentActivity() {
  const [events, setEvents] = useState<SecurityEvent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiService
      .getSecurityEvents(5)
      .then((data) => setEvents(data.events))
      .catch(() => setEvents([]))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="card-dark rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Recent Activity</h2>
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="flex items-start space-x-3 py-3">
              <div className="h-5 w-5 bg-gray-600 animate-pulse rounded-full" />
              <div className="flex-1 min-w-0">
                <div className="h-4 bg-gray-600 animate-pulse rounded mb-2" />
                <div className="h-3 bg-gray-700 animate-pulse rounded w-20" />
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="card-dark rounded-lg p-6">
      <h2 className="text-xl font-semibold text-white mb-4">Recent Activity</h2>
      <div className="space-y-0">
        {events.length > 0 ? (
          events.map((event) => (
            <div
              key={event.id}
              className="flex items-start space-x-3 py-3 border-b border-gray-800 last:border-b-0"
            >
              <SeverityIcon severity={event.severity} />
              <div className="flex-1 min-w-0">
                <p className="text-white text-sm">
                  {event.threat_type} detected in Agent &quot;{event.agent_id}&quot;
                </p>
                <p className="text-gray-400 text-xs mt-1">
                  {timeAgo(event.detected_at)} &middot; Confidence{" "}
                  {Math.round(event.confidence * 100)}%
                </p>
              </div>
              <span
                className={`text-xs px-2 py-0.5 rounded ${
                  event.severity === "CRITICAL"
                    ? "bg-red-900/30 text-red-400"
                    : event.severity === "HIGH"
                      ? "bg-orange-900/30 text-orange-400"
                      : event.severity === "MEDIUM"
                        ? "bg-yellow-900/30 text-yellow-400"
                        : "bg-green-900/30 text-green-400"
                }`}
              >
                {event.severity}
              </span>
            </div>
          ))
        ) : (
          <div className="text-center py-8">
            <Clock className="h-12 w-12 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-400">No recent activity</p>
            <p className="text-gray-500 text-sm mt-1">
              Security events will appear here when your SDK detects threats
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
