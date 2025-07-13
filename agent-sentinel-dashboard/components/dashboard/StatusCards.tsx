"use client"
import { TrendingUp, TrendingDown, Minus } from "lucide-react"

interface StatusCardProps {
  title: string
  value: string | number
  trend?: {
    direction: "up" | "down" | "stable"
    value: string
    period: string
  }
  status?: "clean" | "warning" | "critical"
}

function StatusCard({ title, value, trend, status = "clean" }: StatusCardProps) {
  const getStatusColor = () => {
    switch (status) {
      case "clean":
        return "text-green-400"
      case "warning":
        return "text-orange-400"
      case "critical":
        return "text-red-400"
      default:
        return "text-white"
    }
  }

  const getTrendIcon = () => {
    if (!trend) return null
    switch (trend.direction) {
      case "up":
        return <TrendingUp className="h-4 w-4" />
      case "down":
        return <TrendingDown className="h-4 w-4" />
      case "stable":
        return <Minus className="h-4 w-4" />
    }
  }

  const getTrendColor = () => {
    if (!trend) return ""
    switch (trend.direction) {
      case "up":
        return status === "critical" ? "text-red-400" : "text-green-400"
      case "down":
        return status === "critical" ? "text-green-400" : "text-red-400"
      case "stable":
        return "text-gray-400"
    }
  }

  return (
    <div className="card-dark rounded-lg p-6">
      <h3 className="text-gray-400 text-sm font-medium mb-2">{title}</h3>
      <div className="flex items-center justify-between">
        <span className={`text-3xl font-bold ${getStatusColor()}`}>{value}</span>
        {trend && (
          <div className={`flex items-center space-x-1 text-sm ${getTrendColor()}`}>
            {getTrendIcon()}
            <span>{trend.value}</span>
            <span className="text-gray-500">{trend.period}</span>
          </div>
        )}
      </div>
    </div>
  )
}

export function StatusCards() {
  // Mock data - no database needed
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <StatusCard
        title="Total Agents"
        value={12}
        trend={{ direction: "up", value: "+2", period: "today" }}
        status="clean"
      />
      <StatusCard
        title="Active Agents"
        value={8}
        trend={{ direction: "up", value: "+1", period: "today" }}
        status="clean"
      />
      <StatusCard
        title="Threats Detected"
        value={3}
        trend={{ direction: "up", value: "+1", period: "today" }}
        status="critical"
      />
      <StatusCard
        title="Performance Score"
        value="95.2%"
        trend={{ direction: "up", value: "+2.1%", period: "today" }}
        status="clean"
      />
    </div>
  )
}
