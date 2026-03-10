"use client"

import { useEffect, useState } from "react"
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts"
import { apiService, type DashboardStats } from "@/lib/api"

const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: "#ef4444",
  HIGH: "#f97316",
  MEDIUM: "#eab308",
  LOW: "#22c55e",
}

export function SeverityChart() {
  const [stats, setStats] = useState<DashboardStats | null>(null)

  useEffect(() => {
    apiService
      .getDashboardStats()
      .then(setStats)
      .catch(() => {})
  }, [])

  if (!stats || !stats.severity_counts) return null

  const data = Object.entries(stats.severity_counts)
    .filter(([, count]) => count > 0)
    .map(([severity, count]) => ({
      name: severity,
      value: count,
    }))

  if (data.length === 0) {
    return (
      <div className="card-dark rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">
          Severity Distribution
        </h2>
        <div className="flex items-center justify-center h-48 text-gray-500 text-sm">
          No events yet — severity data will appear here
        </div>
      </div>
    )
  }

  return (
    <div className="card-dark rounded-lg p-6">
      <h2 className="text-xl font-semibold text-white mb-4">
        Severity Distribution
      </h2>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={50}
            outerRadius={80}
            paddingAngle={3}
            dataKey="value"
            stroke="none"
          >
            {data.map((entry) => (
              <Cell
                key={entry.name}
                fill={SEVERITY_COLORS[entry.name] || "#6b7280"}
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: "#1a1a1a",
              border: "1px solid #2d2d2d",
              borderRadius: "8px",
              color: "#fff",
            }}
          />
          <Legend
            wrapperStyle={{ color: "#9ca3af", fontSize: "12px" }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
