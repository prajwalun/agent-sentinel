"use client"

import { Clock, BarChart3, Shield, Activity } from "lucide-react"

interface PerformanceMetricsProps {
  metrics: {
    security_events_count?: number
    session_duration_seconds?: number
    total_function_calls?: number
    average_response_time_ms?: number
    success_rate?: number
    [key: string]: unknown
  }
}

export function PerformanceMetrics({ metrics }: PerformanceMetricsProps) {
  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`
    const minutes = Math.floor(seconds / 60)
    const remaining = seconds % 60
    return `${minutes}m ${remaining}s`
  }

  const items = [
    {
      title: "Events Detected",
      value: metrics.security_events_count ?? 0,
      icon: Shield,
      color: "text-red-400",
    },
    {
      title: "Session Duration",
      value: formatDuration(metrics.session_duration_seconds ?? 0),
      icon: Clock,
      color: "text-blue-400",
    },
    {
      title: "Function Calls",
      value: metrics.total_function_calls ?? "—",
      icon: Activity,
      color: "text-orange-400",
    },
    {
      title: "Success Rate",
      value:
        metrics.success_rate != null ? `${metrics.success_rate}%` : "—",
      icon: BarChart3,
      color: "text-green-400",
    },
  ]

  return (
    <div className="card-dark rounded-lg p-6">
      <h2 className="text-xl font-semibold text-white mb-4">
        Performance Metrics
      </h2>
      <div className="space-y-4">
        {items.map((item, index) => (
          <div
            key={index}
            className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0"
          >
            <div className="flex items-center gap-3">
              <item.icon className={`h-4 w-4 ${item.color}`} />
              <span className="text-gray-400 text-sm">{item.title}</span>
            </div>
            <span className="text-white font-semibold">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
