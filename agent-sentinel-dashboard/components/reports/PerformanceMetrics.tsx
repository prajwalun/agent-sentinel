"use client"

import { Clock, MemoryStickIcon as Memory, Cpu, TrendingUp } from "lucide-react"
import type { PerformanceMetrics as PerformanceMetricsType } from "@/types/report"

interface PerformanceMetricsProps {
  metrics: PerformanceMetricsType
}

export function PerformanceMetrics({ metrics }: PerformanceMetricsProps) {
  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}m ${remainingSeconds}s`
  }

  const metricCards = [
    {
      title: "Response Time",
      value: `${metrics.average_response_time_ms}ms`,
      icon: Clock,
      color: "text-blue-400",
    },
    {
      title: "Memory Usage",
      value: `${metrics.memory_usage_mb}MB`,
      icon: Memory,
      color: "text-purple-400",
    },
    {
      title: "CPU Usage",
      value: `${metrics.cpu_usage_percent}%`,
      icon: Cpu,
      color: "text-orange-400",
    },
    {
      title: "Success Rate",
      value: `${metrics.success_rate}%`,
      icon: TrendingUp,
      color: "text-green-400",
    },
  ]

  return (
    <div className="card-dark rounded-lg p-6">
      <h2 className="text-xl font-semibold text-white mb-6">Performance Metrics</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {metricCards.map((card, index) => (
          <div key={index} className="bg-black/50 rounded-lg p-4 border border-gray-800">
            <div className="flex items-center space-x-3 mb-2">
              <card.icon className={`h-5 w-5 ${card.color}`} />
              <span className="text-gray-400 text-sm">{card.title}</span>
            </div>
            <p className="text-2xl font-bold text-white">{card.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-black/50 rounded-lg p-4 border border-gray-800">
          <h3 className="text-white font-medium mb-2">Function Calls</h3>
          <p className="text-2xl font-bold text-white">{metrics.total_function_calls}</p>
          <p className="text-gray-400 text-sm">Total executed</p>
        </div>

        <div className="bg-black/50 rounded-lg p-4 border border-gray-800">
          <h3 className="text-white font-medium mb-2">Session Duration</h3>
          <p className="text-2xl font-bold text-white">{formatDuration(metrics.session_duration_seconds)}</p>
          <p className="text-gray-400 text-sm">Total runtime</p>
        </div>

        <div className="bg-black/50 rounded-lg p-4 border border-gray-800">
          <h3 className="text-white font-medium mb-2">Throughput</h3>
          <p className="text-2xl font-bold text-white">{metrics.throughput_requests_per_minute}</p>
          <p className="text-gray-400 text-sm">Requests/minute</p>
        </div>
      </div>
    </div>
  )
}
