"use client"

import { Shield, AlertTriangle, CheckCircle, XCircle } from "lucide-react"
import type { ReportSummary } from "@/types/report"

interface ExecutiveSummaryProps {
  summary: ReportSummary
}

export function ExecutiveSummary({ summary }: ExecutiveSummaryProps) {
  const getStatusIcon = () => {
    switch (summary.status) {
      case "CLEAN":
        return <CheckCircle className="h-8 w-8 text-green-400" />
      case "WARNING":
        return <AlertTriangle className="h-8 w-8 text-orange-400" />
      case "CRITICAL":
        return <XCircle className="h-8 w-8 text-red-400" />
      default:
        return <Shield className="h-8 w-8 text-gray-400" />
    }
  }

  const getStatusColor = () => {
    switch (summary.status) {
      case "CLEAN":
        return "text-green-400"
      case "WARNING":
        return "text-orange-400"
      case "CRITICAL":
        return "text-red-400"
      default:
        return "text-gray-400"
    }
  }

  const getRiskScoreColor = () => {
    if (summary.risk_score < 20) return "bg-green-600"
    if (summary.risk_score < 50) return "bg-orange-600"
    return "bg-red-600"
  }

  return (
    <div className="card-dark rounded-lg p-6">
      <h2 className="text-xl font-semibold text-white mb-6">Executive Summary</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Status and Risk Score */}
        <div className="space-y-6">
          <div className="flex items-center space-x-4">
            {getStatusIcon()}
            <div>
              <h3 className="text-lg font-semibold text-white">Overall Status</h3>
              <p className={`text-2xl font-bold ${getStatusColor()}`}>{summary.status}</p>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-white font-medium">Risk Score</span>
              <span className="text-white font-bold">{summary.risk_score}/100</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-3">
              <div className={`h-3 rounded-full ${getRiskScoreColor()}`} style={{ width: `${summary.risk_score}%` }} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-red-400">{summary.threats_detected}</p>
              <p className="text-gray-400 text-sm">Threats Detected</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-400">{summary.performance_score}%</p>
              <p className="text-gray-400 text-sm">Performance Score</p>
            </div>
          </div>
        </div>

        {/* Key Insights */}
        <div>
          <h3 className="text-lg font-semibold text-white mb-4">Key Insights</h3>
          <ul className="space-y-2">
            {summary.key_insights.map((insight, index) => (
              <li key={index} className="flex items-start space-x-2">
                <div className="w-2 h-2 bg-red-600 rounded-full mt-2 flex-shrink-0" />
                <span className="text-gray-300 text-sm">{insight}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
