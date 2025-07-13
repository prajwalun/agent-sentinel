"use client"

import { AlertTriangle, Shield, Clock, CheckCircle } from "lucide-react"
import type { SecurityEvent } from "@/types/report"

interface SecurityEventsProps {
  events: SecurityEvent[]
}

export function SecurityEvents({ events }: SecurityEventsProps) {
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "CRITICAL":
        return <AlertTriangle className="h-5 w-5 text-red-400" />
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

  const getSeverityColor = (severity: string) => {
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

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString()
  }

  return (
    <div className="card-dark rounded-lg p-6">
      <h2 className="text-xl font-semibold text-white mb-6">Security Events</h2>

      <div className="space-y-4">
        {events.map((event) => (
          <div key={event.id} className={`border rounded-lg p-4 ${getSeverityColor(event.severity)}`}>
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 mt-1">{getSeverityIcon(event.severity)}</div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-white font-medium">{event.threat_type}</span>
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${
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
                    <span>{formatTimestamp(event.timestamp)}</span>
                  </div>
                </div>

                <p className="text-gray-300 mb-2">{event.message}</p>

                <div className="flex items-center justify-between">
                  <span className="text-gray-400 text-sm">Confidence: {Math.round(event.confidence * 100)}%</span>
                  {event.details && <button className="text-red-400 hover:text-red-300 text-sm">View Details →</button>}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
