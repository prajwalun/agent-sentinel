"use client"

import { useState } from "react"
import { AlertTriangle, Shield, Clock, CheckCircle, ChevronDown, ChevronRight } from "lucide-react"
import type { SecurityEvent } from "@/types/report"

interface SecurityEventsProps {
  events: SecurityEvent[]
}

function getSeverityIcon(severity: string) {
  switch (severity) {
    case "CRITICAL":
    case "HIGH":
      return <AlertTriangle className="h-5 w-5 text-red-400" />
    case "MEDIUM":
      return <AlertTriangle className="h-5 w-5 text-orange-400" />
    case "LOW":
      return <CheckCircle className="h-5 w-5 text-green-400" />
    default:
      return <Shield className="h-5 w-5 text-gray-400" />
  }
}

function getSeverityColor(severity: string) {
  switch (severity) {
    case "CRITICAL":
    case "HIGH":
      return "border-red-600 bg-red-900/20"
    case "MEDIUM":
      return "border-orange-600 bg-orange-900/20"
    case "LOW":
      return "border-green-600 bg-green-900/20"
    default:
      return "border-gray-600 bg-gray-900/20"
  }
}

function EventCard({ event }: { event: SecurityEvent }) {
  const [expanded, setExpanded] = useState(false)
  const hasDetails = event.details && Object.keys(event.details).length > 0

  return (
    <div className={`border rounded-lg p-4 ${getSeverityColor(event.severity)}`}>
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0 mt-1">{getSeverityIcon(event.severity)}</div>

        <div className="flex-1 min-w-0">
          {/* Header row */}
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <span className="text-white font-medium">{event.threat_type.replace(/_/g, " ")}</span>
              <span
                className={`px-2 py-0.5 rounded text-xs font-medium ${
                  event.severity === "CRITICAL" || event.severity === "HIGH"
                    ? "bg-red-600 text-white"
                    : event.severity === "MEDIUM"
                      ? "bg-orange-600 text-white"
                      : "bg-green-600 text-white"
                }`}
              >
                {event.severity}
              </span>
            </div>
            <div className="flex items-center space-x-2 text-gray-400 text-sm">
              <Clock className="h-4 w-4" />
              <span>{new Date(event.timestamp).toLocaleString()}</span>
            </div>
          </div>

          {/* Message */}
          <p className="text-gray-300 mb-2 text-sm">{event.message}</p>

          {/* Footer row */}
          <div className="flex items-center justify-between">
            <span className="text-gray-400 text-sm">
              Confidence: {Math.round(event.confidence * 100)}%
            </span>
            {hasDetails && (
              <button
                onClick={() => setExpanded((v) => !v)}
                className="flex items-center gap-1 text-red-400 hover:text-red-300 text-sm transition-colors"
              >
                {expanded ? (
                  <>
                    <ChevronDown className="h-4 w-4" />
                    Hide Details
                  </>
                ) : (
                  <>
                    <ChevronRight className="h-4 w-4" />
                    View Details
                  </>
                )}
              </button>
            )}
          </div>

          {/* Expandable details */}
          {expanded && hasDetails && (
            <div className="mt-3 pt-3 border-t border-gray-700">
              <p className="text-gray-400 text-xs font-medium uppercase mb-2">
                Event Context
              </p>
              <div className="space-y-1">
                {Object.entries(event.details).map(([key, value]) => (
                  <div key={key} className="flex items-start gap-2 text-sm">
                    <span className="text-gray-500 min-w-24 capitalize">
                      {key.replace(/_/g, " ")}:
                    </span>
                    <span className="text-gray-300 break-all">
                      {typeof value === "object"
                        ? JSON.stringify(value, null, 2)
                        : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export function SecurityEvents({ events }: SecurityEventsProps) {
  if (!events || events.length === 0) {
    return (
      <div className="card-dark rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Security Events</h2>
        <div className="text-center py-6 text-gray-500">
          <Shield className="h-10 w-10 mx-auto mb-2 text-gray-700" />
          No security events recorded.
        </div>
      </div>
    )
  }

  return (
    <div className="card-dark rounded-lg p-6">
      <h2 className="text-xl font-semibold text-white mb-4">
        Security Events
        <span className="ml-2 text-sm font-normal text-gray-500">
          ({events.length})
        </span>
      </h2>
      <div className="space-y-4">
        {events.map((event) => (
          <EventCard key={event.id} event={event} />
        ))}
      </div>
    </div>
  )
}
